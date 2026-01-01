# Streamlit Cloud Deployment Guide

**For deploying the Travel News Translator app WITHOUT backend folder**

---

## Problem
You have:
- ✅ Streamlit app in `app.py` (for client demo)
- ✅ Backend folder (FastAPI - Phase 2/8 complete)
- ❌ Don't want `backend/` folder on Streamlit Cloud

---

## Solution: Git Branches Strategy

### Method 1: Separate Branches (RECOMMENDED)

```bash
# Step 1: Go to your project folder
cd "E:\data_insightopia\travel_news\v1_all\0. travel_news_"

# Step 2: Check current status
git status

# Step 3: Create and switch to a new branch for Streamlit deployment
git checkout -b streamlit-cloud

# Step 4: Remove backend folder from THIS branch only
git rm -r backend/
git commit -m "Remove backend folder for Streamlit Cloud deployment"

# Step 5: Push to GitHub (streamlit-cloud branch)
git push origin streamlit-cloud

# Step 6: To go back to backend development
git checkout main
# Now backend/ folder is back!
```

**Result:**
- `main` branch: Has backend/ folder (for development)
- `streamlit-cloud` branch: No backend/ folder (for Streamlit Cloud)

**Deploy on Streamlit Cloud:**
1. Go to https://streamlit.io/cloud
2. Connect your GitHub repo
3. **Select branch: `streamlit-cloud`** ← IMPORTANT
4. Main file: `app.py`
5. Deploy!

---

### Method 2: Use .gitignore (Alternative)

If you want to use the SAME branch but exclude backend:

```bash
# Step 1: Edit .gitignore
# Uncomment this line in .gitignore:
backend/

# Step 2: Remove backend from git tracking
git rm -r --cached backend/
git commit -m "Stop tracking backend folder"

# Step 3: Push to GitHub
git push origin main
```

**DRAWBACK:** Backend folder won't be in git anymore (not recommended if you want to version control it)

---

## Recommended Workflow

### For Streamlit Demo (Client-facing):
```bash
git checkout streamlit-cloud
streamlit run app.py
# Show client OR deploy to Streamlit Cloud
```

### For Backend Development:
```bash
git checkout main
cd backend
uvicorn app.main:app --reload
# Continue Phase 3-8 development
```

---

## What Each Branch Has

### `main` branch:
```
0. travel_news_/
├── app.py                   # Streamlit app
├── backend/                 # ✅ FastAPI backend (Phase 2/8)
│   ├── app/
│   ├── alembic/
│   └── ...
├── config/
├── core/
├── data/
└── ...
```

### `streamlit-cloud` branch:
```
0. travel_news_/
├── app.py                   # Streamlit app
├── config/                  # ✅ Settings
├── core/                    # ✅ Scraper, Translator, Enhancer
├── data/                    # ✅ Sample data
├── utils/                   # ✅ Logger
└── requirements.txt         # ✅ Dependencies (Streamlit only)
# ❌ backend/ folder NOT HERE
```

---

## Deploying to Streamlit Cloud

### Step 1: Create GitHub Repository

```bash
# If you haven't initialized git yet:
cd "E:\data_insightopia\travel_news\v1_all\0. travel_news_"
git init
git add .
git commit -m "Initial commit: Streamlit app + Backend Phase 2"
git branch -M main

# Create repo on GitHub (via web interface)
# Then:
git remote add origin https://github.com/YOUR_USERNAME/travel-news-translator.git
git push -u origin main

# Create streamlit-cloud branch
git checkout -b streamlit-cloud
git rm -r backend/
git commit -m "Remove backend for Streamlit Cloud"
git push -u origin streamlit-cloud
```

### Step 2: Configure Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Sign in with GitHub
3. Click **"New app"**
4. Select:
   - Repository: `travel-news-translator`
   - **Branch: `streamlit-cloud`** ← CRITICAL
   - Main file: `app.py`
5. Click **"Advanced settings"**
6. Add secrets (Environment Variables):
   ```toml
   OPENAI_API_KEY = "your-key-here"
   GROQ_API_KEY = "your-key-here"  # if using Groq
   ```
7. Click **"Deploy"**

---

## Requirements.txt for Streamlit Cloud

Make sure your `requirements.txt` has ONLY Streamlit dependencies:

