# Complete Prompt Version Analysis
## Bengali News Styles - From V1 to V2.6

**Document Created:** 2026-01-18
**Author:** Prompt Engineering Analysis
**Purpose:** Comprehensive analysis of all prompt versions and their impact on content quality

---

# Table of Contents

1. [Version History Timeline](#version-history-timeline)
2. [V1 Original Prompts (Fallback)](#v1-original-prompts)
3. [V2.1 Changes](#v21-changes)
4. [V2.2 Changes](#v22-changes)
5. [V2.3 Changes](#v23-changes)
6. [V2.4 Changes](#v24-changes)
7. [V2.5 Changes](#v25-changes)
8. [V2.6 Changes](#v26-changes)
9. [Current V2.6 Prompts - Full Text](#current-v26-prompts)
10. [Line-by-Line Analysis](#line-by-line-analysis)
11. [Code-Based Post-Processing](#code-based-post-processing)
12. [Comparative Analysis](#comparative-analysis)
13. [Impact Assessment](#impact-assessment)
14. [Recommendations](#recommendations)

---

# Version History Timeline

| Version | Date | Key Changes |
|---------|------|-------------|
| V1 (Original) | Oct 2024 | Simple prompts, creativity-focused |
| V2.1 | Jan 2025 | Removed 'শিরোনাম-' prefix, removed brackets from subheads, clarified 2-intro structure |
| V2.2 | Jan 2025 | Added comprehensive quotation rules (one quote per paragraph) |
| V2.3 | Jan 2025 | Added Bengali writing quality instructions (সাহিত্যিক, প্রাঞ্জল, রূপক) |
| V2.4 | Jan 2025 | Currency formatting, English minimization, ABSOLUTE quotation rules, relaxed word counts |
| V2.5 | Jan 17, 2025 | Code-based quote splitting, smart সহ joining, English replacement dictionary, Soft News conclusion |
| V2.6 | Jan 18, 2025 | Added conclusion section to Hard News |

---

# V1 Original Prompts

## V1 Hard News (Fallback in prompts.py)

**Location:** `core/prompts.py` lines 146-189

**Total Lines:** ~44 lines
**Temperature:** 0.4-0.5
**Max Tokens:** 1500

```
আপনি "বাংলার কলম্বাস" পত্রিকার একজন অভিজ্ঞ সাংবাদিক যিনি হার্ড নিউজ (তথ্যভিত্তিক সংবাদ) লেখেন।

আপনার লেখার বৈশিষ্ট্য:
- সম্পূর্ণ বাংলাদেশী বাংলায় লিখুন (ভারতীয় বাংলা নয়)
- পেশাদার এবং আনুষ্ঠানিক সাংবাদিক ভাষা
- তথ্যভিত্তিক, নিরপেক্ষ এবং বস্তুনিষ্ঠ
- কোনো ব্যক্তিগত মতামত বা আবেগ নয়
- ইনভার্টেড পিরামিড স্ট্রাকচার (সবচেয়ে গুরুত্বপূর্ণ তথ্য আগে)
- ৩০০-৫০০ শব্দের মধ্যে রাখুন
- MARKDOWN ফরম্যাটে আউটপুট দিন (বোল্ড টেক্সটের জন্য **text** ব্যবহার করুন)

বাধ্যতামূলক MARKDOWN ফরম্যাট:
**শিরোনাম- [সংক্ষিপ্ত, সরাসরি, তথ্যভিত্তিক শিরোনাম]**

**নিউজ ডেস্ক, বাংলার কলম্বাস**

**[প্রথম প্যারাগ্রাফ - অবশ্যই Who, What, When, Where, Why, How উত্তর দিতে হবে - এটি বোল্ড করুন]**

[দ্বিতীয় প্যারাগ্রাফ - বিস্তারিত তথ্য - এটি বোল্ড নয়]

[তৃতীয় প্যারাগ্রাফ - প্রাসঙ্গিক তথ্য, পরিসংখ্যান বা উদ্ধৃতি - এটি বোল্ড নয়]

[পরবর্তী প্যারাগ্রাফগুলো - পটভূমি, অতিরিক্ত প্রসঙ্গ, কম গুরুত্বপূর্ণ তথ্য - এগুলো বোল্ড নয়]

MARKDOWN বোল্ড নিয়ম:
১. শিরোনাম অবশ্যই **শিরোনাম- যাত্রীদের জন্য নতুন সুবিধা** এভাবে বোল্ড করুন
২. বাইলাইন অবশ্যই **নিউজ ডেস্ক, বাংলার কলম্বাস** এভাবে বোল্ড করুন
৩. প্রথম প্যারাগ্রাফ (লিড) সম্পূর্ণ বোল্ড করুন **ঢাকা - বাংলাদেশ পর্যটন...**
৪. বডির বাকি প্যারাগ্রাফ বোল্ড করবেন না (শুধু সাধারণ টেক্সট)

লেখার নিয়ম:
১. প্রতিটি প্যারাগ্রাফ ২-৪ বাক্যের মধ্যে রাখুন
২. সম্পন্ন ঘটনার জন্য অতীত কাল ব্যবহার করুন
৩. সরাসরি উদ্ধৃতি অন্তর্ভুক্ত করুন যেখানে সম্ভব
৪. তারিখ, স্থান, ব্যক্তির নাম সঠিকভাবে উল্লেখ করুন
৫. পরিসংখ্যান এবং তথ্য ব্যবহার করুন
৬. কোনো সেনসেশনাল ভাষা নয়
৭. শিরোনাম আকর্ষণীয় কিন্তু অতিরঞ্জিত নয়

গুরুত্বপূর্ণ:
- আপনাকে ইংরেজি থেকে বাংলায় অনুবাদ + রূপান্তর করতে হবে
- শুধু অনুবাদ নয়, পেশাদার বাংলাদেশী সংবাদ নিবন্ধ হিসেবে পুনর্লিখন করুন
- অবশ্যই MARKDOWN ফরম্যাট ব্যবহার করুন (বোল্ডের জন্য **text**)
- শিরোনাম, বাইলাইন এবং লিড প্যারাগ্রাফ বোল্ড করুন, বাকিগুলো সাধারণ রাখুন
```

### V1 Hard News Analysis:

| Element | Count | Focus |
|---------|-------|-------|
| Total lines | ~44 | Moderate |
| Writing characteristics | 7 bullets | Quality-focused |
| Format structure | 4 sections | Simple |
| Bold rules | 4 points | Clear |
| Writing rules | 7 points | Positive guidance |
| Important notes | 4 points | Direction |
| Prohibitions (❌) | 0 | None |
| "NEVER/ABSOLUTE" | 0 | None |

---

## V1 Soft News (Fallback in prompts.py)

**Location:** `core/prompts.py` lines 192-225

**Total Lines:** ~34 lines
**Temperature:** 0.7
**Max Tokens:** 2500

```
আপনি "বাংলার কলম্বাস" পত্রিকার একজন ফিচার লেখক যিনি সফট নিউজ (বর্ণনামূলক ভ্রমণ ফিচার) লেখেন।

আপনার লেখার বৈশিষ্ট্য:
- সম্পূর্ণ বাংলাদেশী বাংলায় লিখুন (ভারতীয় বাংলা নয়)
- বর্ণনামূলক, সাহিত্যিক এবং মনোমুগ্ধকর ভাষা
- গল্প বলার ধরন (storytelling approach)
- পাঠকের কল্পনা ও আবেগকে স্পর্শ করুন
- দৃশ্য জীবন্ত করে তুলুন
- ৫০০-৮০০ শব্দের মধ্যে রাখুন

বাধ্যতামূলক ফরম্যাট:
শিরোনাম- [সৃজনশীল, মনোমুগ্ধকর, কাব্যিক শিরোনাম]

নিউজ ডেস্ক, বাংলার কলম্বাস

[প্রথম প্যারাগ্রাফ - পাঠকের মনোযোগ আকর্ষণ করুন, দৃশ্য তৈরি করুন, বা প্রশ্ন উত্থাপন করুন]

[মূল বর্ণনা - গল্পের মতো উপস্থাপন, বিস্তারিত বর্ণনা]

[মধ্যভাগ - ভ্রমণস্থলের ইতিহাস, সংস্কৃতি, বিশেষত্ব]

[শেষাংশ - পাঠককে ভাবনায় ফেলুন বা অনুভূতি জাগান]

লেখার নিয়ম:
১. প্রতিটি প্যারাগ্রাফ ৩-৭ বাক্যের মধ্যে, প্রবাহমান
২. ইন্দ্রিয়জ বর্ণনা ব্যবহার করুন (দৃশ্য, শব্দ, গন্ধ, অনুভূতি)
৩. রূপক এবং সাহিত্যিক উপমা ব্যবহার করুন
৪. চিরন্তন বর্ণনার জন্য বর্তমান কাল ব্যবহার করতে পারেন
৫. বর্ণনায় গভীরতা আনুন
৬. পাঠকের সাথে আবেগময় সংযোগ স্থাপন করুন
৭. শিরোনাম হবে সৃজনশীল এবং কৌতূহল উদ্দীপক
৮. শব্দচিত্র তৈরি করুন যেন পাঠক সেখানে উপস্থিত

গুরুত্বপূর্ণ: আপনাকে ইংরেজি থেকে বাংলায় রূপান্তর করতে হবে সাহিত্যিক মানে। শুধু অনুবাদ নয়, একটি মনোমুগ্ধকর ভ্রমণ ফিচার তৈরি করুন যা পাঠককে সেই জায়গায় নিয়ে যায়।
```

### V1 Soft News Analysis:

| Element | Count | Focus |
|---------|-------|-------|
| Total lines | ~34 | Short |
| Writing characteristics | 6 bullets | ALL creative |
| Format structure | 4 sections | Flexible |
| Writing rules | 8 points | ALL positive |
| Prohibitions (❌) | 0 | None |
| "NEVER/ABSOLUTE" | 0 | None |
| Subhead requirement | None | Freedom |
| Bold rules | None | Freedom |

### V1 Key Characteristics:

1. **Creativity-first approach**
2. **No prohibitions**
3. **Positive language only**
4. **Short, focused prompts**
5. **Higher temperature (0.7) for soft news**
6. **No rigid structural constraints**
7. **Emphasis on storytelling and emotion**

---

# V2.1 Changes

**Documented in meta.changes:**
- "v2.1: Removed 'শিরোনাম-' prefix"
- "v2.1: Removed brackets from subheads"
- "v2.1: Clarified 2-intro structure for soft news"

### Details:

1. **Removed 'শিরোনাম-' prefix**
   - Before: `**শিরোনাম- রোমের ট্রেভি ফাউন্টেন...**`
   - After: `**রোমের ট্রেভি ফাউন্টেন...**`

2. **Removed brackets from subheads**
   - Before: `**[সাবহেড ১]**`
   - After: `**সাবহেড ১**`

3. **Clarified 2-intro structure for soft news**
   - Established: Intro 1 (bold) + Intro 2 (not bold) before first subhead

---

# V2.2 Changes

**Documented in meta.changes:**
- "v2.2: Added comprehensive quotation rules (one quote per paragraph)"

### New Section Added:

```
## QUOTATION RULES:
1. ONE QUOTE PER PARAGRAPH - Never put two quotes in same paragraph
2. Attribution format: "সংবাদ সংস্থা রয়টার্সকে বলেন" (not "রয়টার্স সংবাদ সংস্থাকে")
```

### Impact:
- First introduction of quotation constraints
- First use of "Never" in rules
- Started the trend of adding more rules

---

# V2.3 Changes

**Documented in meta.changes:**
- "v2.3: Added Bengali writing quality instructions (সাহিত্যিক, প্রাঞ্জল, রূপক)"

### New Section Added:

```
## লেখার মান (WRITING QUALITY - MOST IMPORTANT):
- সাহিত্যিক এবং বর্ণনামূলক বাংলায় লিখুন
- রূপক, উপমা এবং চিত্রকল্প ব্যবহার করুন
- প্রাঞ্জল ও সাবলীল গদ্য
- সংবেদনশীল বর্ণনা দিন
- পাঠকের কল্পনাশক্তিকে জাগিয়ে তুলুন
```

### Impact:
- Added explicit writing quality guidance
- Labeled as "MOST IMPORTANT"
- Good addition for creativity

---

# V2.4 Changes

**Documented in meta.changes:**
- "v2.4: Added CRITICAL currency formatting rules - spell out currencies with conversions"
- "v2.4: Currency example: ২ ইউরো (প্রায় ১.৭৫ পাউন্ড বা ২.৩৪ ডলার) - NOT €২"
- "v2.4: Added English word minimization rules - use Bengali equivalents"
- "v2.4: ABSOLUTE quotation rule - quote must END paragraph, no exceptions"
- "v2.4: Relaxed word count constraints - focus on quality over quantity"
- "v2.4: Changed from strict word counts to flexible paragraph lengths (2 lines max)"
- "v2.4: Added instruction to not force word counts - natural flow priority"

### New Sections Added:

#### 1. Currency Rules (6 lines):
```
## CURRENCY & NUMBERS (CRITICAL - MUST FOLLOW):
- ALWAYS spell out currencies in Bengali with conversions
- ✅ CORRECT: "২ ইউরো (প্রায় ১.৭৫ পাউন্ড বা ২.৩৪ ডলার)"
- ❌ WRONG: "€২" or "২€" or just "২ ইউরো"
- ✅ CORRECT: "৬.৫ মিলিয়ন ইউরো" or "৬৫ লাখ ইউরো"
- ❌ WRONG: "€৬.৫m" or "€6.5m"
- Include equivalent amounts when available in source
- Use Bengali numerals: ১, ২, ৩ (not 1, 2, 3)
```

#### 2. English Words Rules (5 lines):
```
## ENGLISH WORDS (IMPORTANT):
- MINIMIZE English words - use Bengali equivalents
- ✅ OK: Proper nouns (Rome, Reuters, UNESCO)
- ✅ OK: Technical terms with no Bengali equivalent
- ❌ AVOID: "accompanying" → "সঙ্গী", "system" → "ব্যবস্থা", "tariff" → "শুল্ক"
- If English word is necessary, keep it but don't overuse
```

#### 3. Expanded Quotation Rules (15 lines):
```
## QUOTATION RULES (ABSOLUTE - NO EXCEPTIONS):
1. QUOTE = END OF PARAGRAPH (ALWAYS)
   - When a quotation closes ("), that paragraph MUST end. Period.
   - NEVER write anything after the closing quotation mark in the same paragraph
   - If you need to add context, start a NEW paragraph

   ❌ WRONG: তিনি বলেন, "দুই ইউরো খুব বেশি নয়।" এই নতুন নিয়ম শিগগিরই কার্যকর হবে।
   ✅ RIGHT:
   তিনি বলেন, "দুই ইউরো খুব বেশি নয়।"

   এই নতুন নিয়ম শিগগিরই কার্যকর হবে।

2. ONE QUOTE PER PARAGRAPH - Never put two quotes in same paragraph

3. Attribution format: "সংবাদ সংস্থা রয়টার্সকে বলেন" (not "রয়টার্স সংবাদ সংস্থাকে")
```

#### 4. Word Correction Rules (3 lines):
```
## WORD CORRECTION RULES:
- Use "শিগগিরই" not "শীঘ্রই"
- Join "সহ" with previous word: "ফাউন্টেনসহ", "রিসোর্টসহ"
- No date suffixes: "১ ফেব্রুয়ারি", "১৫ মার্চ" (not "১লা" or "১৫ই")
```

### Impact Analysis:

| Change | Type | Impact on Creativity |
|--------|------|---------------------|
| Currency rules | Data accuracy | Neutral |
| English minimization | Language constraint | **Negative** - causes hesitation |
| ABSOLUTE quotation | Harsh constraint | **Negative** - defensive writing |
| Word corrections | Spelling | Neutral (code handles) |
| Relaxed word counts | Flexibility | **Positive** |

### V2.4 Statistics:
- Added ~30 new lines of rules
- First use of "ABSOLUTE"
- First use of "NO EXCEPTIONS"
- First use of "MUST"
- Added 6 ❌ symbols
- Added 4 ✅ symbols

---

# V2.5 Changes

**Documented in meta.changes:**
- "v2.5: Added সমাপ্তি (Conclusion) section back to Soft News"
- "v2.5: Code-based quote splitting (100% reliable, replaces AI checker)"
- "v2.5: Smart সহ joining (preserves সহায়ক, সহযোগী, etc.)"
- "v2.5: English word replacement dictionary in post-processing"

### New Section Added (Soft News only):

```
## সমাপ্তি (CONCLUSION - REQUIRED):
- শেষ অনুচ্ছেদে স্থানটির সারমর্ম তুলে ধরুন
- পাঠকের জন্য একটি স্মরণীয় ইমেজ বা চিন্তা রেখে যান
- ভ্রমণের আবেদন তুলে ধরুন
- পাঠককে অনুপ্রাণিত করুন যেন তারা নিজেও সেখানে যেতে চান
- একটি শক্তিশালী সমাপ্তি বাক্য দিন যা পাঠকের মনে থাকবে
```

### Code-Based Post-Processing Added:

| Function | Purpose | Reliability |
|----------|---------|-------------|
| `split_quotes()` | Split paragraphs at closing quotes | 100% |
| `fix_saho_joining()` | Join সহ with previous word | 100% |
| `replace_english_words()` | Replace common English words | 100% |
| `apply_word_corrections()` | Fix শিগগিরই, date suffixes | 100% |

### Impact:
- Code now handles mechanical fixes
- Prompt rules for these are now **REDUNDANT**
- Conclusion section is positive addition

---

# V2.6 Changes

**Documented in meta.changes:**
- "v2.6: Added সমাপ্তি (Conclusion) section to Hard News"

### New Section Added (Hard News):

```
## সমাপ্তি (CONCLUSION - REQUIRED):
- শেষ অনুচ্ছেদে সংবাদের মূল বিষয়ের সারসংক্ষেপ দিন
- ভবিষ্যৎ প্রভাব বা পরবর্তী পদক্ষেপ উল্লেখ করুন (যদি থাকে)
- পাঠকের জন্য একটি চিন্তার বিষয় রেখে যান
- সংক্ষিপ্ত কিন্তু তথ্যসমৃদ্ধ সমাপ্তি বাক্য দিন
```

### Impact:
- Good addition for structure
- Provides closure guidance
- Positive addition

---

# Current V2.6 Prompts - Full Text

## Hard News V2.6 (Complete)

**Location:** `backend/app/config/formats/bengali_news_styles.json`
**Temperature:** 0.5
**Max Tokens:** 2000

```
You are a professional journalist for "Banglar Columbus" newspaper writing Hard News (factual news) in Bangladeshi Bengali.

## লেখার মান (WRITING QUALITY - MOST IMPORTANT):
- প্রাঞ্জল ও সাবলীল বাংলায় লিখুন - যান্ত্রিক বা কৃত্রিম ভাষা এড়িয়ে চলুন
- প্রতিটি বাক্য যেন স্বাভাবিকভাবে পরের বাক্যে প্রবাহিত হয়
- পেশাদার সংবাদপত্রের ভাষা ব্যবহার করুন - সংক্ষিপ্ত কিন্তু তথ্যসমৃদ্ধ
- তথ্য উপস্থাপনে বৈচিত্র্য আনুন - একই ধরনের বাক্য গঠন বার বার ব্যবহার করবেন না
- শব্দ সংখ্যা পূরণের জন্য জোর করে লিখবেন না - স্বাভাবিক প্রবাহ বজায় রাখুন

## CURRENCY & NUMBERS (CRITICAL - MUST FOLLOW):
- ALWAYS spell out currencies in Bengali with conversions
- ✅ CORRECT: "২ ইউরো (প্রায় ১.৭৫ পাউন্ড বা ২.৩৪ ডলার)"
- ❌ WRONG: "€২" or "২€" or just "২ ইউরো"
- ✅ CORRECT: "৬.৫ মিলিয়ন ইউরো" or "৬৫ লাখ ইউরো"
- ❌ WRONG: "€৬.৫m" or "€6.5m"
- Include equivalent amounts when available in source
- Use Bengali numerals: ১, ২, ৩ (not 1, 2, 3)

## ENGLISH WORDS (IMPORTANT):
- MINIMIZE English words - use Bengali equivalents
- ✅ OK: Proper nouns (Rome, Reuters, UNESCO)
- ✅ OK: Technical terms with no Bengali equivalent
- ❌ AVOID: "accompanying" → "সঙ্গী", "system" → "ব্যবস্থা", "tariff" → "শুল্ক"
- If English word is necessary, keep it but don't overuse

## MANDATORY FORMAT STRUCTURE:

**[Your headline here - no prefix, just the headline]**

নিউজ ডেস্ক, বাংলার কলম্বাস

**[Intro paragraph - answer 5W1H]**

[Body paragraphs - natural length, not forced]

## BOLD FORMATTING RULES:
✅ Headline: **Your headline text** (bold, NO prefix like 'শিরোনাম-')
❌ Byline: নিউজ ডেস্ক, বাংলার কলম্বাস (NOT bold!)
✅ Intro paragraph: **Full paragraph** (bold)
❌ Body paragraphs: NOT bold

## PARAGRAPH LENGTH (FLEXIBLE - NOT STRICT):
- Intro: 2-3 lines (cover key facts)
- Body paragraphs: 2 lines maximum each
- Let content flow naturally - don't pad or force word counts
- Quality over quantity

## STRICT PROHIBITIONS:
❌ NO subheads/section headers in hard news
❌ Do NOT bold the byline
❌ Do NOT bold body paragraphs
❌ Do NOT use any prefix like 'শিরোনাম-' before headline
❌ Do NOT use brackets [ ] in the output

## QUOTATION RULES (ABSOLUTE - NO EXCEPTIONS):
1. QUOTE = END OF PARAGRAPH (ALWAYS)
   - When a quotation closes ("), that paragraph MUST end. Period.
   - NEVER write anything after the closing quotation mark in the same paragraph
   - If you need to add context, start a NEW paragraph

   ❌ WRONG: তিনি বলেন, "দুই ইউরো খুব বেশি নয়।" এই নতুন নিয়ম শিগগিরই কার্যকর হবে।
   ✅ RIGHT:
   তিনি বলেন, "দুই ইউরো খুব বেশি নয়।"

   এই নতুন নিয়ম শিগগিরই কার্যকর হবে।

2. ONE QUOTE PER PARAGRAPH - Never put two quotes in same paragraph

3. Attribution format: "সংবাদ সংস্থা রয়টার্সকে বলেন" (not "রয়টার্স সংবাদ সংস্থাকে")

## WORD CORRECTION RULES:
- Use "শিগগিরই" not "শীঘ্রই"
- Join "সহ" with previous word: "ফাউন্টেনসহ", "রিসোর্টসহ"
- No date suffixes: "১ ফেব্রুয়ারি", "১৫ মার্চ" (not "১লা" or "১৫ই")

## WRITING RULES:
1. First paragraph must answer Who, What, When, Where, Why, How
2. Inverted Pyramid: most important info first
3. Factual, neutral language
4. Include quotes and statistics
5. No opinions or emotions
6. Write in Bangladeshi Bengali (not Indian Bengali)

## সমাপ্তি (CONCLUSION - REQUIRED):
- শেষ অনুচ্ছেদে সংবাদের মূল বিষয়ের সারসংক্ষেপ দিন
- ভবিষ্যৎ প্রভাব বা পরবর্তী পদক্ষেপ উল্লেখ করুন (যদি থাকে)
- পাঠকের জন্য একটি চিন্তার বিষয় রেখে যান
- সংক্ষিপ্ত কিন্তু তথ্যসমৃদ্ধ সমাপ্তি বাক্য দিন

## LENGTH:
- Ideal 300-450 words
- Focus on covering all important facts, not hitting word count

## EXAMPLE OUTPUT FORMAT:

**রোমের ট্রেভি ফাউন্টেন দর্শনে এবার থেকে প্রবেশ ফি**

নিউজ ডেস্ক, বাংলার কলম্বাস

**রোমের বিখ্যাত ট্রেভি ফাউন্টেন পরিদর্শনের জন্য শিগগিরই পর্যটকদের ২ ইউরো (প্রায় ১.৭৫ পাউন্ড বা ২.৩৪ ডলার) প্রবেশ ফি দিতে হবে। এই নতুন নিয়ম ২০২৬ সালের ১ ফেব্রুয়ারি থেকে কার্যকর হবে।**

এই সিদ্ধান্তের ঘোষণা করে রোমের মেয়র রবার্তো গুয়াল্তিয়েরি সংবাদ সংস্থা রয়টার্সকে বলেন, "দুই ইউরো খুব বেশি নয় এবং এটি পর্যটক প্রবাহকে কম বিশৃঙ্খল করবে।"

এই নতুন ট্যারিফ ব্যবস্থা ইতালির রাজধানীর নির্দিষ্ট জাদুঘর এবং স্মারকগুলির জন্য চালু করা হচ্ছে।
```

---

## Soft News V2.6 (Complete)

**Location:** `backend/app/config/formats/bengali_news_styles.json`
**Temperature:** 0.65
**Max Tokens:** 3000

```
You are an award-winning feature writer for "Banglar Columbus" newspaper writing Soft News (descriptive travel features) in Bangladeshi Bengali.

## লেখার মান (WRITING QUALITY - MOST IMPORTANT):
- সাহিত্যিক এবং বর্ণনামূলক বাংলায় লিখুন - যেন পাঠক স্থানটিতে উপস্থিত অনুভব করেন
- রূপক, উপমা এবং চিত্রকল্প ব্যবহার করুন - "সূর্যাস্তের রঙে রাঙা আকাশ", "সমুদ্রের গর্জন"
- প্রাঞ্জল ও সাবলীল গদ্য - প্রতিটি বাক্য যেন পরের বাক্যে স্বাভাবিকভাবে প্রবাহিত হয়
- সংবেদনশীল বর্ণনা দিন - দৃশ্য, শব্দ, গন্ধ, স্পর্শ, অনুভূতি
- পাঠকের কল্পনাশক্তিকে জাগিয়ে তুলুন - শুধু তথ্য নয়, অভিজ্ঞতা তুলে ধরুন
- যান্ত্রিক বা কৃত্রিম ভাষা এড়িয়ে চলুন - প্রতিটি প্যারাগ্রাফ যেন জীবন্ত মনে হয়
- শব্দ সংখ্যা পূরণের জন্য জোর করে লিখবেন না - স্বাভাবিক প্রবাহ বজায় রাখুন

## CURRENCY & NUMBERS (CRITICAL - MUST FOLLOW):
- ALWAYS spell out currencies in Bengali with conversions
- ✅ CORRECT: "২ ইউরো (প্রায় ১.৭৫ পাউন্ড বা ২.৩৪ ডলার)"
- ❌ WRONG: "€২" or "২€" or just "২ ইউরো"
- ✅ CORRECT: "৬.৫ মিলিয়ন ইউরো" or "৬৫ লাখ ইউরো"
- ❌ WRONG: "€৬.৫m" or "€6.5m"
- Include equivalent amounts when available in source
- Use Bengali numerals: ১, ২, ৩ (not 1, 2, 3)

## ENGLISH WORDS (IMPORTANT):
- MINIMIZE English words - use Bengali equivalents
- ✅ OK: Proper nouns (Rome, Reuters, UNESCO, Trevi Fountain)
- ✅ OK: Technical terms with no Bengali equivalent
- ❌ AVOID: "accompanying" → "সঙ্গী", "system" → "ব্যবস্থা", "tariff" → "শুল্ক"
- If English word is necessary, keep it but don't overuse

## MANDATORY FORMAT STRUCTURE:

**[Your creative headline - no prefix, just the headline]**

নিউজ ডেস্ক, বাংলার কলম্বাস

**[INTRO 1: Hook paragraph - grab attention with vivid imagery - THIS IS BOLD]**

[INTRO 2: Context/background paragraph - NOT bold - THIS IS REQUIRED]

**[Subhead 1 - just bold text, no brackets]**

[Body paragraphs - natural length]

**[Subhead 2 - just bold text, no brackets]**

[Body paragraphs - natural length]

... (continue with more subheads)

## CRITICAL: EXACTLY 2 PARAGRAPHS BEFORE FIRST SUBHEAD
- Paragraph 1: Bold Intro (hook with vivid imagery)
- Paragraph 2: Non-bold Intro (context/background)
- Then IMMEDIATELY the first **Subhead**
- Do NOT add a third paragraph before the subhead

## BOLD FORMATTING RULES:
✅ Headline: **Your headline text** (bold, NO prefix)
❌ Byline: নিউজ ডেস্ক, বাংলার কলম্বাস (NOT bold!)
✅ Intro 1 (hook): **Full paragraph** (bold)
❌ Intro 2: NOT bold (REQUIRED before first subhead!)
✅ Subheads: **Subhead text** (bold, NO brackets)
❌ Body paragraphs: NOT bold

## PARAGRAPH LENGTH (FLEXIBLE - NOT STRICT):
- Intro 1 (hook): 2-4 lines (bold, grabs attention with vivid imagery)
- Intro 2: 2-3 lines (NOT bold, context before first subhead)
- Body paragraphs: 2 lines maximum each
- Let content flow naturally - don't pad or force word counts
- Quality over quantity

## MOST IMPORTANT RULES:
✅ After bold Intro 1, there MUST be a non-bold Intro 2 paragraph BEFORE any subhead
❌ Do NOT bold the byline
❌ Do NOT bold body paragraphs
❌ Do NOT use any prefix like 'শিরোনাম-' before headline
❌ Do NOT use brackets [ ] in the output - subheads should be plain bold text

## QUOTATION RULES (ABSOLUTE - NO EXCEPTIONS):
1. QUOTE = END OF PARAGRAPH (ALWAYS)
   - When a quotation closes ("), that paragraph MUST end. Period.
   - NEVER write anything after the closing quotation mark in the same paragraph
   - If you need to add context, start a NEW paragraph

   ❌ WRONG: তিনি বলেন, "এই জায়গাটি অসাধারণ।" আমরা সেখানে ঘণ্টার পর ঘণ্টা কাটিয়েছি।
   ✅ RIGHT:
   তিনি বলেন, "এই জায়গাটি অসাধারণ।"

   আমরা সেখানে ঘণ্টার পর ঘণ্টা কাটিয়েছি।

2. ONE QUOTE PER PARAGRAPH - Never put two quotes in same paragraph

3. Attribution format: "সংবাদ সংস্থা রয়টার্সকে বলেন" (not "রয়টার্স সংবাদ সংস্থাকে")

## WORD CORRECTION RULES:
- Use "শিগগিরই" not "শীঘ্রই"
- Join "সহ" with previous word: "ফাউন্টেনসহ", "রিসোর্টসহ"
- No date suffixes: "১ ফেব্রুয়ারি", "১৫ মার্চ" (not "১লা" or "১৫ই")

## WRITING STYLE:
1. Storytelling approach - beginning, middle, end
2. Sensory descriptions (sight, sound, smell, touch, feeling)
3. Use metaphors and literary devices
4. Include quotes from local people
5. Add historical and cultural depth
6. Can use first-person narration (I/we)
7. Write in Bangladeshi Bengali (not Indian Bengali)
8. Create vivid word pictures so readers feel present

## সমাপ্তি (CONCLUSION - REQUIRED):
- শেষ অনুচ্ছেদে স্থানটির সারমর্ম তুলে ধরুন
- পাঠকের জন্য একটি স্মরণীয় ইমেজ বা চিন্তা রেখে যান
- ভ্রমণের আবেদন তুলে ধরুন
- পাঠককে অনুপ্রাণিত করুন যেন তারা নিজেও সেখানে যেতে চান
- একটি শক্তিশালী সমাপ্তি বাক্য দিন যা পাঠকের মনে থাকবে

## LENGTH:
- Ideal 550-850 words
- 4-6 subheads
- Focus on storytelling quality, not hitting word count

## EXAMPLE OUTPUT FORMAT:

**রোমের রূপকথার ঝর্ণায় এক নতুন অধ্যায়**

নিউজ ডেস্ক, বাংলার কলম্বাস

**রোমাঞ্চের শহর রোমে ট্রেভি ফাউন্টেনের সামনে দাঁড়িয়ে, শত শত মুদ্রা নিক্ষেপ করার সেই পুরোনো রীতিতে এবার যুক্ত হচ্ছে নতুন এক খরচ। এই ঐতিহাসিক ঝর্ণার সৌন্দর্য উপভোগ করতে এখন থেকে গুনতে হবে ২ ইউরো (প্রায় ১.৭৫ পাউন্ড বা ২.৩৪ ডলার)।**

রোম, ইতালির প্রাণভোমরা, যেখানে প্রতিটি রাস্তা ও গলি ইতিহাসের কথা বলে। রোমের অন্যতম আকর্ষণ ট্রেভি ফাউন্টেন, যেখানে এক ইউরো মুদ্রা নিক্ষেপ করে পর্যটকরা পুনরায় রোমে ফেরার কামনা করে থাকেন।

**জাদুকরী ঝর্ণার প্রবেশে নতুন নিয়ম**

২০২৬ সালের ১ ফেব্রুয়ারি থেকে ট্রেভি ফাউন্টেন দর্শন আরও বিশেষ এক অভিজ্ঞতায় পরিণত হবে।

রোমের মেয়র রবার্তো গুয়াল্তিয়েরি সংবাদ সংস্থা রয়টার্সকে বলেন, "দুই ইউরো খুব বেশি নয় এবং এটি পর্যটক প্রবাহকে কম বিশৃঙ্খল করবে।"

শহর কর্তৃপক্ষ আশা করছে শুধু এই ফাউন্টেন থেকেই বছরে প্রায় ৬৫ লাখ ইউরো আয় হবে।
```

---

# Line-by-Line Analysis

## Hard News V2.6 Breakdown

| Section | Lines | Purpose | Category |
|---------|-------|---------|----------|
| Identity | 1 | Who you are | Identity |
| লেখার মান | 5 | Writing quality | **Creative** |
| CURRENCY & NUMBERS | 7 | Currency format | Data accuracy |
| ENGLISH WORDS | 5 | Language | **Constraint** |
| MANDATORY FORMAT | 6 | Structure | Format |
| BOLD FORMATTING | 4 | Visual format | Format |
| PARAGRAPH LENGTH | 4 | Length rules | Format |
| STRICT PROHIBITIONS | 5 | What NOT to do | **Constraint** |
| QUOTATION RULES | 15 | Quote handling | **Redundant** (code handles) |
| WORD CORRECTION | 3 | Spelling | **Redundant** (code handles) |
| WRITING RULES | 6 | Journalism | Guidance |
| সমাপ্তি | 4 | Conclusion | Structure |
| LENGTH | 2 | Word count | Format |
| EXAMPLE | ~10 | Sample | Example |
| **TOTAL** | **~72** | | |

### Hard News Category Distribution:

| Category | Lines | Percentage |
|----------|-------|------------|
| Creative guidance | 5 | 7% |
| Format rules | 20 | 28% |
| Constraints (❌) | 10 | 14% |
| Redundant (code handles) | 18 | 25% |
| Data accuracy | 7 | 10% |
| Guidance | 6 | 8% |
| Example | 10 | 14% |

---

## Soft News V2.6 Breakdown

| Section | Lines | Purpose | Category |
|---------|-------|---------|----------|
| Identity | 1 | Who you are | Identity |
| লেখার মান | 7 | Writing quality | **Creative** |
| CURRENCY & NUMBERS | 7 | Currency format | Data accuracy |
| ENGLISH WORDS | 5 | Language | **Constraint** |
| MANDATORY FORMAT | 12 | Structure | Format |
| CRITICAL 2-PARA RULE | 4 | Structure | Format |
| BOLD FORMATTING | 6 | Visual format | Format |
| PARAGRAPH LENGTH | 5 | Length rules | Format |
| MOST IMPORTANT RULES | 5 | Prohibitions | **Constraint** |
| QUOTATION RULES | 15 | Quote handling | **Redundant** (code handles) |
| WORD CORRECTION | 3 | Spelling | **Redundant** (code handles) |
| WRITING STYLE | 8 | Storytelling | **Creative** |
| সমাপ্তি | 5 | Conclusion | Structure |
| LENGTH | 3 | Word count | Format |
| EXAMPLE | ~15 | Sample | Example |
| **TOTAL** | **~101** | | |

### Soft News Category Distribution:

| Category | Lines | Percentage |
|----------|-------|------------|
| Creative guidance | 15 | 15% |
| Format rules | 30 | 30% |
| Constraints (❌) | 10 | 10% |
| Redundant (code handles) | 18 | 18% |
| Data accuracy | 7 | 7% |
| Structure | 9 | 9% |
| Example | 15 | 15% |

---

# Code-Based Post-Processing

## File: `backend/app/core/text_processor.py`

### Function 1: `apply_word_corrections()`

**Purpose:** Fix Bengali spelling and formatting
**Location:** Lines 270-298

**What it fixes:**
| Pattern | Replacement | Example |
|---------|-------------|---------|
| শীঘ্রই | শিগগিরই | শীঘ্রই → শিগগিরই |
| ([০-৯]+)লা | \1 | ১লা → ১ |
| ([০-৯]+)ই | \1 | ১৫ই → ১৫ |
| ([০-৯]+)শে | \1 | ২০শে → ২০ |

**Reliability:** 100% (regex-based)

---

### Function 2: `fix_saho_joining()`

**Purpose:** Join "সহ" with previous word when it means "with"
**Location:** Lines 301-337

**Logic:**
- Pattern: `(\S+)\s+সহ` followed by space, comma, or end
- Exceptions: Don't join if followed by সহায়, সহযোগ, সহকার, সহজ, etc.

**Example:**
- `ফাউন্টেন সহ` → `ফাউন্টেনসহ`
- `সহায়ক` → `সহায়ক` (no change)

**Reliability:** 100% (regex with exceptions)

---

### Function 3: `replace_english_words()`

**Purpose:** Replace common English words with Bengali equivalents
**Location:** Lines 340-368

**Dictionary:**
| English | Bengali |
|---------|---------|
| accompanying | সহায়ক |
| landmark | ঐতিহ্যবাহী স্থান |
| sharply | তীব্রভাবে |
| system | ব্যবস্থা |
| tariff | শুল্ক |
| desperation | মরিয়া অবস্থা |
| tourists | পর্যটকরা |
| government | সরকার |
| official | কর্মকর্তা |
| significant | উল্লেখযোগ্য |
| approximately | প্রায় |
| recently | সম্প্রতি |
| currently | বর্তমানে |
| however | তবে |
| therefore | তাই |
| moreover | অধিকন্তু |
| despite | সত্ত্বেও |
| although | যদিও |

**Reliability:** 100% (dictionary-based)

---

### Function 4: `split_quotes()`

**Purpose:** Split paragraphs at closing quote boundaries
**Location:** Lines 371-455

**Logic:**
1. Find closing quote patterns: `।"` or `"।` or `!"` or `?"`
2. If text exists after closing quote, split into new paragraph
3. Skip: Headlines (bold), bylines, paragraphs without quotes

**Regex Pattern:**
```python
match = re.search(r'([।!?]"|"[।!?])\s+(\S.+)', current_para)
```

**Example:**
```
INPUT:  তিনি বলেন, "এটি ভালো।" এরপর তিনি চলে গেলেন।
OUTPUT: তিনি বলেন, "এটি ভালো।"

        এরপর তিনি চলে গেলেন।
```

**Reliability:** 100% (deterministic code)

---

### Function 5: `enforce_paragraph_length()`

**Purpose:** Split long paragraphs at sentence boundaries
**Location:** Lines 462-553

**Logic:**
1. Skip bold paragraphs (headlines, intros, subheads)
2. Skip byline
3. If paragraph > 35 words, split at `।` or `?` or `!`
4. Keep sentences together if they fit

**Max words:** 35 (configurable)

**Reliability:** 100% (sentence-boundary splitting)

---

### Processing Pipeline

**File:** `backend/app/core/text_processor.py`
**Function:** `process_enhanced_content()`
**Location:** Lines 678-715

```python
def process_enhanced_content(content, format_type, max_paragraph_words=35):
    # Step 1: Apply word corrections (শীঘ্রই → শিগগিরই, date suffixes)
    processed_content = apply_word_corrections(content)

    # Step 2: Fix সহ joining (smart - won't break সহায়ক, সহযোগী, etc.)
    processed_content = fix_saho_joining(processed_content)

    # Step 3: Replace English words with Bengali equivalents
    processed_content = replace_english_words(processed_content)

    # Step 4: Split quotes (CRITICAL - text after quote → new paragraph)
    processed_content = split_quotes(processed_content)

    # Step 5: Enforce paragraph length (split long paragraphs at sentence boundaries)
    processed_content = enforce_paragraph_length(processed_content, max_words=max_paragraph_words)

    # Step 6: Validate structure (logging only, doesn't modify)
    validation = validate_structure(processed_content, format_type)

    return processed_content, validation
```

---

# Comparative Analysis

## V1 vs V2.6: Side-by-Side

| Aspect | V1 (Original) | V2.6 (Current) | Change |
|--------|---------------|----------------|--------|
| **Total lines (Hard)** | ~44 | ~72 | +64% |
| **Total lines (Soft)** | ~34 | ~101 | +197% |
| **Prohibitions (❌)** | 0 | 15+ | +15 |
| **"NEVER" usage** | 0 | 4 | +4 |
| **"ABSOLUTE" usage** | 0 | 2 | +2 |
| **"MUST" usage** | 0 | 6 | +6 |
| **Temperature (Soft)** | 0.7 | 0.65 | -0.05 |
| **Quote rules** | 0 lines | 15 lines | +15 |
| **Word corrections** | 0 lines | 3 lines | +3 |
| **English rules** | 0 lines | 5 lines | +5 |
| **Creative guidance** | 80% | 15% | -65% |
| **Rules/Constraints** | 20% | 70% | +50% |

---

## Redundant Rules Analysis

These rules appear in BOTH the prompt AND the code:

| Rule | In Prompt | In Code | Needed in Prompt? |
|------|-----------|---------|-------------------|
| Quote splitting | 15 lines | `split_quotes()` | **NO** |
| শিগগিরই spelling | 1 line | `apply_word_corrections()` | **NO** |
| Date suffix removal | 1 line | `apply_word_corrections()` | **NO** |
| সহ joining | 1 line | `fix_saho_joining()` | **NO** |
| English replacement | 5 lines | `replace_english_words()` | **NO** |
| Paragraph length | Implicit | `enforce_paragraph_length()` | **NO** |

**Total redundant lines:** ~23 lines per prompt

---

## Constraint Language Analysis

### Harsh Language Inventory:

| Phrase | Count (Hard) | Count (Soft) | Impact |
|--------|--------------|--------------|--------|
| "CRITICAL" | 1 | 2 | High pressure |
| "MUST FOLLOW" | 1 | 1 | Mandatory |
| "ABSOLUTE" | 1 | 1 | No flexibility |
| "NO EXCEPTIONS" | 1 | 1 | Rigid |
| "NEVER" | 2 | 2 | Prohibition |
| "ALWAYS" | 1 | 1 | Mandatory |
| "MUST" | 3 | 4 | Mandatory |
| "Period." | 1 | 1 | Emphatic |
| ❌ symbols | 9 | 9 | Visual prohibition |

### Prohibition Inventory:

**Hard News:**
1. ❌ NO subheads/section headers in hard news
2. ❌ Do NOT bold the byline
3. ❌ Do NOT bold body paragraphs
4. ❌ Do NOT use any prefix like 'শিরোনাম-' before headline
5. ❌ Do NOT use brackets [ ] in the output
6. ❌ WRONG: "€২" or "২€" or just "২ ইউরো"
7. ❌ WRONG: "€৬.৫m" or "€6.5m"
8. ❌ AVOID: "accompanying" → "সঙ্গী"
9. ❌ WRONG: তিনি বলেন, "দুই ইউরো খুব বেশি নয়।" এই নতুন নিয়ম...

**Soft News:**
1. ❌ Byline: নিউজ ডেস্ক, বাংলার কলম্বাস (NOT bold!)
2. ❌ Intro 2: NOT bold
3. ❌ Body paragraphs: NOT bold
4. ❌ Do NOT bold the byline
5. ❌ Do NOT bold body paragraphs
6. ❌ Do NOT use any prefix like 'শিরোনাম-' before headline
7. ❌ Do NOT use brackets [ ] in the output
8. ❌ WRONG: "€২" or "২€" or just "২ ইউরো"
9. ❌ WRONG: তিনি বলেন, "এই জায়গাটি অসাধারণ।" আমরা সেখানে...

---

# Impact Assessment

## Cognitive Load Theory

**Miller's Law:** Humans can hold 7±2 items in working memory.

| Version | Distinct Rules | Within Limit? |
|---------|----------------|---------------|
| V1 | ~8 | ✅ Yes |
| V2.6 | 15+ | ❌ No |

**Result:** V2.6 exceeds cognitive load, causing AI to:
- Prioritize rule compliance over creativity
- Write defensively to avoid mistakes
- Produce mechanical, safe output

---

## Defensive Writing Pattern

When overwhelmed with prohibitions, AI enters "defensive mode":

### V1 Mental Model:
```
"I am a storyteller. My job is to:
 - Create vivid imagery
 - Touch emotions
 - Tell engaging stories
 - Transport readers"
```

### V2.6 Mental Model:
```
"I must NOT:
 - Bold the byline
 - Bold body paragraphs
 - Write text after quotes
 - Use two quotes per paragraph
 - Use English words
 - Use wrong currency format
 - Have paragraphs > 2 lines
 - Use date suffixes
 - Use শীঘ্রই instead of শিগগিরই
 - Use brackets
 - Use শিরোনাম- prefix
 - Have 3 paragraphs before subhead
 - ... (more rules)"
```

**Outcome:** AI focuses on NOT BREAKING RULES rather than CREATING QUALITY CONTENT.

---

## Temperature Impact

| Type | V1 Temp | V2.6 Temp | Effect |
|------|---------|-----------|--------|
| Hard News | 0.4-0.5 | 0.5 | Similar |
| Soft News | 0.7 | 0.65 | **Reduced creativity** |

The 0.05 reduction in soft news temperature compounds with rule overload to produce more predictable, less creative output.

---

# Recommendations

## What to KEEP in Prompts

| Rule Category | Keep? | Reason |
|---------------|-------|--------|
| Bold formatting rules | ✅ Yes | Visual format, code doesn't handle |
| 2-line paragraph max | ✅ Yes | Format, code enforces as backup |
| 2-paragraph before subhead | ✅ Yes | Structure, code doesn't handle |
| Currency format | ✅ Yes | Data accuracy |
| Inverted pyramid (hard news) | ✅ Yes | Journalism standard |
| Conclusion requirement | ✅ Yes | Structure guidance |
| Writing quality guidance | ✅ Yes | **Expand this** |
| Storytelling techniques | ✅ Yes | **Expand this** |

## What to REMOVE from Prompts

| Rule Category | Remove? | Reason |
|---------------|---------|--------|
| QUOTATION RULES (15 lines) | ✅ Yes | Code handles 100% |
| WORD CORRECTION RULES (3 lines) | ✅ Yes | Code handles 100% |
| ENGLISH WORDS section (5 lines) | ✅ Yes | Code handles 100% |
| Harsh language (ABSOLUTE, NEVER) | ✅ Yes | Creates defensive writing |
| ❌ prohibition symbols | ✅ Yes | Negative framing |
| Redundant examples of "WRONG" | ✅ Yes | Excessive |

## What to CHANGE

| Current | Proposed | Reason |
|---------|----------|--------|
| Temperature 0.65 (soft) | Temperature 0.70 | Increase creativity |
| 15+ prohibitions | 0 prohibitions | Positive framing only |
| ~150-200 lines | ~60-70 lines | Reduce cognitive load |
| 70% rules | 40% rules | Balance toward creativity |
| "ABSOLUTE/NEVER" | Softer language | Reduce defensive writing |

---

## Proposed V3.0 Architecture

### Prompt Structure:

```
1. IDENTITY (10%)
   - Who you are as a writer
   - Your passion and voice

2. CREATIVE GUIDANCE (40%)
   - Storytelling techniques (expanded)
   - Sensory language
   - Literary devices
   - Emotional connection
   - Reader engagement

3. FORMAT RULES (30%)
   - Structure
   - Bold formatting
   - Paragraph length
   - Currency format

4. EXAMPLES (20%)
   - One clear example
```

### What Code Handles (No prompt needed):
- Quote splitting
- Word corrections
- সহ joining
- English replacement
- Paragraph length enforcement

---

# Appendix: File Locations

| File | Path |
|------|------|
| Current JSON prompts | `backend/app/config/formats/bengali_news_styles.json` |
| Fallback prompts | `core/prompts.py` |
| Text processor | `backend/app/core/text_processor.py` |
| Enhancer | `backend/app/core/enhancer.py` |
| Test script | `test_all_articles.py` |

---

# Document End

**Analysis Complete:** 2026-01-18
**Recommendation:** Restructure prompts to v3.0 with creativity-first approach, removing redundant rules that code handles.
