# 🚀 TRAVEL NEWS TRANSLATOR - PRODUCTION APP

## ✅ YOUR PRODUCTION APPLICATION

This is a **multi-user SaaS platform** with:

- **Backend**: FastAPI + SQLAlchemy (Python)
- **Frontend**: React 19.2.0 + TypeScript + Vite
- **Database**: SQLite (local dev) / PostgreSQL (production)
- **Authentication**: JWT-based username/password
- **AI**: OpenAI GPT-4 for translation and content enhancement

---

## 📁 PRODUCTION APP STRUCTURE

```
✅ PRODUCTION APP (What you're using):
├── backend/app/main.py          # FastAPI entry point
├── backend/app/api/             # API endpoints (auth, scraper, translate, enhance)
├── backend/app/models/          # Database models (User, Article, Translation, etc.)
├── backend/app/services/        # Business logic services
├── frontend/src/App.tsx         # React frontend entry point
├── frontend/src/components/     # React components
├── shared/                      # Shared business logic (single source of truth)
│   ├── core/                   # AI providers, scraper, translator, enhancer
│   ├── config/                 # Settings, site configs, format configs
│   └── utils/                  # Logging, helpers

❌ LEGACY/BACKUP (Ignore these):
├── app_streamlit_legacy.py.backup   # Old Streamlit single-user app (deprecated)
├── app_copy.py.backup               # Backup file (can delete)
```

---

## 🗄️ DATABASE

### Local Development:
- **SQLite** (`backend/app.db`)
- Automatically created on first run
- No setup required

### Production:
- **PostgreSQL** (via Docker)
- Configured in `docker-compose.prod.yml`
- Auto-migrates on deployment

---

## 🏃 HOW TO RUN YOUR APP

### Option 1: Manual (Development)

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install  # First time only
npm run dev
```

**Access:**
- Frontend: http://localhost:5173
- Backend API Docs: http://localhost:8000/docs

---

### Option 2: Batch Script (Windows)

**Double-click:**
```
START_FULLSTACK.bat
```

This automatically:
1. Starts FastAPI backend on port 8000
2. Starts React frontend on port 5173
3. Opens browser to http://localhost:5173

---

### Option 3: Docker (Production-like)

**Run locally with Docker:**
```bash
# Copy and configure environment
cp .env.production .env
# Edit .env with your OPENAI_API_KEY and SECRET_KEY

# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Access at http://localhost
```

**Stop services:**
```bash
docker-compose -f docker-compose.prod.yml down
```

---

## 🌐 DEPLOY TO HOSTINGER/VPS

**Follow the complete guide:**
```
DEPLOYMENT_GUIDE.md
```

**Quick Deploy:**
```bash
# 1. SSH to your server
ssh root@your-server-ip

# 2. Clone your repo
git clone https://github.com/YOUR_USERNAME/travel-news.git
cd travel-news

# 3. Configure environment
cp .env.production .env
nano .env  # Add your API keys

# 4. Deploy
chmod +x deploy.sh
./deploy.sh
```

Your app will be live at `http://YOUR_SERVER_IP` (or `https://yourdomain.com` with SSL).

---

## 🔑 ENVIRONMENT VARIABLES

**Required in `.env`:**

```bash
# OpenAI API Key (REQUIRED)
OPENAI_API_KEY=sk-your-actual-openai-key-here

# JWT Secret (REQUIRED - generate with: openssl rand -hex 32)
SECRET_KEY=your-random-32-char-secret-here

# Database (Production only)
POSTGRES_PASSWORD=your-secure-database-password

# CORS (Production only)
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

**Generate Secret Key:**
```bash
# Linux/Mac
openssl rand -hex 32

# Windows (Git Bash)
openssl rand -hex 32

# Or use Python
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🎯 KEY FEATURES

### 1. Multi-Site News Scraping
- Configurable scraper for multiple news sources
- Concurrent scraping with real-time progress tracking
- Site configurations in `shared/config/sites_config.json`

### 2. AI Translation
- OpenAI-powered content extraction from webpage HTML
- Translates to **Bangladeshi Bengali** (not Indian Bengali)
- Smart article extraction from full webpage paste

### 3. Multi-Format Content Generation
- **6 Output Formats:**
  1. `newspaper` - Formal newspaper article
  2. `blog` - Personal blog style
  3. `facebook` - Social media post (100-150 words)
  4. `instagram` - Caption with hashtags (50-100 words)
  5. `hard_news` - Professional factual reporting (BC News style)
  6. `soft_news` - Literary travel feature (BC News style)

### 4. User Management
- JWT authentication
- Token-based usage tracking
- Monthly token limits with auto-pause
- Admin panel (separate interface in same app)

### 5. Per-User Data Isolation
- Each user has isolated:
  - Articles
  - Translations
  - Enhancements
  - Scraper configurations
  - Token usage history

---

## 📂 IMPORTANT FILES

