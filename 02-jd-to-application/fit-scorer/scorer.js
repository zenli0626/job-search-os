/**
 * scorer.js — JD Fit Scorer
 *
 * Pure CommonJS module. No personal data. No external dependencies.
 *
 * Usage:
 *   const { scoreJD } = require('./scorer');
 *   const rubric = require('./rubric.example.json');
 *   const result = scoreJD(jdText, rubric);
 *
 * Returns: { score, verdict, matchedStrengths, gapPenalties, dealbreakersTriggered, pitchAngle, evidence }
 */

'use strict';

/**
 * Normalize text for matching: lowercase, collapse whitespace.
 * @param {string} text
 * @returns {string}
 */
function normalizeText(text) {
  if (typeof text !== 'string') return '';
  return text.toLowerCase().replace(/\s+/g, ' ').trim();
}

/**
 * Count how many triggers appear in normalizedText.
 * Each trigger is matched as a substring. Deduplicates so the same trigger
 * doesn't score multiple times if it appears many times.
 *
 * @param {string} normalizedText
 * @param {string[]} triggers
 * @returns {{ count: number, matched: string[] }}
 */
function countTriggerHits(normalizedText, triggers) {
  const matched = [];
  for (const trigger of triggers) {
    const t = trigger.toLowerCase();
    if (normalizedText.includes(t) && !matched.includes(t)) {
      matched.push(t);
    }
  }
  return { count: matched.length, matched };
}

/**
 * Determine whether a trigger appears near a "must"/"required" signal
 * or a "preferred"/"nice to have" signal in the surrounding sentence.
 *
 * Returns 'hard' | 'soft' | 'neutral'
 *
 * @param {string} normalizedText  Full normalized JD text
 * @param {string} trigger         The trigger word/phrase to locate
 * @returns {'hard'|'soft'|'neutral'}
 */
function detectRequirementStrength(normalizedText, trigger) {
  const t = trigger.toLowerCase();
  const idx = normalizedText.indexOf(t);
  if (idx === -1) return 'neutral';

  // Look at a 120-char window around the trigger
  const windowStart = Math.max(0, idx - 120);
  const windowEnd = Math.min(normalizedText.length, idx + 120);
  const window = normalizedText.slice(windowStart, windowEnd);

  const hardPatterns = ['must', 'required', 'requirement', 'mandatory', 'you have', 'you will have'];
  const softPatterns = ['preferred', 'nice to have', 'ideal', 'bonus', 'plus', 'desirable', 'a plus'];

  for (const p of hardPatterns) {
    if (window.includes(p)) return 'hard';
  }
  for (const p of softPatterns) {
    if (window.includes(p)) return 'soft';
  }
  return 'neutral';
}

/**
 * Score the strength buckets.
 *
 * For each bucket:
 * - Count trigger hits (capped at bucket.triggers.length to prevent gaming)
 * - Normalize hit rate to 0–100
 * - Apply bucket weight
 *
 * Returns the weighted contribution (0–100 scale, proportional to weight sum).
 *
 * @param {string} normalizedText
 * @param {Array<{name: string, weight: number, triggers: string[], pitchLine: string}>} strengthBuckets
 * @returns {{ weightedScore: number, matchedStrengths: Array<{name: string, triggers: string[], pitchLine: string, rawScore: number}> }}
 */
function scoreStrengths(normalizedText, strengthBuckets) {
  let totalWeightedScore = 0;
  let totalWeight = 0;
  const matchedStrengths = [];

  for (const bucket of strengthBuckets) {
    const weight = bucket.weight || 0;
    const triggers = Array.isArray(bucket.triggers) ? bucket.triggers : [];
    if (triggers.length === 0) continue;

    const { count, matched } = countTriggerHits(normalizedText, triggers);
    // Cap at total triggers to normalize
    const hitRate = Math.min(count, triggers.length) / triggers.length;
    const rawScore = Math.round(hitRate * 100);

    totalWeightedScore += rawScore * weight;
    totalWeight += weight;

    if (count > 0) {
      matchedStrengths.push({
        name: bucket.name,
        triggers: matched,
        pitchLine: bucket.pitchLine || '',
        rawScore
      });
    }
  }

  // Normalize by total weight so result is still 0–100
  const weightedScore = totalWeight > 0 ? totalWeightedScore / totalWeight : 0;
  return { weightedScore, matchedStrengths };
}

/**
 * Score gap penalties.
 *
 * For each gap bucket:
 * - Count trigger hits
 * - Detect requirement strength (hard vs. soft)
 * - Hard gaps carry full penalty weight; soft gaps carry half
 *
 * Returns a total penalty value on the 0–100 scale.
 *
 * @param {string} normalizedText
 * @param {Array<{name: string, weight: number, triggers: string[], framingLine: string}>} gapBuckets
 * @returns {{ totalPenalty: number, gapPenalties: Array<{name: string, triggers: string[], strength: string, penaltyWeight: number, framingLine: string}> }}
 */
function scoreGaps(normalizedText, gapBuckets) {
  let totalPenalty = 0;
  const gapPenalties = [];

  for (const bucket of gapBuckets) {
    const weight = bucket.weight || 0;
    const triggers = Array.isArray(bucket.triggers) ? bucket.triggers : [];
    if (triggers.length === 0) continue;

    const { count, matched } = countTriggerHits(normalizedText, triggers);
    if (count === 0) continue;

    // Detect the strongest requirement signal across all matched triggers
    let strength = 'neutral';
    for (const t of matched) {
      const s = detectRequirementStrength(normalizedText, t);
      if (s === 'hard') { strength = 'hard'; break; }
      if (s === 'soft') strength = 'soft';
    }

    // Hard gaps apply full weight penalty; soft gaps apply half
    const penaltyMultiplier = strength === 'hard' ? 1.0 : strength === 'soft' ? 0.5 : 0.75;
    const penaltyWeight = weight * penaltyMultiplier;

    totalPenalty += penaltyWeight * 100; // penalty is weighted contribution
    gapPenalties.push({
      name: bucket.name,
      triggers: matched,
      strength,
      penaltyWeight,
      framingLine: bucket.framingLine || ''
    });
  }

  return { totalPenalty, gapPenalties };
}

