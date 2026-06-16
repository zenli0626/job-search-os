#!/usr/bin/env python3
"""
job-sweep.py — Daily ATS Job Board Sweep

Sweeps Greenhouse, Ashby, and Lever ATS boards in parallel.
Filters by lane inclusion, exclusion keywords, seniority level, and location.
Persists results to SQLite and prints only NET-NEW jobs (not seen in previous runs).

Usage:
    python3 job-sweep.py
    python3 job-sweep.py --config config.json --db sweep.sqlite --output job-targets-raw.json

Requirements: Python 3.8+ stdlib only (no pip install needed).
"""

import argparse
import json
import re
import sqlite3
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import URLError, HTTPError
from urllib.request import urlopen, Request


# ──────────────────────────────────────────────────────────────────────────────
# Database
# ──────────────────────────────────────────────────────────────────────────────

def init_db(db_path: str) -> sqlite3.Connection:
    """Open (or create) the sweep SQLite database and ensure the schema exists."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            url        TEXT PRIMARY KEY,
            title      TEXT NOT NULL,
            company    TEXT NOT NULL,
            lanes      TEXT NOT NULL DEFAULT '',
            location   TEXT NOT NULL DEFAULT '',
            first_seen TEXT NOT NULL,
            status     TEXT NOT NULL DEFAULT 'SEEN'
        )
    """)
    conn.commit()
    return conn


def is_new(conn: sqlite3.Connection, url: str) -> bool:
    """Return True if this URL has not been seen in a previous sweep."""
    row = conn.execute("SELECT 1 FROM jobs WHERE url = ?", (url,)).fetchone()
    return row is None


def insert_job(conn: sqlite3.Connection, job: dict) -> None:
    """Insert a new job row. Silently ignores duplicates (URL conflict)."""
    conn.execute(
        """
        INSERT OR IGNORE INTO jobs (url, title, company, lanes, location, first_seen, status)
        VALUES (?, ?, ?, ?, ?, ?, 'SEEN')
        """,
        (
            job["url"],
            job["title"],
            job["company"],
            ",".join(job.get("lanes", [])),
            job.get("location", ""),
            job.get("first_seen", datetime.now(timezone.utc).isoformat()),
        ),
    )


# ──────────────────────────────────────────────────────────────────────────────
# HTTP helper
# ──────────────────────────────────────────────────────────────────────────────

def fetch_json(url: str, timeout: int = 15) -> object:
    """
    Fetch a URL and parse the response as JSON.
    Returns None on any network or parsing error.
    """
    try:
        req = Request(url, headers={"User-Agent": "JobSearchOS/1.0"})
        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            return json.loads(raw)
    except HTTPError as e:
        print(f"  [HTTP {e.code}] {url}", file=sys.stderr)
        return None
    except URLError as e:
        print(f"  [URLError] {url}: {e.reason}", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"  [JSON parse error] {url}: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  [Error] {url}: {e}", file=sys.stderr)
        return None


# ──────────────────────────────────────────────────────────────────────────────
# ATS fetchers
# ──────────────────────────────────────────────────────────────────────────────

def fetch_greenhouse(slug: str) -> list[dict]:
    """
    Fetch jobs from Greenhouse.
    API: GET https://boards-api.greenhouse.io/v1/boards/{slug}/jobs
    Returns a list of normalized job dicts.
    """
    url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
    data = fetch_json(url)
    if not data or "jobs" not in data:
        return []

    jobs = []
    for job in data.get("jobs", []):
        title = job.get("title", "")
        absolute_url = job.get("absolute_url", "")
        location_obj = job.get("location", {})
        location = location_obj.get("name", "") if isinstance(location_obj, dict) else str(location_obj)
        if title and absolute_url:
            jobs.append({
                "title": title,
                "url": absolute_url,
                "location": location,
                "company": slug,
                "ats": "greenhouse",
            })
    return jobs