```txt
# Core
streamlit==1.31.0
requests==2.31.0
beautifulsoup4==4.12.2

# Translation
deep-translator==1.11.4

# AI Providers
openai>=1.12.0
groq>=0.4.0

# Data Processing
pandas==2.1.4
python-dotenv==1.0.0

# Scheduling (if needed)
APScheduler==3.10.4

# Utilities
lxml==4.9.3
python-dateutil>=2.8.0

# Optional: Selenium for advanced scraping
selenium==4.36.0
```

**Remove** from requirements.txt for Streamlit Cloud:
- ❌ FastAPI
- ❌ SQLAlchemy
- ❌ uvicorn
- ❌ alembic
- ❌ Celery
- ❌ Redis

---

## Switching Between Branches

### To work on Streamlit app (for client demo):
```bash
git checkout streamlit-cloud
streamlit run app.py
# backend/ folder is NOT visible here
```

### To work on Backend (Phase 3-8):
```bash
git checkout main
cd backend
python test_phase2.py
# backend/ folder is back!
```

### To sync changes from main to streamlit-cloud:
```bash
# Make changes in main branch
git checkout main
# Edit app.py, core/, config/, etc.
git add .
git commit -m "Updated scraper logic"
git push origin main

# Merge into streamlit-cloud (but skip backend/)
git checkout streamlit-cloud
git merge main
# If backend/ appears, remove it again:
git rm -r backend/
git commit -m "Keep backend removed"
git push origin streamlit-cloud
```

---

## Common Issues & Solutions

### Issue 1: "backend/ folder appeared in streamlit-cloud branch"

**Solution:**
```bash
git checkout streamlit-cloud
git rm -r backend/
git commit -m "Remove backend folder"
git push origin streamlit-cloud
```

### Issue 2: "Streamlit Cloud can't find modules"

**Cause:** Missing files in `streamlit-cloud` branch

**Solution:**
```bash
git checkout streamlit-cloud
# Make sure these exist:
ls config/settings.py
ls core/scraper.py
ls core/translator.py
ls core/enhancer.py
# If missing, copy from main:
git checkout main -- config/ core/ utils/
git commit -m "Add missing modules"
git push origin streamlit-cloud
```

### Issue 3: "Import errors in app.py"

**Cause:** app.py trying to import from backend/

**Solution:** Ensure app.py doesn't have these imports:
```python
# ❌ Remove these if present:
from backend.app.core.ai_providers import ...
from backend.app.services import ...

# ✅ Keep these:
from core.translator import OpenAITranslator
from core.scraper import TravelNewsScraper
from config.settings import AI_CONFIG
```

---

## Folder Structure After Setup

### Your Local Machine:

```
E:\data_insightopia\travel_news\v1_all\0. travel_news_\
├── .git/
│   └── (both branches stored here)
├── app.py
├── backend/          ← Visible in 'main', hidden in 'streamlit-cloud'
├── config/
├── core/
└── ...
```

### Streamlit Cloud (streamlit-cloud branch):

```
deployed-app/
├── app.py
├── config/
├── core/
├── data/
└── requirements.txt
# ❌ No backend/ folder
```

### GitHub Repository:

```
github.com/YOUR_USERNAME/travel-news-translator/
├── Branch: main
│   └── (has backend/)
└── Branch: streamlit-cloud
    └── (no backend/)
```

---

## Summary

✅ **Best Practice:**
- Use **separate git branches**
- `main` branch: Full project (Streamlit + Backend)
- `streamlit-cloud` branch: Only Streamlit app
- Deploy `streamlit-cloud` branch to Streamlit Cloud
- Continue backend work in `main` branch

✅ **Benefits:**
- Clean separation
- No code duplication
- Easy to sync updates
- Backend stays in version control
- Client only sees Streamlit app

✅ **Commands:**
```bash
# Client demo / Streamlit work
git checkout streamlit-cloud

# Backend development
git checkout main
```

---

## Next Steps

1. ✅ Fix OpenAI translation error (done in app.py)
2. Initialize git and create branches (see above)
3. Push to GitHub
4. Deploy `streamlit-cloud` branch to Streamlit Cloud
5. Share live URL with client
6. Continue backend development in `main` branch

---

**Need Help?**
- Test locally: `streamlit run app.py`
- Check branch: `git branch`
- View changes: `git status`
- Streamlit Cloud logs: Check app dashboard for errors

Good luck! 🚀
