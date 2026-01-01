# Travel News SaaS - Complete Testing Guide

**All features are now built and ready to test!** 🎉

---

## 🚀 Quick Start

### Backend Server
- **Status:** ✅ Running
- **URL:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health:** http://localhost:8000/health

### Frontend Server
- **Status:** ✅ Running
- **URL:** http://localhost:5173

---

## 🧪 Step-by-Step Testing Guide

### **1. Authentication Flow** ✅

#### Test Login:
1. Open http://localhost:5173
2. You should see the Login page
3. **Use test credentials:**
   - Email: `test@example.com`
   - Password: `Test1234`
4. Click "Sign In"
5. You should be redirected to Dashboard

#### Test Registration:
1. Click "Sign up" link
2. Fill in the form:
   - Full Name: `Test User`
   - Email: `newuser@example.com`
   - Password: `Test1234Abc`
   - Confirm Password: `Test1234Abc`
3. Click "Create Account"
4. You should see success message
5. Login with the new credentials

#### Test Protected Routes:
1. Logout from dashboard
2. Try to access: http://localhost:5173/dashboard
3. Should redirect to login page ✅

---

### **2. Dashboard** ✅

After login, you should see:

**User Info Card:**
- Welcome message with your name
- Email address
- Subscription tier badge (FREE TIER)
- Token balance (5000 / 5000 Tokens)
- Token usage progress bar

**Features Grid (4 Cards):**
1. 🌐 **Translation** - Blue gradient card
2. ✨ **Enhancement** - Purple gradient card
3. 📰 **Articles** - Green gradient card
4. 🔍 **Scraper** - Orange gradient card

**Quick Stats (3 Cards):**
- Tokens Used: 0
- Account Status: Active
- Member Since: (your join date)

**Click each feature card to test the pages!**

---

### **3. Translation Feature** ✅

**URL:** http://localhost:5173/translation

#### Test Translation from URL:
1. Click "Translation" from dashboard
2. Select "From URL" tab (should be default)
3. Paste a travel article URL, for example:
   ```
   https://www.theguardian.com/travel
   ```
4. Click "Extract & Translate"
5. Wait for processing (uses OpenAI API)
6. **Expected Result:**
   - Green result card appears
   - Shows Bengali headline
   - Shows Bengali translated content
   - Shows tokens used
   - Copy and Download buttons work

#### Test Direct Text Translation:
1. Click "Direct Text" tab
2. Paste some English text:
   ```
   The Maldives is a tropical paradise with crystal-clear waters and beautiful beaches.
   It's the perfect destination for travelers seeking luxury and relaxation.
   ```
3. Click "Translate"
4. **Expected Result:**
   - Same as URL translation
   - Bengali translation appears
   - Tokens deducted from balance

#### Test Features:
- ✅ Copy button - copies translation to clipboard
- ✅ Download button - downloads as .txt file
- ✅ Clear button - resets form

---

### **4. Enhancement Feature** ✅

**URL:** http://localhost:5173/enhancement

#### Test Multi-Format Generation:
1. Click "Enhancement" from dashboard
2. Fill in the form:
   - **Headline:** `মালদ্বীপ ভ্রমণ গাইড`
   - **Bengali Content:** Paste the Bengali translation from step 3
3. Select formats to generate (default: all 6 formats)
   - 📰 Newspaper
   - ✍️ Blog
   - 📘 Facebook
   - 📸 Instagram
   - 📊 Hard News
   - 🎨 Soft News
4. Click "Enhance Content"
5. Wait for processing

**Expected Result:**
- 6 separate result cards appear
- Each with different style/tone:
  - **Newspaper:** Formal, professional
  - **Blog:** Personal, conversational
  - **Facebook:** Social, engaging (100-150 words)
  - **Instagram:** Short caption with hashtags (50-100 words)
  - **Hard News:** BC News style, factual
  - **Soft News:** BC News style, literary
- Each shows token usage
- Copy and Download buttons for each format

#### Test Format Selection:
1. Uncheck some formats
2. Click "Enhance Content"
3. Should only generate selected formats

---

### **5. Articles Browsing** ✅

**URL:** http://localhost:5173/articles

**Note:** You need to run the scraper first to have articles!

#### Test Empty State:
1. Click "Articles" from dashboard
2. If no articles exist:
   - Shows "No articles found"
   - Suggests running scraper

#### Test Article List (after scraping):
1. Articles displayed as cards
2. Each card shows:
   - Source badge
   - Published date
   - Title
   - Content preview (3 lines)
   - "View Original" link
   - Scraped timestamp

#### Test Filtering:
1. **Search:** Type keywords in search box, press Enter
2. **Source Filter:** Select from dropdown (e.g., "The Guardian")
3. **Clear Filters:** Resets all filters

#### Test Pagination:
1. If more than 10 articles:
   - Shows "Previous" and "Next" buttons
   - Shows current page number
   - Navigate between pages

---

### **6. Scraper** ✅

**URL:** http://localhost:5173/scraper

#### Test Scraping:
1. Click "Scraper" from dashboard
2. Click "Start Scraper" button
3. **Expected Behavior:**
   - Button shows "Scraping..." with spinner
   - Status badge appears showing "RUNNING"
   - Progress bar appears and updates
   - Shows current site being scraped
   - Shows article count
   - Shows sites completed/total
   - Updates every 3 seconds

4. **When Complete:**
   - Status changes to "COMPLETED" (green badge)
   - Results card appears showing:
     - Total articles scraped
     - New articles found
     - Number of sites scraped
     - List of recent articles (first 5)

