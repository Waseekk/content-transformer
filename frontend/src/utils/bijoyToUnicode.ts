/**
 * Bijoy (SutonnyMJ) to Unicode Bengali conversion utility
 *
 * The SutonnyMJ font maps ASCII/Windows-1252 bytes to Bengali glyphs.
 * When Bijoy text is pasted into a Unicode textarea, it arrives as
 * garbled ASCII/Latin characters. This module detects and converts it.
 *
 * Mapping source: bahar/BijoyToUnicode (PHP) and Mad-FOX/bijoy2unicode (Python)
 *
 * Pipeline:
 *   preConversion → charMap → reorderPreKars → reorderReph → postConversion
 */

import { countBengaliChars } from './languageDetection';

// ─── Stage 1: Pre-conversion string fixes ────────────────────────────────────

const PRE_CONVERSION: [string, string][] = [
  ['yy', 'y'],
  ['vv', 'v'],
  ['\u00AD\u00AD', '\u00AD'],
];

// ─── Stage 2: Main character map ─────────────────────────────────────────────
// IMPORTANT: Multi-char sequences MUST come before their single-char components.
// Uses Array<[from, to]> to preserve insertion order.

const CHAR_MAP: [string, string][] = [
  // ── Multi-char: standalone আ (must precede 'A' and 'v' entries) ──
  ['Av', 'আ'],   // অ + া = আ (standalone aa-vowel, extremely common)

  // ── Uppercase — standalone vowels ────────────────────────────────
  ['A', 'অ'],   // U+0985
  ['B', 'ই'],   // U+0987
  ['C', 'ঈ'],   // U+0988
  ['D', 'উ'],   // U+0989
  ['E', 'ঊ'],   // U+098A
  ['F', 'ঋ'],   // U+098B
  ['G', 'এ'],   // U+098F
  ['H', 'ঐ'],   // U+0990
  ['I', 'ও'],   // U+0993
  ['J', 'ঔ'],   // U+0994

  // ── Uppercase — consonants ────────────────────────────────────────
  ['K', 'ক'],   // U+0995
  ['L', 'খ'],   // U+0996
  ['M', 'গ'],   // U+0997
  ['N', 'ঘ'],   // U+0998
  ['O', 'ঙ'],   // U+0999
  ['P', 'চ'],   // U+099A
  ['Q', 'ছ'],   // U+099B
  ['R', 'জ'],   // U+099C
  ['S', 'ঝ'],   // U+099D
  ['T', 'ঞ'],   // U+099E
  ['U', 'ট'],   // U+099F
  ['V', 'ঠ'],   // U+09A0
  ['W', 'ড'],   // U+09A1
  ['X', 'ঢ'],   // U+09A2
  ['Y', 'ণ'],   // U+09A3
  ['Z', 'ত'],   // U+09A4

  // ── Special ASCII → consonants ────────────────────────────────────
  ['_', 'থ'],   // U+09A5 (underscore)
  ['`', 'দ'],   // U+09A6 (backtick)

  // ── Lowercase — consonants ────────────────────────────────────────
  ['a', 'ধ'],   // U+09A7
  ['b', 'ন'],   // U+09A8
  ['c', 'প'],   // U+09AA
  ['d', 'ফ'],   // U+09AB
  ['e', 'ব'],   // U+09AC
  ['f', 'ভ'],   // U+09AD
  ['g', 'ম'],   // U+09AE
  ['h', 'য'],   // U+09AF
  ['i', 'র'],   // U+09B0
  ['j', 'ল'],   // U+09B2
  ['k', 'শ'],   // U+09B6
  ['l', 'ষ'],   // U+09B7
  ['m', 'স'],   // U+09B8
  ['n', 'হ'],   // U+09B9
  ['o', 'ড়'],  // U+09DC
  ['p', 'ঢ়'],  // U+09DD
  ['q', 'য়'],  // U+09DF
  ['r', 'ৎ'],   // U+09CE
  ['s', 'ং'],   // U+0982 anusvara
  ['t', 'ঃ'],   // U+0983 visarga
  ['u', 'ঁ'],   // U+0981 chandrabindu

  // ── Vowel signs (kars) ────────────────────────────────────────────
  // v, w, x, y: these are the most common — handle carefully
  ['v', 'া'],   // U+09BE aa-kar  (post-kar: stays after consonant)
  ['w', 'ি'],   // U+09BF i-kar   (PRE-KAR: reordered in stage 3)
  ['x', 'ী'],   // U+09C0 ii-kar  (post-kar)
  ['y', 'ু'],   // U+09C1 u-kar
  ['z', 'ু'],   // U+09C1 u-kar (alternate)
  ['~', 'ূ'],   // U+09C2 uu-kar

  // ── Extended Windows-1252 vowel signs (common in pasted Bijoy) ───
  ['\u201E', 'ৃ'],   // CP1252 0x84 → ri-kar  (U+09C3)
  ['\u2026', 'ৃ'],   // CP1252 0x85 → ri-kar
  ['\u2020', 'ে'],   // CP1252 0x86 → e-kar   (PRE-KAR: reordered in stage 3)
  ['\u2021', 'ে'],   // CP1252 0x87 → e-kar   (PRE-KAR)
  ['\u02C6', 'ৈ'],   // CP1252 0x88 → oi-kar  (PRE-KAR)
  ['\u2030', 'ৈ'],   // CP1252 0x89 → oi-kar  (PRE-KAR)
  ['\u0160', 'ৗ'],   // CP1252 0x8A → au-kar

  // ── Reph and ra-conjunct ──────────────────────────────────────────
  ['\u00A9', 'র্'],  // CP1252 0xA9 → reph (ra + hasanta) — reordered in stage 4
  ['\u00AA', '্র'],  // CP1252 0xAA → hasanta + ra (e.g., ক্র)

  // ── Dari / hasanta ────────────────────────────────────────────────
  ['\\|', '।'],       // Dari (Bengali full stop) U+0964
  ['\\&', '্\u200C'], // Explicit hasanta + ZWNJ

  // ── Bengali digits ────────────────────────────────────────────────
  ['0', '০'], ['1', '১'], ['2', '২'], ['3', '৩'], ['4', '৪'],
  ['5', '৫'], ['6', '৬'], ['7', '৭'], ['8', '৮'], ['9', '৯'],

  // ── Common pre-built conjuncts (extended ASCII single bytes) ─────
  ['\u00B0', 'ক্ক'], ['\u00B1', 'ক্ট'], ['\u00B2', 'ক্ষ্ণ'],
  ['\u00B3', 'ক্ত'], ['\u00B4', 'ক্ম'], ['\u00B5', 'ক্র'],
  ['\u00B6', 'ক্ষ'], ['\u00B7', 'ক্স'], ['\u00B8', 'গু'],
  ['\u00B9', 'জ্ঞ'], ['\u00BA', 'গ্দ'], ['\u00BB', 'গ্ধ'],
  ['\u00BC', 'ঙ্ক'], ['\u00BD', 'ঙ্গ'], ['\u00BE', 'জ্জ'],
  ['\u00BF', '্ত্র'], ['\u00C0', 'জ্ঝ'], ['\u00C1', 'জ্ঞ'],
  ['\u00C2', 'ঞ্চ'], ['\u00C3', 'ঞ্ছ'], ['\u00C4', 'ঞ্জ'],
  ['\u00C5', 'ঞ্ঝ'], ['\u00C6', 'ট্ট'], ['\u00C7', 'ড্ড'],
  ['\u00C8', 'ণ্ট'], ['\u00C9', 'ণ্ঠ'], ['\u00CA', 'ণ্ড'],
  ['\u00CB', 'ত্ত'], ['\u00CC', 'ত্থ'], ['\u00CD', 'ত্ম'],
  ['\u00CE', 'ত্র'], ['\u00CF', 'দ্দ'], ['\u00D6', '্র'],
  ['\u00D7', 'দ্ধ'], ['\u00D8', 'দ্ব'], ['\u00D9', 'দ্ম'],
  ['\u00DA', 'ন্ঠ'], ['\u00DB', 'ন্ড'], ['\u00DC', 'ন্ধ'],
  ['\u00DD', 'ন্স'], ['\u00DE', 'প্ট'], ['\u00DF', 'প্ত'],
  ['\u00E0', 'প্প'], ['\u00E1', 'প্স'], ['\u00E2', 'ব্জ'],
  ['\u00E3', 'ব্দ'], ['\u00E4', 'ব্ধ'], ['\u00E5', 'ভ্র'],
  ['\u00E6', 'ম্ন'], ['\u00E7', 'ম্ফ'], ['\u00E8', '্ন'],
  ['\u00E9', 'ল্ক'], ['\u00EA', 'ল্গ'], ['\u00EB', 'ল্ট'],
  ['\u00EC', 'ল্ড'], ['\u00ED', 'ল্প'], ['\u00EE', 'ল্ফ'],
  ['\u00EF', 'শু'],  ['\u00F0', 'শ্চ'], ['\u00F1', 'শ্ছ'],
  ['\u00F2', 'ষ্ণ'], ['\u00F3', 'ষ্ট'], ['\u00F4', 'ষ্ঠ'],
  ['\u00F5', 'ষ্ফ'], ['\u00F6', 'স্খ'], ['\u00F7', 'স্ট'],
  ['\u00F8', 'স্ন'], ['\u00F9', 'স্ফ'], ['\u00FA', '্প'],
  ['\u00FB', 'হু'],  ['\u00FC', 'হৃ'],  ['\u00FD', 'হ্ন'],
  ['\u00FE', 'হ্ম'],
];

