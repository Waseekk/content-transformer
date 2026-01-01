# Complete Swagger UI Testing Guide

## Prerequisites
✅ Server running on http://127.0.0.1:8500
✅ Test user exists: test@example.com / Test1234
✅ Database: test_fresh.db

---

## PART 1: AUTHORIZATION (Do This First!)

### Step 1: Open Swagger UI
```
http://127.0.0.1:8500/docs
```

### Step 2: Authorize
1. Click the green **"Authorize"** button (top right)
2. Fill in:
   - **username:** `test@example.com` (your email)
   - **password:** `Test1234`
3. Leave **client_id** and **client_secret** empty
4. Click **"Authorize"** button
5. Click **"Close"**

**✅ You're now authorized!** All 🔒 locks should turn to 🔓

---

## PART 2: TEST AUTHENTICATION ENDPOINTS (0 tokens)

### Test 1: Get User Profile
**Endpoint:** `GET /api/auth/me`

**Steps:**
1. Expand **GET /api/auth/me**
2. Click **"Try it out"**
3. Click **"Execute"**

**Expected Response (200):**
```json
{
  "id": 1,
  "email": "test@example.com",
  "full_name": "Test User",
  "subscription_tier": "free",
  "tokens_remaining": 5000,
  "tokens_used": 0
}
```

---

### Test 2: Check Token Balance
**Endpoint:** `GET /api/auth/token-balance`

**Steps:**
1. Expand **GET /api/auth/token-balance**
2. Click **"Try it out"**
3. Click **"Execute"**

**Expected Response (200):**
```json
{
  "tokens_remaining": 5000,
  "tokens_used": 0,
  "monthly_token_limit": 5000,
  "subscription_tier": "free",
  "subscription_status": "active",
  "reset_date": "2026-01-01"
}
```

---

### Test 3: Get Usage Statistics
**Endpoint:** `GET /api/auth/usage-stats`

**Steps:**
1. Expand **GET /api/auth/usage-stats**
2. Click **"Try it out"**
3. Click **"Execute"**

**Expected Response (200):**
```json
{
  "total_translations": 0,
  "total_enhancements": 0,
  "tokens_used_this_month": 0,
  "tokens_remaining": 5000
}
```

---

## PART 3: TEST TRANSLATION ENDPOINTS (Uses tokens!)

### Test 4: Translate Raw Text
**Endpoint:** `POST /api/translate/translate-text`

**⚠️ WARNING: This uses ~500-1000 tokens**

**Steps:**
1. Expand **POST /api/translate/translate-text**
2. Click **"Try it out"**
3. Edit the request body:
```json
{
  "text": "The Maldives is a tropical paradise located in the Indian Ocean. Known for its crystal-clear turquoise waters, white sandy beaches, and vibrant coral reefs. This stunning archipelago consists of 26 atolls and over 1,000 coral islands.",
  "title": "Maldives Travel Guide",
  "save_to_history": true
}
```
4. Click **"Execute"**

**Expected Response (201):**
```json
{
  "id": 1,
  "original_title": "Maldives Travel Guide",
  "original_text": "The Maldives is a tropical paradise...",
  "translated_text": "মালদ্বীপ একটি গ্রীষ্মমন্ডলীয় স্বর্গ...",
  "tokens_used": 500,
  "tokens_remaining": 4500
}
```

---

### Test 5: Get Translation History
**Endpoint:** `GET /api/translate/`

