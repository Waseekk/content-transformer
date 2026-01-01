# Keyword Search Feature - Implementation Guide

**Status:** Ready for implementation
**Branch:** master
**For:** Next Claude conversation

---

## 🎯 Objective

Add a **Keyword Search** tab that uses Playwright MCP to search Bengali news sites (Prothom Alo + Daily Star) based on user keywords, then auto-translate and enhance found articles.

---

## 📋 Requirements Recap

### User Flow
1. User enters keywords (e.g., "রোহিঙ্গা", "Rohingya crisis")
2. System searches Prothom Alo and Daily Star
3. Extracts matching articles
4. Auto-translates to Bengali (if English)
5. Auto-enhances to Hard & Soft News formats
6. Displays in editable markdown editor

### Technical Requirements
- Use Playwright MCP (already integrated: `.mcp.json` exists)
- Search both Bangla and English content
- Target sites: Prothom Alo, Daily Star (configured in `sites_config.json`)
- Integrate with existing translation & enhancement pipeline
- Use ReviewAgent for quality checking

---

## 🗂️ Current Project State

### ✅ What's Already Done

**Files Modified:**
- `app.py` - Formats limited to Hard/Soft News, markdown editor added, review agent integrated
- `config/sites_config.json` - Prothom Alo & Daily Star added
- `core/review_agent.py` - Quality checking agent (NEW)
- `.gitignore` - Excludes .md/.bat files

**Features Working:**
- ✅ Hard News & Soft News formats only
- ✅ Editable markdown editor with preview
- ✅ Copy/Download functionality
- ✅ ReviewAgent auto-reviews enhanced content
- ✅ Token tracking for enhancement + review
- ✅ Bengali news sites in config

**Git Status:**
- Current branch: `master`
- Latest commit: `96d15d4` - "feat: newspaper-focused enhancements with review agent"
- Pushed to GitHub: ✅

**Branches:**
- `master` - Full project (Streamlit + Backend)
- `streamlit-cloud` - Streamlit only (no backend)

---

## 🛠️ Implementation Steps

### Step 1: Create Keyword Search Module

**File:** `core/keyword_search.py`

**Features needed:**
```python
class KeywordSearch:
    def __init__(self, playwright_mcp):
        # Initialize Playwright MCP

    def search_site(self, site_name, keyword, language='bn'):
        # Search Prothom Alo or Daily Star
        # Return: list of article URLs + headlines

    def extract_article(self, url):
        # Extract full article content from URL
        # Return: dict with headline, content, date, author

    def search_all_sites(self, keyword):
        # Search all configured sites
        # Return: deduplicated results
```

**Playwright MCP Integration:**
- Check `.mcp.json` for server config
- Use MCP to navigate and extract content
- Handle both Bangla and English pages

---

### Step 2: Add 6th Tab to app.py

**Current tabs (line 472):**
```python
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📰 Articles", "🔄 Translate", "📚 History", "📁 Files", "📋 Logs"])
```

**Change to:**
```python
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📰 Articles", "🔄 Translate", "🔍 Keyword Search", "📚 History", "📁 Files", "📋 Logs"])
```

---

### Step 3: Implement Tab Content

**Location:** After line ~1100 (after tab5 Logs section)

**UI Components:**
```python
with tab6:
    st.header("🔍 Keyword Search")
    st.info("Search Bengali newspapers for specific topics")

    # Keyword input
    keyword = st.text_input("Enter keyword (Bangla or English)")

    # Site selection
    sites = st.multiselect("Select sites", ["Prothom Alo", "Daily Star"], default=["Prothom Alo", "Daily Star"])

    # Search button
    if st.button("🔍 Search"):
        # 1. Search sites using Playwright
        # 2. Display results
        # 3. User selects article
        # 4. Auto-translate if needed
        # 5. Auto-enhance to Hard/Soft News
        # 6. Show in markdown editor (reuse existing code)
```

---

### Step 4: Pipeline Integration

**Reuse existing functions:**
- `translate_text_openai()` - For translation
- `enhance_translation()` - For enhancement
- `ReviewAgent` - For quality review
- Markdown editor code (lines 978-1013 in app.py)