// ─── Stage 5: Post-conversion cleanup ────────────────────────────────────────

const POST_CONVERSION: [string, string][] = [
  ['অা', 'আ'],   // A + aa-kar (Av variant) → standalone আ
  ['্্', '্'],   // double hasanta → single
  ['  ', ' '],   // double space → single
];

// ─── Bengali Unicode helpers ──────────────────────────────────────────────────

const HASANTA = '্'; // U+09CD

const isConsonant = (ch: string): boolean => {
  const code = ch.codePointAt(0) ?? 0;
  return (
    (code >= 0x0995 && code <= 0x09B9) || // ক–হ
    code === 0x09CE ||  // ৎ
    code === 0x09DC ||  // ড়
    code === 0x09DD ||  // ঢ়
    code === 0x09DF     // য়
  );
};

// Pre-kars: these appear BEFORE the consonant in Bijoy but AFTER in Unicode.
const PRE_KARS = new Set(['ি', 'ে', 'ৈ']); // U+09BF, U+09C7, U+09C8

// ─── Stage 3: Reorder pre-kars ───────────────────────────────────────────────
//
// Bijoy order:  ে + ক + ্ + ষ   (e-kar, then ka-hasanta-ssa)
// Unicode order: ক + ্ + ষ + ে  (consonant cluster, then e-kar)
//
// Also composes compound vowels:
//   ে + া → ো  (o-kar, U+09CB)
//   ে + ৗ → ৌ  (au-kar, U+09CC)