/**
 * Check dealbreakers.
 *
 * If any dealbreaker's triggers match, the role is automatically capped at 29 (SKIP).
 *
 * @param {string} normalizedText
 * @param {Array<{name: string, triggers: string[]}>} dealbreakers
 * @returns {{ triggered: boolean, dealbreakersTriggered: Array<{name: string, triggers: string[]}> }}
 */
function checkDealbreakers(normalizedText, dealbreakers) {
  const dealbreakersTriggered = [];

  for (const db of dealbreakers) {
    const triggers = Array.isArray(db.triggers) ? db.triggers : [];
    const { count, matched } = countTriggerHits(normalizedText, triggers);
    if (count > 0) {
      dealbreakersTriggered.push({ name: db.name, triggers: matched });
    }
  }

  return { triggered: dealbreakersTriggered.length > 0, dealbreakersTriggered };
}

/**
 * Map a numeric score to a verdict string using the rubric's band definitions.
 *
 * @param {number} score
 * @param {Array<{min: number, max: number, verdict: string}>} bands
 * @returns {string}
 */
function mapVerdict(score, bands) {
  for (const band of bands) {
    if (score >= band.min && score <= band.max) {
      return band.verdict;
    }
  }
  // Fallback
  if (score >= 70) return 'APPLY';
  if (score >= 45) return 'STRETCH';
  return 'SKIP';
}

/**
 * Select the best pitch angle from matched strength buckets.
 * Returns the pitchLine of the highest-scoring strength bucket.
 *
 * @param {Array<{name: string, rawScore: number, pitchLine: string}>} matchedStrengths
 * @returns {string}
 */
function selectPitchAngle(matchedStrengths) {
  if (!matchedStrengths || matchedStrengths.length === 0) return '';
  const sorted = [...matchedStrengths].sort((a, b) => b.rawScore - a.rawScore);
  return sorted[0].pitchLine || sorted[0].name;
}

/**
 * Main scoring function.
 *
 * @param {string} jdText   Raw job description text (any case, any format)
 * @param {object} rubric   Rubric object matching rubric.example.json schema
 * @returns {{
 *   score: number,
 *   verdict: string,
 *   matchedStrengths: Array,
 *   gapPenalties: Array,
 *   dealbreakersTriggered: Array,
 *   pitchAngle: string,
 *   evidence: string
 * }}
 */
function scoreJD(jdText, rubric) {
  if (!jdText || typeof jdText !== 'string') {
    throw new Error('scoreJD: jdText must be a non-empty string');
  }
  if (!rubric || typeof rubric !== 'object') {
    throw new Error('scoreJD: rubric must be an object');
  }

  const normalizedText = normalizeText(jdText);

  // 1. Check dealbreakers first — if triggered, cap and return early
  const { triggered, dealbreakersTriggered } = checkDealbreakers(
    normalizedText,
    rubric.dealbreakers || []
  );

  if (triggered) {
    const bands = (rubric.scoringSpec && rubric.scoringSpec.bands) ? rubric.scoringSpec.bands : [];
    return {
      score: 29,
      verdict: 'SKIP',
      matchedStrengths: [],
      gapPenalties: [],
      dealbreakersTriggered,
      pitchAngle: '',
      evidence: `Dealbreaker(s) triggered: ${dealbreakersTriggered.map(d => d.name).join(', ')}`
    };
  }

  // 2. Score strengths
  const { weightedScore, matchedStrengths } = scoreStrengths(
    normalizedText,
    rubric.strengthBuckets || []
  );

  // 3. Score gap penalties
  const { totalPenalty, gapPenalties } = scoreGaps(
    normalizedText,
    rubric.gapBuckets || []
  );

  // 4. Compute final score
  // Gap penalty is expressed as a deduction from the base strength score
  // Penalty is capped so it can't make the score go negative
  const penaltyDeduction = Math.min(weightedScore, totalPenalty);
  const rawFinalScore = weightedScore - penaltyDeduction;
  const score = Math.max(0, Math.min(100, Math.round(rawFinalScore)));

  // 5. Map to verdict
  const bands = (rubric.scoringSpec && rubric.scoringSpec.bands) ? rubric.scoringSpec.bands : [];
  const verdict = mapVerdict(score, bands);

  // 6. Pitch angle
  const pitchAngle = selectPitchAngle(matchedStrengths);

  // 7. Evidence summary
  const strengthSummary = matchedStrengths.length > 0
    ? `Strengths: ${matchedStrengths.map(s => `${s.name} (${s.rawScore}%)`).join(', ')}`
    : 'No significant strength matches found';

  const gapSummary = gapPenalties.length > 0
    ? `Gap penalties: ${gapPenalties.map(g => `${g.name} [${g.strength}]`).join(', ')}`
    : 'No significant gap penalties';

  const evidence = [strengthSummary, gapSummary].join(' | ');

  return {
    score,
    verdict,
    matchedStrengths,
    gapPenalties,
    dealbreakersTriggered,
    pitchAngle,
    evidence
  };
}

module.exports = { scoreJD, normalizeText, countTriggerHits, detectRequirementStrength };
