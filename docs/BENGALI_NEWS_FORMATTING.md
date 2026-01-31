# Bengali News Formatting Guide

## Overview

This document describes the formatting rules for Bengali news content generation in Swiftor.

## Format Types

### Hard News (হার্ড নিউজ)

| Component | Lines | Bold | Notes |
|-----------|-------|------|-------|
| Headline | 1 | **Yes** | No prefix |
| Byline | 1 | No | `নিউজ ডেস্ক, বাংলার কলম্বাস` |
| Intro | 3 | **Yes** | 3 sentences, FULLY bold |
| Body | Max 2 per para | No | Each paragraph max 2 sentences |

**Word Count Requirement:**
- Minimum: **220 words** (from intro to conclusion)
- The system regenerates up to 2 times if below 220 words

### Soft News (সফট নিউজ)

| Component | Lines | Bold | Notes |
|-----------|-------|------|-------|
| Headline | 1 | **Yes** | No prefix |
| Byline | 1 | No | `নিউজ ডেস্ক, বাংলার কলম্বাস` |
| Intro 1 | 3-4 | **Yes** | Vivid hook, FULLY bold |
| Intro 2 | 2-3 | No | Context/background |
| Subhead | 1 | **Yes** | Bold, no brackets |
| Body | Max 2 per para | No | Each paragraph max 2 sentences |

**Critical Rule:** Exactly 2 paragraphs before the first subhead.

---

## Post-Processing Pipeline

The following code-based fixes are applied in order:

1. **`fix_intro_structure()`** - Ensures intros are FULLY bold
2. **`apply_word_corrections()`** - Fixes Bengali spelling (শীঘ্রই → শিগগিরই)
3. **`fix_saho_joining()`** - Joins `X সহ` → `Xসহ`
4. **`replace_english_words()`** - Converts remaining English words
5. **`split_quotes()`** - Ensures paragraphs end at quotes
6. **`fix_three_line_paragraphs()`** - Splits 3+ sentence paragraphs into max 2

---

## Configuration

### Temperature Setting
- Hard News: **0.5** (increased from 0.4 for more variety)
- Soft News: **0.5**

### Model Configuration
Current: `gpt-4o-mini`

**Known Limitation:** gpt-4o-mini tends to produce shorter content. Despite explicit 220-word instructions, approximately 2/7 test articles may fall below the minimum.

**Planned Test:** Switch to `gpt-4o` for better word count compliance.

| Model | Input Cost | Output Cost | Notes |
|-------|------------|-------------|-------|
| gpt-4o-mini | $0.15/1M | $0.60/1M | Current, shorter output |
| gpt-4o | $2.50/1M | $10.00/1M | ~17x more expensive, better compliance |

---

## Testing

### Run Full Test
```bash
python test_all_articles.py
```

### Test Output
- Location: `test_output/all_articles_test_results.docx`
- Validates: Structure, word count, intro formatting

### Current Test Results (2026-01-31)
- Soft News 2-para rule: **7/7 PASS**
- Hard News 220-word minimum: **5/7 PASS** (model limitation)

---

## Files

| File | Purpose |
|------|---------|
| `config/formats/bengali_news_styles.json` | Prompt configurations |
| `config/formats/news_guidelines_feedback.json` | Validation rules |
| `backend/app/core/text_processor.py` | Post-processing functions |
| `backend/app/core/enhancer.py` | Content generation with regeneration |
| `test_all_articles.py` | Comprehensive format testing |

---

## TODO

- [ ] Test with `gpt-4o` model for better word count compliance
- [ ] Evaluate cost vs quality tradeoff
- [ ] Consider hybrid approach: gpt-4o-mini for soft news, gpt-4o for hard news