const reorderPreKars = (text: string): string => {
  const chars = Array.from(text);
  const result: string[] = [];
  let i = 0;

  while (i < chars.length) {
    const ch = chars[i];

    if (!PRE_KARS.has(ch)) {
      result.push(ch);
      i++;
      continue;
    }

    // ch is a pre-kar; skip it and collect the following consonant cluster
    const preKar = ch;
    i++;

    const cluster: string[] = [];

    // Walk forward: consonant optionally followed by hasanta + consonant (chain)
    while (i < chars.length && isConsonant(chars[i])) {
      cluster.push(chars[i]);
      i++;
      if (i < chars.length && chars[i] === HASANTA) {
        cluster.push(HASANTA);
        i++;
        // The next consonant (if any) will be picked up in the next iteration
      } else {
        break;
      }
    }

    if (cluster.length === 0) {
      // Orphan pre-kar with no following consonant — keep as-is
      result.push(preKar);
      continue;
    }

    // Compose compound vowels
    let finalKar = preKar;
    if (preKar === 'ে' && i < chars.length && chars[i] === 'া') {
      finalKar = 'ো'; // U+09CB (o-kar)
      i++;
    } else if (preKar === 'ে' && i < chars.length && chars[i] === 'ৗ') {
      finalKar = 'ৌ'; // U+09CC (au-kar)
      i++;
    }

    // Output: [consonant cluster] + [composed kar]
    result.push(...cluster, finalKar);
  }

  return result.join('');
};

// ─── Stage 4: Reorder reph (র্) ──────────────────────────────────────────────
//
// Bijoy: cluster + র্  →  Unicode: র্ + cluster
// i.e., ক + ্ + ষ + র + ্  →  র + ্ + ক + ্ + ষ
//
// We detect র followed by ্ where র is NOT itself preceded by ্
// (meaning it's a reph, not part of a hasanta-ra conjunct like ক্র).