**Flow:**
```
Keyword → Search (Playwright) → Extract articles →
Translate (if English) → Enhance (Hard/Soft) →
Review (ReviewAgent) → Display (Markdown editor)
```

---

## 📝 Playwright MCP Details

**MCP Server Info:**
- Config file: `.mcp.json` (exists in project)
- Server: Playwright MCP
- Capabilities: Navigate, extract, interact with web pages

**Usage Pattern:**
```python
# Example (pseudocode)
playwright = get_playwright_mcp()
page = playwright.navigate("https://www.prothomalo.com")
results = page.search(keyword)
for result in results:
    article = playwright.extract_article(result.url)
```

---

## 🧪 Testing Checklist

After implementation:

1. ✅ Can search with Bangla keywords
2. ✅ Can search with English keywords
3. ✅ Finds articles on Prothom Alo
4. ✅ Finds articles on Daily Star
5. ✅ Extracts article content correctly
6. ✅ Translates English articles to Bengali
7. ✅ Enhances to Hard & Soft News formats
8. ✅ ReviewAgent improves content quality
9. ✅ Markdown editor shows editable results
10. ✅ Copy/Download works

---

## 🔗 Related Files to Review

Before starting, review these files:

1. **`app.py`** - Lines 870-1013 (enhancement display)
2. **`core/review_agent.py`** - Review agent implementation
3. **`config/sites_config.json`** - Prothom Alo & Daily Star configs
4. **`.mcp.json`** - Playwright MCP configuration
5. **`core/translator.py`** - Translation logic
6. **`core/enhancer.py`** - Enhancement logic

---

## 💡 Implementation Tips

### For Playwright Integration:
- Use Selenium as reference (sites use `"use_selenium": true`)
- Extract using CSS selectors from `sites_config.json`
- Handle dynamic content loading (wait for elements)

### For Search Logic:
- Simple keyword match in headlines first
- Later: AI-powered semantic search
- Deduplicate by URL

### For Bengali Content:
- Prothom Alo: Already in Bengali (no translation needed)
- Daily Star: English (needs translation to Bengali)
- Use `language` field in config to determine

### For UI/UX:
- Show search progress (like scraper progress bar)
- Display number of results found
- Let user select which articles to enhance
- Show token usage estimate before processing

---

## 🎯 Success Criteria

Feature is complete when:
1. ✅ User can search Prothom Alo & Daily Star
2. ✅ Results show article headlines
3. ✅ User can select articles to process
4. ✅ Auto-translate + enhance works
5. ✅ ReviewAgent improves quality
6. ✅ Results display in editable markdown
7. ✅ All existing features still work

---

## 📊 Estimated Complexity

**Time estimate:** 2-3 hours
**Complexity:** Medium-High
**Dependencies:** Playwright MCP setup

**Why medium-high:**
- Playwright integration (new)
- Two different news sites (different structures)
- Bilingual search (Bangla + English)
- Pipeline integration (translate → enhance → review)

---

## 🚀 Next Steps for New Conversation

**When you start the next conversation, say:**

> "I want to implement the Keyword Search feature. I have KEYWORD_SEARCH_TODO.md with all the details. Let's build it step by step:
> 1. Create keyword_search.py module
> 2. Add 6th tab to app.py
> 3. Integrate Playwright MCP
> 4. Connect to translation & enhancement pipeline
> 5. Test with Prothom Alo and Daily Star"

---

## 📁 Project Structure Reference

```
0. travel_news_/
├── app.py                      # Main Streamlit app (needs tab6 added)
├── .mcp.json                   # Playwright MCP config (exists)
├── config/
│   └── sites_config.json       # Has Prothom Alo & Daily Star ✅
├── core/
│   ├── translator.py           # Translation (reuse) ✅
│   ├── enhancer.py             # Enhancement (reuse) ✅
│   ├── review_agent.py         # Review (reuse) ✅
│   └── keyword_search.py       # NEW - to create
└── backend/                    # Not needed for Streamlit Cloud
```

---

## ✅ Verification Before Starting

Make sure:
1. You're in `master` branch
2. Latest commit is `96d15d4`
3. All previous features work
4. `.mcp.json` exists and is configured

---

**Ready to implement! 🚀**

Pass this document to Claude in the next conversation for seamless continuation.