def fetch_ashby(slug: str) -> list[dict]:
    """
    Fetch jobs from Ashby.
    API: GET https://api.ashbyhq.com/posting-api/job-board/{slug}
    Returns a list of normalized job dicts.
    """
    url = f"https://api.ashbyhq.com/posting-api/job-board/{slug}"
    data = fetch_json(url)
    if not data:
        return []

    # Ashby wraps results under 'results' or returns a list at top level
    postings = data.get("results", data) if isinstance(data, dict) else data
    if not isinstance(postings, list):
        return []

    jobs = []
    for posting in postings:
        title = posting.get("title", "")
        job_url = posting.get("jobUrl", posting.get("url", ""))
        location = posting.get("locationName", posting.get("location", ""))
        if title and job_url:
            jobs.append({
                "title": title,
                "url": job_url,
                "location": location,
                "company": slug,
                "ats": "ashby",
            })
    return jobs


def fetch_lever(slug: str) -> list[dict]:
    """
    Fetch jobs from Lever.
    API: GET https://api.lever.co/v0/postings/{slug}
    Returns a list of normalized job dicts.
    """
    url = f"https://api.lever.co/v0/postings/{slug}"
    data = fetch_json(url)
    if not isinstance(data, list):
        return []

    jobs = []
    for posting in data:
        title = posting.get("text", "")
        job_url = posting.get("hostedUrl", posting.get("applyUrl", ""))
        # Lever location is nested under 'categories'
        categories = posting.get("categories", {})
        location = categories.get("location", "") if isinstance(categories, dict) else ""
        if title and job_url:
            jobs.append({
                "title": title,
                "url": job_url,
                "location": location,
                "company": slug,
                "ats": "lever",
            })
    return jobs


# ──────────────────────────────────────────────────────────────────────────────
# Filtering
# ──────────────────────────────────────────────────────────────────────────────

def compile_patterns(config: dict) -> dict:
    """
    Pre-compile all regex patterns from config for reuse across postings.
    Returns a dict of compiled patterns.
    """
    flags = re.IGNORECASE

    # Lane patterns: dict of {lane_name: compiled_regex}
    lane_patterns = {}
    for lane_name, pattern in config.get("lanes", {}).items():
        lane_patterns[lane_name] = re.compile(pattern, flags)

    # Global exclusion pattern (single pipe-delimited string)
    exclude_pattern = config.get("exclude", "")
    exclude_re = re.compile(exclude_pattern, flags) if exclude_pattern else None

    # Seniority level pattern
    levels_pattern = config.get("levels", "")
    levels_re = re.compile(levels_pattern, flags) if levels_pattern else None

    # Location exclusion list (exact substring match, case-insensitive)
    exclude_locations = [loc.lower() for loc in config.get("exclude_locations", [])]

    return {
        "lanes": lane_patterns,
        "exclude": exclude_re,
        "levels": levels_re,
        "exclude_locations": exclude_locations,
    }


def is_international_only(location: str, exclude_locations: list[str]) -> bool:
    """
    Return True if the location string matches any excluded international location.
    Allows through: US states/cities, Remote, empty/unknown locations.
    """
    if not location:
        return False  # unknown location → let it through
    loc_lower = location.lower()
    # Check for explicit exclusions
    for ex in exclude_locations:
        if ex in loc_lower:
            return True
    return False


def filter_posting(job: dict, patterns: dict) -> dict | None:
    """
    Apply all filters to a posting. Returns the job dict (augmented with matched lanes)
    if it passes all filters, or None if it should be excluded.
    """
    title = job.get("title", "")
    location = job.get("location", "")

    # 1. Global exclusion check
    if patterns["exclude"] and patterns["exclude"].search(title):
        return None

    # 2. Seniority gate
    if patterns["levels"] and not patterns["levels"].search(title):
        return None

    # 3. Location filter
    if is_international_only(location, patterns["exclude_locations"]):
        return None

    # 4. Lane inclusion check — must match at least one lane
    matched_lanes = [
        lane_name
        for lane_name, lane_re in patterns["lanes"].items()
        if lane_re.search(title)
    ]
    if not matched_lanes:
        return None

    return {**job, "lanes": matched_lanes}


# ──────────────────────────────────────────────────────────────────────────────
# Parallel sweep
# ──────────────────────────────────────────────────────────────────────────────