const reorderReph = (text: string): string => {
  const chars = Array.from(text);
  const result: string[] = [];
  let i = 0;

  while (i < chars.length) {
    const ch = chars[i];

    // Detect reph: র followed by ্, not preceded by ্
    const isReph =
      ch === 'র' &&
      i + 1 < chars.length && chars[i + 1] === HASANTA &&
      (result.length === 0 || result[result.length - 1] !== HASANTA);

    if (!isReph) {
      result.push(ch);
      i++;
      continue;
    }

    // Find the start of the preceding consonant cluster in result[]
    let j = result.length - 1;

    // Skip over any post-kars (া, ী, ু, ূ, ৃ) sitting after the cluster
    while (j >= 0 && !isConsonant(result[j]) && result[j] !== HASANTA) {
      j--;
    }
    // Walk back through consonant + hasanta pairs
    while (j >= 1 && result[j - 1] === HASANTA) {
      j -= 2;
    }

    // Insert র্ at position j (before the consonant cluster)
    result.splice(j, 0, 'র', HASANTA);
    i += 2; // skip র + ্
  }

  return result.join('');
};

// ─── Detection ────────────────────────────────────────────────────────────────
//
// Bijoy markers: sequences extremely common in Bengali Bijoy text
// but very rare in normal English text.
//
// Based on SutonnyMJ map: v=া (aa-kar), w=ি (i-kar), b=ন, g=ম, e=ব, j=ল, etc.
// Examples: bv=না, gv=মা, mv=সা, jv=লা, wg=+মি, wb=+নি (+ means pre-kar)

// IMPORTANT: Do NOT add 'ev' or 'iv' here — they appear constantly in English
// ('every', 'seven', 'live', 'give', etc.) and cause false positives.
// Only include bigrams that are extremely rare in English prose.
const BIJOY_MARKERS = [
  'bv',  // না  (ন+া)
  'gv',  // মা  (ম+া)
  'mv',  // সা  (স+া)
  'jv',  // লা  (ল+া)
  'wg',  // মি  (ি+ম — pre-kar sequence)
  'wb',  // নি  (ি+ন — pre-kar sequence)
  'wK',  // কি  (ি+ক — pre-kar sequence)
  'Av',  // আ   (standalone আ vowel)
];

export const isBijoyEncoded = (text: string): boolean => {
  if (!text || text.trim().length < 5) return false;
  // Already has Unicode Bengali → definitely not Bijoy
  if (countBengaliChars(text) > 0) return false;

  // Require at least 2 Bijoy-specific marker sequences
  const markerCount = BIJOY_MARKERS.filter(m => text.includes(m)).length;
  if (markerCount < 2) return false;

  // Secondary guard: in Bijoy text 'v' (=া aa-kar) is very frequent (~10-20% of
  // non-whitespace chars). In English 'v' appears at ~1%. Any text where 'v' is
  // below 4% is almost certainly English, not Bijoy — even if it contains rare
  // bigrams like "obvious" (bv) or a sentence starting with "Av...".
  const nonWhitespace = text.replace(/\s/g, '').length;
  if (nonWhitespace === 0) return false;
  const vDensity = (text.match(/v/g) ?? []).length / nonWhitespace;
  return vDensity > 0.04; // Bijoy: ~10-20%, English: ~1%
};

// ─── Main conversion ──────────────────────────────────────────────────────────

export const convertBijoyToUnicode = (text: string): string => {
  // Stage 1: pre-conversion fixes
  let result = text;
  for (const [from, to] of PRE_CONVERSION) {
    result = result.split(from).join(to);
  }

  // Stage 2: character mapping (multi-char sequences first, then single-char)
  for (const [bijoy, unicode] of CHAR_MAP) {
    result = result.split(bijoy).join(unicode);
  }

  // Stage 3: reorder pre-kars (ি, ে, ৈ must come AFTER their consonant in Unicode)
  result = reorderPreKars(result);

  // Stage 4: reorder reph (র্ must come BEFORE its consonant cluster in Unicode)
  result = reorderReph(result);

  // Stage 5: post-conversion cleanup
  for (const [from, to] of POST_CONVERSION) {
    result = result.split(from).join(to);
  }

  return result;
};