#### Test Error Handling:
1. If no sites configured:
   - Shows error message
   - Suggests checking backend config

---

## 🔄 Complete User Flow Test

**Test the entire workflow:**

1. **Login** → Dashboard shows 5000 tokens
2. **Scraper** → Collect articles (tokens remain same, scraping is free)
3. **Articles** → Browse scraped articles
4. **Translation** → Translate an article (tokens decrease by ~500)
5. **Enhancement** → Generate 6 formats (tokens decrease by ~1500)
6. **Dashboard** → Check updated token balance (should be ~3000)
7. **Logout** → Redirects to login

---

## 🎯 API Testing (Advanced)

### **Using Swagger UI:**
1. Open: http://localhost:8000/docs
2. Click "Authorize" button
3. Login to get token:
   - POST `/api/auth/login`
   - Use test credentials
   - Copy the `access_token`
4. Click "Authorize" again, paste token
5. Now test all endpoints:

**Translation Endpoints:**
- `POST /api/translate/extract-and-translate`
- `POST /api/translate/translate-text`
- `GET /api/translate/` (history)

**Enhancement Endpoints:**
- `GET /api/enhance/formats`
- `POST /api/enhance/`
- `GET /api/enhance/` (history)

**Scraper Endpoints:**
- `POST /api/scraper/run`
- `GET /api/scraper/status/{job_id}`
- `GET /api/scraper/result/{job_id}`
- `GET /api/scraper/sites`

**Articles Endpoints:**
- `GET /api/articles/`
- `GET /api/articles/stats`
- `GET /api/articles/sources/list`

---

## ✅ Expected Behavior Checklist

### **Authentication:**
- [ ] Login works with correct credentials
- [ ] Login fails with wrong credentials
- [ ] Registration creates new user
- [ ] Password validation enforces rules
- [ ] Protected routes redirect to login
- [ ] Logout clears session

### **Dashboard:**
- [ ] Shows user info correctly
- [ ] Displays token balance
- [ ] Shows all 4 feature cards
- [ ] Cards navigate to correct pages
- [ ] Stats display correctly

### **Translation:**
- [ ] URL extraction works
- [ ] Text translation works
- [ ] Bengali output is correct
- [ ] Tokens are deducted
- [ ] Copy/download works
- [ ] Error messages display

### **Enhancement:**
- [ ] Format selection works
- [ ] All 6 formats generate
- [ ] Each format has unique style
- [ ] Tokens are deducted per format
- [ ] Copy/download works per format

### **Articles:**
- [ ] Articles list displays
- [ ] Search filtering works
- [ ] Source filtering works
- [ ] Pagination works
- [ ] External links work

### **Scraper:**
- [ ] Start button initiates scraping
- [ ] Progress bar updates in real-time
- [ ] Status updates every 3 seconds
- [ ] Completion shows results
- [ ] New articles appear in Articles page

---

## 🐛 Common Issues & Solutions

### **Backend not responding:**
```bash
# Check if server is running
curl http://localhost:8000/health

# If not, restart:
cd backend
python -m uvicorn app.main:app --reload
```

### **Frontend not loading:**
```bash
# Check if Vite is running
# Should see: http://localhost:5173

# If not, restart:
cd frontend
npm run dev
```

### **CORS errors:**
- Backend should have CORS enabled for localhost:5173
- Check backend console for CORS logs

### **OpenAI API errors:**
- Check `.env` file has valid `OPENAI_API_KEY`
- Check OpenAI account has credits

### **No articles in Articles page:**
- Run the Scraper first
- Wait for completion
- Refresh Articles page

---

## 📊 Performance Notes

**Expected Response Times:**
- Translation (URL): 5-15 seconds
- Translation (Text): 3-8 seconds
- Enhancement (6 formats): 20-40 seconds
- Scraper (all sites): 30-90 seconds
- Article listing: <1 second

**Token Usage (Approximate):**
- Translation: 300-800 tokens
- Enhancement per format: 200-400 tokens
- Full enhancement (6 formats): 1200-2400 tokens

---

## 🎉 Success Criteria

**All features working if:**
✅ Can login and register
✅ Dashboard shows correct user data
✅ Translation extracts and translates articles
✅ Enhancement generates all 6 formats
✅ Scraper collects articles successfully
✅ Articles page displays and filters data
✅ Token balance updates correctly
✅ All copy/download functions work
✅ Navigation between pages works
✅ Logout clears session

---

## 📝 Test Results Template

Use this to track your testing:

```
# Test Results - [Date]

## Authentication
- [ ] Login: ___________
- [ ] Register: ___________
- [ ] Logout: ___________

## Translation
- [ ] URL Translation: ___________
- [ ] Text Translation: ___________
- [ ] Token Deduction: ___________

## Enhancement
- [ ] 6 Formats Generated: ___________
- [ ] Copy/Download: ___________
- [ ] Token Deduction: ___________

## Articles
- [ ] List Display: ___________
- [ ] Filtering: ___________
- [ ] Pagination: ___________

## Scraper
- [ ] Start Scraper: ___________
- [ ] Progress Updates: ___________
- [ ] Completion: ___________

## Overall
- [ ] All features working: ___________
- [ ] Performance acceptable: ___________
- [ ] UI responsive: ___________
```

---

**Happy Testing! 🚀**

If you find any issues, check the browser console (F12) and backend logs for error messages.