### Configuration:
- `shared/config/settings.py` - All system settings
- `shared/config/sites_config.json` - Scraper site configurations
- `shared/config/formats/bengali_news_styles.json` - **Bengali news format guidelines (HARD NEWS & SOFT NEWS)**

### Core Business Logic:
- `shared/core/ai_providers.py` - OpenAI integration
- `shared/core/scraper.py` - Multi-site news scraper
- `shared/core/translator.py` - AI translation engine
- `shared/core/enhancer.py` - Multi-format content generator
- `shared/core/prompts.py` - AI prompts for all 6 formats

### Backend API:
- `backend/app/main.py` - FastAPI application entry point
- `backend/app/api/` - All API endpoint routers
- `backend/app/models/` - Database models (User, Article, Translation, etc.)
- `backend/app/services/` - Business logic services

### Frontend:
- `frontend/src/App.tsx` - React application entry point
- `frontend/src/components/` - All React components
- `frontend/src/api/` - API client functions

### Deployment:
- `docker-compose.prod.yml` - Production Docker orchestration
- `backend/Dockerfile.prod` - Backend production image
- `frontend/Dockerfile.prod` - Frontend production image (multi-stage build)
- `deploy.sh` - One-command deployment script
- `DEPLOYMENT_GUIDE.md` - Complete deployment instructions

---

## 🧪 TESTING

### Test Backend API:
```bash
cd backend
python -m uvicorn app.main:app --reload
# Visit http://localhost:8000/docs for Swagger UI
```

### Test Translation:
```bash
cd backend
python -c "
from shared.core.translator import OpenAITranslator
translator = OpenAITranslator()
result = translator.extract_and_translate('Test article content here')
print(result)
"
```

### Test Multi-Format Enhancement:
```bash
python verify_6_formats.py
```

### Test Scraper:
```bash
python -c "
from shared.core.scraper import MultiSiteScraper
scraper = MultiSiteScraper()
results = scraper.scrape_all_sites()
print(f'Scraped {len(results)} articles')
"
```

---

## 🔧 TROUBLESHOOTING

### Port Already in Use:
```bash
# Windows - Kill process on port 8000
netstat -ano | findstr :8000
taskkill /F /PID <PID>

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

### Database Locked:
```bash
# Delete SQLite database and restart
cd backend
del app.db  # Windows
rm app.db   # Linux/Mac
# Restart backend - database will be recreated
```

### Frontend Build Error:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Docker Issues:
```bash
# Rebuild without cache
docker-compose -f docker-compose.prod.yml build --no-cache

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Restart specific service
docker-compose -f docker-compose.prod.yml restart backend
```

---

## 📚 DOCUMENTATION

- **Production Deployment**: `DEPLOYMENT_GUIDE.md` (471 lines)
- **Project Instructions**: `CLAUDE.md` (full architecture & design patterns)
- **Bengali News Formats**: `shared/config/formats/bengali_news_styles.json` (hard/soft news guidelines)
- **Git Commit Guidelines**: `GIT_COMMIT_GUIDE.md`
- **API Documentation**: http://localhost:8000/docs (when backend is running)

---

## 🎉 NEXT STEPS

1. **Test Locally**: Run with `START_FULLSTACK.bat` or manual commands
2. **Configure API Keys**: Add `OPENAI_API_KEY` to `.env`
3. **Create Admin User**: Use Python shell (see DEPLOYMENT_GUIDE.md Step 5)
4. **Deploy to Production**: Follow `DEPLOYMENT_GUIDE.md` for Hostinger/VPS
5. **Configure Domain**: Point domain to server IP and install SSL

---

## 💡 QUICK TIPS

- **API Documentation**: Visit `/docs` endpoint for interactive API docs (Swagger UI)
- **Database Admin**: Use SQLite browser or psql for database inspection
- **Logs**: Check `backend/logs/` for detailed application logs
- **Format Guidelines**: Hard news and soft news guidelines preserved in `bengali_news_styles.json`
- **Add New Sites**: Edit `shared/config/sites_config.json` to add scraper sources
- **Token Limits**: Configure per-user in database `users` table

---

## ⚠️ IMPORTANT NOTES

1. **This is NOT Streamlit** - The legacy Streamlit app (`app_streamlit_legacy.py.backup`) is deprecated
2. **Production App** = `backend/app/` (FastAPI) + `frontend/` (React)
3. **Hard/Soft News Guidelines** - Fully preserved in `bengali_news_styles.json`
4. **Database** - SQLite locally, PostgreSQL in production
5. **Shared Package** - All business logic in `shared/` to eliminate duplication

---

## 🆘 NEED HELP?

- **API Errors**: Check `backend/logs/` for detailed error logs
- **Database Issues**: See troubleshooting section above
- **Deployment**: Read `DEPLOYMENT_GUIDE.md` step-by-step
- **Architecture**: See `CLAUDE.md` for detailed system design

---

**Your app is production-ready and deployable to Hostinger/VPS! 🚀**
