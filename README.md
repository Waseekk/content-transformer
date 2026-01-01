# 🌍 Travel News Translator - Multi-User SaaS Platform

A comprehensive travel news aggregation, translation, and multi-format content generation system with support for both single-user (Streamlit) and multi-user (FastAPI + React) deployments.

## 🚀 Quick Start

### Option 1: Full Stack (Recommended for Development)
```bash
# Windows
START_FULLSTACK.bat

# Or use the menu
QUICK_START.bat  # Select option 2
```

This launches:
- **Backend API** at `http://localhost:8000` (FastAPI)
- **Frontend UI** at `http://localhost:5173` (React + Vite)
- **API Docs** at `http://localhost:8000/docs` (Swagger)

### Option 2: Legacy Streamlit App (Single User)
```bash
# Windows
streamlit run app.py

# Or use the menu
QUICK_START.bat  # Select option 1
```

Access at `http://localhost:8501`

---

## 📋 Features

### Core Features
- **Multi-Site News Scraping**: Configurable scraping from multiple travel news sources
- **AI-Powered Translation**: OpenAI-based intelligent translation to Bangladeshi Bengali
- **Multi-Format Content Generation**: 6 output formats (Hard News, Soft News, Blog, Facebook, Instagram, Newspaper)
- **Token-Based Pricing**: User token management with auto-pause and monthly resets (Multi-user mode)
- **Real-Time Progress Tracking**: WebSocket-based live scraping updates
- **JWT Authentication**: Secure user authentication and authorization (Multi-user mode)

### Special Features
- **Bengali News Styles**: Professional "বাংলার কলম্বাস" newspaper format guidelines
  - **Hard News**: Factual, objective, inverted pyramid structure
  - **Soft News**: Literary, descriptive travel features with storytelling approach
- **Keyword Search Integration**: Advanced search within scraped articles (29K+ lines feature)
- **Review Agent**: Quality checking system for enhanced content
- **Scheduler**: Automated scraping at configurable intervals

---

## 🏗️ Architecture

### NEW: Shared Package Structure ✨

All core business logic is now centralized in the `shared/` package to eliminate duplication:

```
shared/
├── core/                          # Business logic (single source of truth)
│   ├── ai_providers.py            # OpenAI/Groq AI provider abstraction
│   ├── enhancer.py                # Multi-format content generation
│   ├── prompts.py                 # Format-specific system prompts
│   ├── scraper.py                 # Multi-site news scraper
│   └── translator.py              # OpenAI translation & extraction
├── config/                        # All configuration files
│   ├── settings.py                # System settings
│   ├── sites_config.json          # Scraper site configurations
│   └── formats/
│       └── bengali_news_styles.json  # Hard/Soft news guidelines
└── utils/                         # Utility modules
    └── logger.py                  # Centralized logging
```

**Both Streamlit and FastAPI now import from `shared/`** - eliminating 15,000+ lines of duplicate code!

### Directory Structure

```
travel-news-translator/
├── shared/                        # Shared business logic (NEW!)
├── backend/                       # FastAPI Multi-User API
│   ├── app/
│   │   ├── api/                   # REST endpoints
│   │   ├── models/                # SQLAlchemy database models
│   │   ├── schemas/               # Pydantic validation schemas
│   │   ├── services/              # Business logic layer
│   │   └── middleware/            # Auth middleware
│   ├── migrations/                # Alembic database migrations
│   └── tests/                     # Backend tests
├── frontend/                      # React + TypeScript SPA
│   ├── src/
│   │   ├── pages/                 # Page components
│   │   ├── components/            # Reusable UI components
│   │   ├── api/                   # Axios API client
│   │   ├── contexts/              # React contexts
│   │   └── hooks/                 # Custom React hooks
│   └── public/                    # Static assets
├── app.py                         # Streamlit single-user app (legacy)
├── data/                          # Data storage
│   ├── raw/                       # Scraped articles (JSON/CSV)
│   ├── enhanced/                  # AI-enhanced content
│   └── archive/                   # Archived data
├── logs/                          # Application logs
├── translations/                  # Saved translation files
├── .claude/                       # Claude Code agents
├── docs/                          # Organized documentation
├── START_FULLSTACK.bat            # Launch React + Backend
├── STOP_SERVICES.bat              # Stop all services
└── QUICK_START.bat                # Interactive menu
```

---

## ⚙️ Setup

### 1. Environment Setup

Create `.env` file at the root:
```bash
OPENAI_API_KEY=your_openai_api_key_here
GROQ_API_KEY=your_groq_api_key_here  # Optional
```

### 2. Install Dependencies

#### Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
```

#### Frontend (React)
```bash
cd frontend
npm install
```

#### Streamlit (Legacy)
```bash
pip install -r requirements.txt  # Root directory
```

### 3. Database Setup (Multi-User Mode)

```bash
cd backend
python create_test_user.py  # Creates test user
```

---

## 🎯 Usage

### Full Stack Development

1. **Start Services**:
   ```bash
   START_FULLSTACK.bat
   ```

2. **Access**:
   - Frontend: `http://localhost:5173`
   - Backend API: `http://localhost:8000`
   - API Docs: `http://localhost:8000/docs`