def sweep_company(ats: str, slug: str) -> tuple[str, list[dict]]:
    """
    Fetch and return raw postings for one company.
    Returns (slug, list_of_raw_jobs).
    """
    fetchers = {
        "greenhouse": fetch_greenhouse,
        "ashby": fetch_ashby,
        "lever": fetch_lever,
    }
    fetcher = fetchers.get(ats)
    if not fetcher:
        print(f"  [Unknown ATS] {ats}", file=sys.stderr)
        return slug, []
    return slug, fetcher(slug)


def run_sweep(config: dict) -> list[dict]:
    """
    Run parallel sweeps across all configured companies.
    Returns a deduplicated list of filtered job dicts.
    """
    # Build a flat list of (ats, slug) tasks
    tasks = []
    for ats in ("greenhouse", "ashby", "lever"):
        for slug in config.get(ats, []):
            tasks.append((ats, slug))

    if not tasks:
        print("[sweep] No companies configured. Edit config.json to add ATS slugs.",
              file=sys.stderr)
        return []

    patterns = compile_patterns(config)

    # Fetch in parallel
    all_jobs = []
    seen_urls = set()

    max_workers = min(len(tasks), 20)  # cap threads
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(sweep_company, ats, slug): (ats, slug)
            for ats, slug in tasks
        }
        for future in as_completed(futures):
            ats, slug = futures[future]
            try:
                _, raw_jobs = future.result()
                for job in raw_jobs:
                    # Apply filters
                    filtered = filter_posting(job, patterns)
                    if filtered is None:
                        continue
                    # Dedup by URL within this run
                    url = filtered.get("url", "")
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        filtered["first_seen"] = datetime.now(timezone.utc).isoformat()
                        all_jobs.append(filtered)
            except Exception as e:
                print(f"  [Error] {ats}/{slug}: {e}", file=sys.stderr)

    return all_jobs


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Job Search OS — Daily ATS sweep (Greenhouse / Ashby / Lever)"
    )
    parser.add_argument(
        "--config",
        default=str(Path(__file__).parent / "config.json"),
        help="Path to config JSON file (default: config.json in same directory)",
    )
    parser.add_argument(
        "--db",
        default=str(Path(__file__).parent / "sweep.sqlite"),
        help="Path to SQLite persistence file (default: sweep.sqlite in same directory)",
    )
    parser.add_argument(
        "--output",
        default=str(Path(__file__).parent / "job-targets-raw.json"),
        help="Path to write full results JSON (default: job-targets-raw.json in same directory)",
    )
    args = parser.parse_args()

    # Load config
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"[sweep] Config not found: {config_path}", file=sys.stderr)
        print("[sweep] Copy config.example.json to config.json and customize it.", file=sys.stderr)
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # Initialize database
    conn = init_db(args.db)

    print(f"[sweep] Starting sweep — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Run parallel sweep
    all_jobs = run_sweep(config)

    print(f"[sweep] Found {len(all_jobs)} matching postings after filtering.")

    # Identify net-new jobs and persist
    new_jobs = []
    for job in all_jobs:
        if is_new(conn, job["url"]):
            new_jobs.append(job)
            insert_job(conn, job)

    conn.commit()
    conn.close()

    # Write full results to JSON (for Stage 02 review queue)
    output_path = Path(args.output)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_jobs, f, indent=2)

    # Print only net-new jobs to stdout
    print(f"\n{'─' * 60}")
    print(f"  NET-NEW JOBS: {len(new_jobs)} (not seen in previous sweeps)")
    print(f"{'─' * 60}\n")

    if not new_jobs:
        print("  No new jobs since last run.")
    else:
        for i, job in enumerate(new_jobs, 1):
            lanes_str = ", ".join(job.get("lanes", []))
            loc = job.get("location", "")
            print(f"  {i}. [{lanes_str}] {job['title']}")
            print(f"     Company: {job['company']} ({job['ats']})")
            if loc:
                print(f"     Location: {loc}")
            print(f"     {job['url']}")
            print()

    print(f"[sweep] Full results: {output_path}")
    print(f"[sweep] Database: {args.db}")


if __name__ == "__main__":
    main()
