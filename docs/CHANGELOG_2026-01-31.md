# Changelog - 2026-01-31

## Hard News & Intro Bold Fixes

### Problem Summary
1. **Hard news generating as soft news** - Sometimes hard news was being generated with subheads (soft news format)
2. **Intro not always bold** - The intro paragraph was not consistently being made bold

---

## Changes Made

### 1. Hard News Prompt Update
**File:** `config/formats/bengali_news_styles.json`

Added explicit "NO SUBHEADS" instruction at the top of hard news prompt:
```
⛔⛔⛔ সর্বোচ্চ গুরুত্বপূর্ণ - NO SUBHEADS ⛔⛔⛔

❌ হার্ড নিউজে কোনো সাবহেড/সেকশন হেডার থাকবে না!
❌ বোল্ড উপশিরোনাম একদম ব্যবহার করবেন না!
❌ শুধুমাত্র শিরোনাম এবং ইন্ট্রো বোল্ড হবে, বডিতে কোনো বোল্ড লাইন নয়!
```

### 2. Backend Post-Processing Updates
**File:** `backend/app/core/text_processor.py`

#### New Function: `strip_hard_news_subheads()`
- Removes any bold subheads from hard news output
- Safety net in case AI still generates subheads despite prompt instruction
- Converts bold subheads to regular paragraphs

#### Improved Function: `final_intro_bold_check()`
- Now uses robust `make_fully_bold()` function
- Added double-check with error logging if bold still fails
- This is the LAST LINE OF DEFENSE for intro bolding

#### Updated Pipeline Order:
```
1. Normalize line breaks
2. Strip subheads (hard news only) ← NEW
3. Enforce intro sentence count
4. Fix intro structure (make fully bold)
5. Apply word corrections
6. Fix সহ joining
7. Replace English words
8. Split quotes
9. Fix 3-line paragraphs
10. Final bold check ← IMPROVED
11. Validate structure
```

### 3. Frontend Fixes
**Files:**
- `frontend/src/components/common/OperationStatusBar.tsx`
- `frontend/src/components/translation/EnhancementSection.tsx`
- `frontend/src/components/translation/FormatCard.tsx`

#### OperationStatusBar.tsx
- Fixed notification positioning (now centered)
- Fixed text capitalization: "Generating News Articles"

#### EnhancementSection.tsx
- Added global pending state check from Zustand store
- Loading state now persists when navigating away and back

#### FormatCard.tsx
- Fixed regex to match bold markers across newlines: `/\*\*([\s\S]+?)\*\*/g`

### 4. Additional Features
- Password reset functionality with email service
- User dashboard page
- Forgot password and reset password pages

---

## Technical Details

### Why Intro Bold Was Failing
Markdown `**bold**` must be on ONE line - newlines inside break the parsing.

**Before (broken):**
```
**First sentence.
Second sentence.**
```

**After (fixed):**
```
**First sentence. Second sentence.**
```

The `make_fully_bold()` function now:
1. Removes all existing `**` markers
2. Removes ALL newlines (`\r\n`, `\n`, `\r`)
3. Collapses multiple spaces
4. Wraps in `**...**`

### Hard News Structure (Expected)
```
P1: **Headline** (bold)
P2: Byline (NOT bold)
P3: **Intro** (FULLY bold, 3 sentences)
P4+: Body paragraphs (NOT bold, NO subheads)
```

### Soft News Structure (Expected)
```
P1: **Headline** (bold)
P2: Byline (NOT bold)
P3: **Intro 1** (FULLY bold, 3-4 sentences)
P4: Intro 2 (NOT bold)
P5: **First Subhead** (bold)
P6+: Body paragraphs with subheads
```

---

## Files Modified
| File | Changes |
|------|---------|
| `config/formats/bengali_news_styles.json` | Added NO SUBHEADS instruction |
| `backend/app/core/text_processor.py` | Added strip_hard_news_subheads(), improved final_intro_bold_check() |
| `frontend/src/components/common/OperationStatusBar.tsx` | Fixed positioning and text |
| `frontend/src/components/translation/EnhancementSection.tsx` | Added global pending state |
| `frontend/src/components/translation/FormatCard.tsx` | Fixed bold regex |
| `test_all_articles.py` | Updated with improved intro processing |

---

## Testing
Run the test script to verify:
```bash
python test_all_articles.py
```

Check output for:
- All hard news intros are FULLY bold
- All soft news intro 1s are FULLY bold
- No subheads in hard news output