**Steps:**
1. Expand **GET /api/translate/**
2. Click **"Try it out"**
3. Set parameters:
   - page: 1
   - page_size: 10
4. Click **"Execute"**

**Expected Response (200):**
```json
{
  "translations": [
    {
      "id": 1,
      "original_title": "Maldives Travel Guide",
      "tokens_used": 500,
      "created_at": "2025-12-21T..."
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10
}
```

---

### Test 6: Get Specific Translation
**Endpoint:** `GET /api/translate/{translation_id}`

**Steps:**
1. Expand **GET /api/translate/{translation_id}**
2. Click **"Try it out"**
3. Enter **translation_id:** `1` (from previous test)
4. Click **"Execute"**

**Expected Response (200):**
```json
{
  "id": 1,
  "original_title": "Maldives Travel Guide",
  "original_text": "The Maldives is a tropical paradise...",
  "translated_text": "মালদ্বীপ একটি গ্রীষ্মমন্ডলীয় স্বর্গ...",
  "tokens_used": 500
}
```

---

## PART 4: TEST ENHANCEMENT ENDPOINTS (Uses tokens!)

### Test 7: Get Available Formats
**Endpoint:** `GET /api/enhance/formats`

**Steps:**
1. Expand **GET /api/enhance/formats**
2. Click **"Try it out"**
3. Click **"Execute"**

**Expected Response (200):**
```json
{
  "user_tier": "free",
  "available_formats": [
    {
      "format_type": "hard_news",
      "name": "Hard News",
      "description": "Professional news reporting style",
      "tier_required": "free"
    }
  ]
}
```

---

### Test 8: Generate Enhanced Content
**Endpoint:** `POST /api/enhance/`

**⚠️ WARNING: This uses ~500-1000 tokens per format**

**Steps:**
1. Expand **POST /api/enhance/**
2. Click **"Try it out"**
3. Edit the request body:
```json
{
  "text": "মালদ্বীপ একটি গ্রীষ্মমন্ডলীয় স্বর্গ যা ভারত মহাসাগরে অবস্থিত। স্ফটিক-স্বচ্ছ ফিরোজা জল, সাদা বালুকাময় সৈকত এবং প্রাণবন্ত প্রবাল প্রাচীরের জন্য পরিচিত।",
  "headline": "মালদ্বীপ ভ্রমণ গাইড",
  "formats": ["hard_news"]
}
```
4. Click **"Execute"**

**Expected Response (201):**
```json
{
  "id": 1,
  "formats": [
    {
      "id": 1,
      "format_type": "hard_news",
      "headline": "মালদ্বীপ: ভারত মহাসাগরের গ্রীষ্মমন্ডলীয় স্বর্গ",
      "content": "...generated content...",
      "tokens_used": 500
    }
  ],
  "total_tokens_used": 500,
  "tokens_remaining": 4000
}
```

---

### Test 9: Get Enhancement History
**Endpoint:** `GET /api/enhance/`

**Steps:**
1. Expand **GET /api/enhance/**
2. Click **"Try it out"**
3. Set parameters:
   - page: 1
   - page_size: 10
4. Click **"Execute"**

**Expected Response (200):**
```json
{
  "enhancements": [
    {
      "id": 1,
      "format_type": "hard_news",
      "headline": "মালদ্বীপ ভ্রমণ গাইড",
      "tokens_used": 500
    }
  ],
  "total": 1
}
```

---

## PART 5: ADVANCED TESTS (High token usage!)

### Test 10: Extract and Translate from URL
**Endpoint:** `POST /api/translate/extract-and-translate`

**⚠️⚠️ WARNING: This uses ~1000-3000 tokens**

**Steps:**
1. Expand **POST /api/translate/extract-and-translate**
2. Click **"Try it out"**
3. Edit the request body:
```json
{
  "url": "https://www.bbc.com/travel/article/20251209-the-20-best-places-to-travel-in-2026",
  "extraction_method": "auto",
  "save_to_history": true
}
```
4. Click **"Execute"**

**Expected Response (201):**
```json
{
  "id": 2,
  "original_url": "https://www.bbc.com/travel/article/...",
  "original_text": "...extracted content...",
  "translated_text": "...Bengali translation...",
  "extraction_method": "trafilatura",
  "tokens_used": 1500,
  "tokens_remaining": 2500
}
```

---

## TESTING CHECKLIST

### ✅ Part 1: Auth (0 tokens)
- [ ] Get user profile
- [ ] Check token balance
- [ ] Get usage statistics

### ✅ Part 2: Translation (Uses tokens!)
- [ ] Translate raw text (~500 tokens) ⚠️
- [ ] Get translation history (0 tokens)
- [ ] Get specific translation (0 tokens)

### ✅ Part 3: Enhancement (Uses tokens!)
- [ ] Get available formats (0 tokens)
- [ ] Generate hard_news format (~500 tokens) ⚠️
- [ ] Get enhancement history (0 tokens)

### ✅ Part 4: Advanced (High token usage!)
- [ ] Extract from URL and translate (~1500 tokens) ⚠️⚠️

---

## RECOMMENDED TESTING ORDER

**Follow this order to avoid running out of tokens:**

1. ✅ **Auth endpoints** (all free)
2. ✅ **Get available formats** (free)
3. ✅ **Translation history** (free, will be empty)
4. ⚠️ **Translate ONE text** (uses ~500 tokens)
5. ✅ **Check token balance** (verify deduction)
6. ⚠️ **Generate ONE format** (uses ~500 tokens)
7. ✅ **Enhancement history** (see your results)
8. ⚠️⚠️ **URL extraction** (ONLY if you have 1500+ tokens left)

---

## TOKEN BUDGET PLANNING

**You have 5,000 tokens to test with:**

| Operation | Token Cost | Max Times |
|-----------|------------|-----------|
| Translate text | ~500 | 10 times |
| Extract from URL | ~1500 | 3 times |
| Generate hard_news | ~500 | 10 times |

**Smart testing approach:**
- Test 2-3 translations (1500 tokens)
- Test 2-3 enhancements (1500 tokens)
- Test 1 URL extraction (1500 tokens)
- Keep 1500 tokens for future testing

---

## COMMON ERRORS & FIXES

### 401 Unauthorized
**Error:** "Not authenticated"
**Fix:** Click "Authorize" button and enter credentials

### 402 Payment Required
**Error:** "Insufficient tokens"
**Fix:** Reset tokens in database:
```bash
cd backend
sqlite3 test_fresh.db
UPDATE users SET tokens_remaining = 5000, tokens_used = 0 WHERE email = 'test@example.com';
.quit
```

### 403 Forbidden
**Error:** "Format not available for your tier"
**Fix:** Free tier only has hard_news format

### 500 Internal Server Error
**Error:** Server error
**Fix:** Check server logs, might be OpenAI API key issue

---

## TIPS

### 💡 Monitoring Token Usage
After each token-consuming test, check your balance:
```
GET /api/auth/token-balance
```

### 💡 Workflow Tip
The natural workflow is:
1. **Translate** content to Bengali
2. **Enhance** the translated content to multiple formats
3. This is why translation comes before enhancement!

---

**🎉 Happy Testing!**

All bugs fixed! Translation endpoints now work correctly.