3. **Default Test User**:
   - Email: `test@example.com`
   - Password: `password123`

### Streamlit (Legacy)

1. **Start**:
   ```bash
   streamlit run app.py
   ```

2. **Access**: `http://localhost:8501`

3. **Default Password**: `demo1_2025` (set in `.env` as `APP_PASSWORD`)

---

## 📚 API Endpoints (FastAPI Backend)

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login (returns JWT token)

### Scraper
- `POST /api/scraper/run` - Trigger scraping (async Celery task)
- `GET /api/scraper/status/{job_id}` - Get scraping job status
- `GET /api/scraper/sites` - List user's configured sites

### Translation
- `POST /api/translate` - Extract and translate content (OpenAI)
- Returns: Bengali translation + tokens used

### Enhancement
- `POST /api/enhance` - Generate multi-format content
- Formats: `hard_news`, `soft_news`, `blog`, `facebook`, `instagram`, `newspaper`

### Articles
- `GET /api/articles` - List user's articles (pagination + filters)
- `GET /api/translations` - Translation history
- `GET /api/enhancements` - Enhancement history

### Admin (Admin users only)
- `GET /api/admin/users` - List all users + stats
- `PUT /api/admin/users/{id}/tokens` - Adjust user tokens
- `POST /api/admin/sites` - Add/edit scraper configurations

---

## 🔧 Configuration

### Scraper Sites (`shared/config/sites_config.json`)

```json
{
  "name": "Site Name",
  "url": "https://example.com/travel",
  "multi_view": true,
  "views": {
    "top": "",
    "latest": "?type=latest"
  },
  "selectors": [
    {
      "container_tag": "article",
      "title_tag": "h2",
      "link_tag": "a"
    }
  ]
}
```

### Bengali News Formats (`shared/config/formats/bengali_news_styles.json`)

Contains comprehensive guidelines for:
- **Hard News**: Formal, factual reporting (temperature: 0.4)
- **Soft News**: Literary travel features (temperature: 0.8)

**CRITICAL**: These guidelines are preserved and loaded by `shared/core/prompts.py`

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Manual Testing
- Use `QUICK_START.bat` → Option 5 to test OpenAI translation
- Use `QUICK_START.bat` → Option 6 to view logs

---

## 📖 Documentation

- **[CLAUDE.md](./CLAUDE.md)** - Complete project guide for AI assistants
- **[docs/](./docs/)** - Organized documentation (coming soon)
- **API Docs**: `http://localhost:8000/docs` (when backend is running)

---

## 🛠️ Development

### Adding a New Format

1. Add format config to `shared/core/prompts.py`:
   ```python
   'my_format': {
       'name': 'My Format',
       'icon': '📝',
       'system_prompt': MY_FORMAT_PROMPT,
       'temperature': 0.7,
       'max_tokens': 2000,
   }
   ```

2. Create system prompt with Bengali guidelines

3. Update enhancer to include new format

### Adding a New Scraper Site

1. Edit `shared/config/sites_config.json`
2. Add site configuration with selectors
3. Test using `core/scraper.py` directly
4. Admin can test selectors using Playwright integration

---

## 🚢 Deployment

### Streamlit Cloud
```bash
QUICK_START.bat → Option 4  # Setup git branches
```

### Docker (Full Stack)
```bash
docker-compose up -d
```

### Production Checklist
- [ ] Set production `OPENAI_API_KEY`
- [ ] Update CORS settings in `backend/app/main.py`
- [ ] Set secure `DATABASE_URL` (PostgreSQL recommended)
- [ ] Configure Redis for Celery
- [ ] Set up error tracking (Sentry)
- [ ] Enable HTTPS

---

## 📊 Token Management (Multi-User)

- Each user has a monthly token allocation
- Auto-pause when limit reached
- Monthly automatic reset
- Admin can manually adjust tokens
- Tracks usage per operation (translate/enhance)

---

## 🤝 Contributing

See `docs/CONTRIBUTING.md` (coming soon)

---

## 📝 License

Proprietary - All rights reserved

---

## 🆘 Troubleshooting

### Services won't start
```bash
STOP_SERVICES.bat  # Kill all processes
START_FULLSTACK.bat  # Restart
```

### Import errors after restructure
- Ensure you're using `from shared.core import ...`
- Old imports from `core/`, `config/`, `utils/` are deprecated

### Database issues
```bash
cd backend
rm app.db test_fresh.db  # Reset database
python create_test_user.py  # Recreate
```

### Frontend build fails
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

## 📞 Support

- **Issues**: GitHub Issues
- **Documentation**: See `CLAUDE.md` and `docs/`
- **Logs**: `QUICK_START.bat` → Option 6

---

**Built with ❤️ for the Travel News Community**
