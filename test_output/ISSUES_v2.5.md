# Issues Documentation - v2.5 (2026-01-17)

## Status: PARTIAL FIX - Needs Review

---

## Issues Fixed by Code

### 1. Quote Splitting ✅ FIXED (needs verification)
- **Original Problem**: Text appearing after closing quotes in same paragraph
- **v2.5 Solution**: Code-based regex split at `।"` or `"।` patterns
- **Current Status**: Fixed pattern to only split at CLOSING quotes (not opening quotes)
- **Pattern**: `([।!?]"|"[।!?])\s+(\S.+)` - splits when punctuation+quote followed by text

### 2. সহ Joining Bug ✅ FIXED
- **Original Problem**: `একজন সহায়ক` → `একজনসহায়ক` (breaking words)
- **v2.5 Solution**: Smart regex with exception list
- **Exceptions**: সহায়, সহযোগ, সহকার, সহজ, সহ্য, সহস্র, etc.
- **Pattern**: Only joins `X সহ` when সহ is standalone "with" meaning

### 3. English Words ✅ PARTIAL
- **Original Problem**: Words like "landmark", "sharply", "accompanying" appearing
- **v2.5 Solution**: Dictionary replacement in post-processing
- **Current Dictionary**: 20+ common words mapped
- **Note**: May need to expand dictionary based on new issues

---

## Issues NOT Fully Solved

### 4. Multiple Quotes in Same Paragraph ⚠️ PARTIAL
- **Problem**: Two quotes in same paragraph should be split
- **Example**: `তিনি বলেন, "X।" তিনি আরও বলেন, "Y।"`
- **Current Fix**: Only splits if text after quote, not if another quote starts
- **Need**: May need additional logic for quote-after-quote pattern

### 5. Paragraph Word Count > 35 ⚠️ NOT FIXED BY CODE
- **Problem**: Body paragraphs exceeding 35 words
- **Current**: `enforce_paragraph_length()` splits at sentence boundaries
- **Issue**: If a single sentence is > 35 words, cannot split
- **Note**: AI Checker was supposed to fix this but failed

### 6. Quality Degradation ⚠️ NEEDS REVIEW
- **User Feedback**: "i think it downgraded the quality"
- **Possible Causes**:
  - Removed AI Checker may have done some quality improvements
  - Code-based fixes may be too aggressive
  - Prompt changes may have affected output
- **Action**: Need to compare v2.4 vs v2.5 outputs manually

---

## Issues Identified in Feedback (feedback.txt)

### From Article 1:
- Hard News: `একজনসহায়ক` - **FIXED** with smart সহ joining
- Soft News: Quote ending issue - **FIXED** with quote splitter

### From Article 2:
- Hard News: Two quotes in same paragraph - **PARTIAL FIX**
- Hard News: Paragraph > 40 words - **NOT FIXED BY CODE**
- Soft News: Text after quote - **FIXED**

### From Article 3:
- Hard News: Text after quote - **FIXED**

### From Article 7:
- English words: "landmark", "sharply" - **FIXED** with dictionary

---

## Code Changes Made in v2.5

### text_processor.py
1. `split_quotes()` - NEW: Splits paragraphs at closing quote boundaries
2. `fix_saho_joining()` - NEW: Smart সহ joining with exceptions
3. `replace_english_words()` - NEW: Dictionary-based English replacement
4. `process_enhanced_content()` - UPDATED: Added new steps to pipeline

### enhancer.py
1. Removed `run_checker()` - AI Checker removed
2. `enhance_single_format()` - UPDATED: No longer calls AI Checker, code fixes only

### bengali_news_styles.json
1. Added সমাপ্তি (Conclusion) section to Soft News
2. Updated version to 2.5

---

## Recommendations for Further Work

1. **Manual Quality Review**: Compare v2.4 vs v2.5 outputs side-by-side
2. **Expand English Dictionary**: Add more words as they're found
3. **Multiple Quote Handling**: Improve detection of quote-after-quote
4. **Long Sentence Handling**: Consider splitting at comma for very long sentences
5. **Consider Hybrid Approach**: Maybe use AI Checker only for specific cases

---

## Files Modified
- `backend/app/core/text_processor.py`
- `backend/app/core/enhancer.py`
- `backend/app/config/formats/bengali_news_styles.json`
- `test_all_articles.py`

---

## Test Results (7 Articles)
- 2-Paragraph Rule: 7/7 PASS
- Quote Issues Detected: Multiple (fixed by code)
- Code Fixed Applied: Yes (most articles)

---

*Document created: 2026-01-17*
*Version: 2.5*
