# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Travel News Translator** system that scrapes travel news from multiple websites, translates content to Bengali using AI (OpenAI/Groq), and generates multi-format content optimized for different platforms (newspapers, blogs, social media). The system includes a Streamlit web interface, automated scheduling, and real-time scraping progress tracking.

## Project Structure

```
0. travel_news_/
├── .claude/                          # Claude Code configuration
│   └── settings.local.json          # Permissions for Claude Code
├── .env                             # Environment variables (API keys)
├── .git/                            # Git repository
│   └── hooks/                       # Git hooks directory
├── app.py                           # Main Streamlit web application (1200+ lines)
├── CLAUDE.md                        # This file
├── config/                          # Configuration files
│   ├── settings.py                  # All system settings and paths
│   ├── sites_config.json            # Multi-site scraper configurations
│   └── formats/
│       └── bengali_news_styles.json # Bengali news format configs
├── core/                            # Core business logic
│   ├── ai_providers.py              # AI provider abstraction (OpenAI/Groq)
│   ├── enhancer.py                  # Multi-format content generation
│   ├── prompts.py                   # Format-specific prompts (6 formats)
│   ├── scheduler.py                 # Background job scheduler
│   ├── scraper.py                   # Multi-site news scraper
│   └── translator.py                # OpenAI-based translation
├── data/                            # Data storage
│   ├── raw/                         # Scraped articles (JSON/CSV)
│   ├── enhanced/                    # AI-enhanced multi-format outputs
│   ├── processed/                   # Processed data
│   ├── archive/                     # Archived old data
│   └── travel_news_folder/          # Reference samples
├── logs/                            # Application logs
│   ├── scraper_YYYYMMDD.log
│   ├── webapp_YYYYMMDD.log
│   ├── scheduler_YYYYMMDD.log
│   └── enhancer_YYYYMMDD.log
├── translations/                    # Saved translation files
│   └── translation_*.txt
├── utils/                           # Utility modules
│   └── logger.py                    # Centralized logging
├── setup.py                         # Package setup
├── test_bengali_news.py             # Test Bengali formats
├── verify_6_formats.py              # Verify all 6 output formats
├── verify_app_ui.py                 # UI verification script
├── example_6_formats.py             # Usage examples
├── groq_test.py                     # Groq API test
├── BENGALI_NEWS_INTEGRATION.md      # Bengali news feature docs
├── INTEGRATION_COMPLETE.md          # Integration completion notes
├── OPENAI_TRANSLATION_MIGRATION.md  # OpenAI migration docs
└── GIT_COMMIT_GUIDE.md              # Git commit guidelines
```

### Key Directories

- **`config/`** - All configuration files; modify `sites_config.json` to add new scraping sources
- **`core/`** - All business logic modules; self-contained and testable
- **`data/raw/`** - Scraper output; files named `travel_news_multisite_YYYYMMDD_HHMMSS.json`
- **`data/enhanced/`** - AI-generated multi-format content
- **`translations/`** - User-saved translations from the web UI
- **`logs/`** - Rotating daily logs; viewable in the web UI Logs tab

## Running the Application

### Start the Web Application
```bash
streamlit run app.py
```

The app will launch at `http://localhost:8501` with a full UI for:
- Manual and scheduled scraping
- Article browsing with pagination and filtering
- AI-powered translation (OpenAI or Google Translate)
- Multi-format content generation (6 formats)
- Translation history and file management
- Real-time scraping logs

### Testing Components

**Test multi-site scraper:**
```bash
python core/scraper.py
```

**Test OpenAI translation:**
```bash
python core/translator.py
```

**Test content enhancement:**
```bash
python core/enhancer.py
```

**Verify 6-format output:**
```bash
python verify_6_formats.py
```

**Test Bengali news formats:**
```bash
python test_bengali_news.py
```

## Architecture Overview

### Core Components

**1. Multi-Site Scraper (`core/scraper.py`)**
- `MultiSiteScraper` (alias: `TravelNewsScraper`) - Main scraper class
- Reads site configurations from `config/sites_config.json`
- Supports multi-view scraping (top/latest/popular)
- Thread-safe status tracking via `NewsScraperStatus`
- Saves results to `data/raw/` as JSON and CSV
- Returns per-site statistics and progress updates

**2. AI Translation System (`core/translator.py`)**
- `OpenAITranslator` - Smart content extraction and translation
- Extracts article content from pasted webpage HTML
- Translates to natural Bangladeshi Bengali (not Indian Bengali)
- Uses structured prompts for content extraction
- Returns JSON with headline, content, author, date
- Fallback to `GoogleTranslator` (legacy, via `deep_translator`)

**3. Content Enhancer (`core/enhancer.py`)**
- `ContentEnhancer` - Multi-format content generation
- Generates 6 output formats from translated text:
  - `newspaper` - Formal newspaper article
  - `blog` - Personal blog style
  - `facebook` - Social media post (100-150 words)
  - `instagram` - Caption with hashtags (50-100 words)
  - `hard_news` - Professional factual reporting (BC News style)
  - `soft_news` - Literary travel feature (BC News style)
- Uses format-specific prompts from `core/prompts.py`
- Tracks token usage per format
- `EnhancementResult` objects store output

**4. Scheduler (`core/scheduler.py`)**
- `ScraperScheduler` - Background job scheduling
- Uses APScheduler with configurable intervals (1-24 hours)
- Global instance via `get_scheduler()`
- Status tracking: next run time, run count, last run
- Thread-safe execution

**5. AI Providers (`core/ai_providers.py`)**
- Unified interface for OpenAI and Groq APIs
- `get_provider(provider_name, model)` factory function
- Handles API key validation from environment
- Returns (content, tokens_used) tuples

**6. Prompts (`core/prompts.py`)**
- Format-specific system prompts for all 6 formats
- Bengali news styles loaded from `config/formats/bengali_news_styles.json`
- `FORMAT_CONFIG` dictionary with temperature, max_tokens per format
- `get_format_config(format_type)` and `get_user_prompt()` helpers

### Configuration

**Settings (`config/settings.py`)**
- All paths: `RAW_DATA_DIR`, `TRANSLATIONS_DIR`, `LOGS_DIR`, etc.
- `SCRAPER_CONFIG` - Headers, timeout, delays
- `SCHEDULER_CONFIG` - Default intervals, timezone
- `TRANSLATION_CONFIG` - Languages, chunk sizes
- `AI_CONFIG` - Provider/model configs, format definitions
- `SITES_CONFIG_PATH` - Points to sites configuration

**Sites Configuration (`config/sites_config.json`)**
- Multi-site scraping configurations
- Each site has: name, url, selectors (CSS selectors for scraping)
- Supports multi-view scraping with view parameters
- Selector fields: container_tag, title_tag, link_tag, publisher_tag, etc.

### Data Flow

1. **Scraping**: `MultiSiteScraper` → reads `sites_config.json` → scrapes articles → saves to `data/raw/travel_news_multisite_*.json`
2. **Translation**: User pastes content → `OpenAITranslator.extract_and_translate()` → returns Bengali text
3. **Enhancement**: Bengali text → `ContentEnhancer.enhance_all_formats()` → generates 6 formats → optionally saves to `data/enhanced/`
4. **Storage**: Translations saved to `translations/translation_*.txt`, Enhanced content to `data/enhanced/*.txt` and JSON

### State Management (Streamlit)

The app uses `st.session_state` for:
- `articles` - Loaded articles list
- `selected_article` - Currently selected article
- `translations` - Translation history
- `translation_method` - 'openai' or 'google'
- `scraper_status` - Real-time scraping status
- `scheduler` - Global scheduler instance
- `is_polling` - Enable/disable UI refresh during scraping
- `enhancement_results` - Last generated formats
- `ai_provider` / `ai_model` - Current AI settings

### Logging

All modules use centralized logging via `utils/logger.py`:
- `get_scraper_logger()` → `logs/scraper_YYYYMMDD.log`
- `get_webapp_logger()` → `logs/webapp_YYYYMMDD.log`
- `get_scheduler_logger()` → `logs/scheduler_YYYYMMDD.log`
- `LoggerManager.get_logger('enhancer')` → `logs/enhancer_YYYYMMDD.log`

View logs in the **Logs** tab in the web UI with filtering and auto-refresh.

## Key Design Patterns

**1. Status Tracking**
The scraper uses a shared `NewsScraperStatus` object that updates in real-time:
- Progress percentage
- Current site being scraped
- Articles count
- Per-site statistics
- Start/end times

This allows the UI to poll for updates during background scraping.

**2. Provider Abstraction**
All AI providers (OpenAI, Groq) implement the same interface:
```python
provider = get_provider(provider_name, model)
content, tokens = provider.generate(system_prompt, user_prompt, temperature, max_tokens)
```

**3. Format Configuration**
Each output format has a config dict with:
- `name`, `icon`, `description` (for UI)
- `system_prompt` (AI instructions)
- `temperature`, `max_tokens` (generation params)

Add new formats by extending `FORMAT_CONFIG` in `core/prompts.py`.

**4. Background Threading**
Long-running operations (scraping, scheduling) run in separate threads to prevent UI blocking:
```python
thread = threading.Thread(target=run_scraper_async, args=(scraper,))
thread.start()
```

**5. Light Polling**
The app uses a 4-second polling loop when `is_polling=True` to refresh the UI during scraping without heavy resource usage.

## Important Implementation Notes

### Adding a New Site to Scraper

Edit `config/sites_config.json` and add:
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
      "container_class": "news-item",
      "title_tag": "h2",
      "title_class": "headline",
      "link_tag": "a",
      "link_attribute": "href"
    }
  ]
}
```

### Translation Method Selection

- **OpenAI Translation** (default): Intelligently extracts article from full webpage paste, translates naturally
- **Google Translate**: Fast but basic word-by-word translation, requires clean article text

Set via `st.session_state.translation_method` in UI.

### Bengali Content Requirements

All Bengali output must use:
- **Bangladeshi Bengali dialect** (not Indian Bengali)
- Modern vocabulary and phrasing
- Appropriate formality for format (news vs. social media)

The prompts in `core/prompts.py` enforce this.

### Environment Variables

Required in `.env`:
```
OPENAI_API_KEY=your_key_here
GROQ_API_KEY=your_key_here  # Optional, for Groq provider
```

### File Naming Conventions

- Scraped data: `travel_news_multisite_YYYYMMDD_HHMMSS.json`
- Translations: `translation_YYYYMMDD_HHMMSS.txt`
- Enhanced content: `{headline_slug}_{format_type}_YYYYMMDD_HHMMSS.txt`
- Logs: `{logger_type}_YYYYMMDD.log`

## Testing Before Commits

When modifying core functionality, test:
1. Run the scraper directly: `python core/scraper.py`
2. Test translation: `python core/translator.py`
3. Verify formats: `python verify_6_formats.py`
4. Launch the web app: `streamlit run app.py` and test the complete flow

## Common Pitfalls

1. **Don't modify `app.py` without reading it first** - It's 1200+ lines with complex state management
2. **Status callbacks are optional** - Many methods accept `status_callback=None` for CLI usage
3. **The scraper has backward compatibility** - `TravelNewsScraper` is an alias for `MultiSiteScraper`, and `scrape_all_views()` calls `scrape_all_sites()`
4. **Format configs load from JSON** - Hard news and soft news configs are loaded from `config/formats/bengali_news_styles.json` with fallbacks
5. **Translation returns different types** - OpenAI returns a dict with multiple fields, Google returns a tuple `(text, tokens)`

## When Debugging

- Check logs in `logs/` directory (viewable in web UI)
- Use the Logs tab with filters for specific issues
- Scraper status is accessible via `scraper.status` object
- Test individual modules before integration
- Verify API keys are loaded: `echo $OPENAI_API_KEY` or check `.env`



## Developers Note
 🎯 Project Overview

 Transform single-user Streamlit app into multi-user SaaS with:
 - Backend: FastAPI + SQLite + Celery
 - Frontend: React with TypeScript
 - Auth: JWT-based username/password
 - Pricing: Token-based with auto-pause (monthly reset)
 - Data: Fully isolated per user
 - Admin: Separate admin panel in same app
 - AI: OpenAI only (remove Groq)

 ---
 📋 Implementation Phases

 Phase 1: Backend Foundation (Week 1-2)

 1.1 Project Setup
 - Create new backend/ directory structure
 - Set up FastAPI with SQLAlchemy + Alembic migrations
 - Configure SQLite database
 - Set up Redis for Celery + caching
 - Copy reusable core modules (core/scraper.py, core/translator.py, core/enhancer.py,
 core/ai_providers.py, core/prompts.py)

 1.2 Database Models
 - Create models: User, Article, Translation, Enhancement, Job, TokenUsage, UserConfig
 - Design schema for full user data isolation
 - Set up foreign keys and cascading deletes
 - Add indexes for performance

 1.3 Authentication System
 - Implement user registration/login endpoints
 - JWT token generation + refresh tokens
 - Password hashing (bcrypt)
 - Email validation
 - Token middleware for protected routes

 1.4 User & Token Management
 - Token tracking per operation (translate/enhance)
 - Auto-pause logic when monthly limit reached
 - Monthly token reset scheduler
 - User subscription tier system (Free/Premium)

 ---
 Phase 2: Core API Endpoints (Week 2-3)

 2.1 Scraper API
 - POST /api/scraper/run - Trigger scraping (async Celery task)
 - GET /api/scraper/status/{job_id} - Get scraping status
 - GET /api/scraper/sites - List available sites (user-specific)
 - POST /api/admin/scraper/sites - Admin: Add/edit scraper sites

 2.2 Translation API
 - POST /api/translate - Extract + translate content (OpenAI only)
 - Check user token balance before processing
 - Deduct tokens after completion
 - Save translation to user's database records
 - Return translation + remaining tokens

 2.3 Enhancement API
 - POST /api/enhance - Generate multi-format content (async job)
 - User-specific format access control (FB/Blog/Instagram vs Hard/Soft News)
 - Token deduction per format
 - Save enhanced content to database
 - Return job ID for status polling

 2.4 Articles & History
 - GET /api/articles - List user's articles (pagination + filters)
 - GET /api/translations - Translation history
 - GET /api/enhancements - Enhancement history
 - DELETE /api/translations/{id} - Delete user's translations

 ---
 Phase 3: Background Jobs & Real-Time (Week 3-4)

 3.1 Celery Tasks
 - Set up Celery with Redis broker
 - Create tasks: scrape_articles_task, enhance_content_task
 - Per-user task isolation
 - Task progress tracking in database
 - Error handling and retry logic

 3.2 WebSocket for Real-Time Updates
 - Set up Socket.IO or FastAPI WebSocket
 - Real-time scraper progress (replace polling)
 - Enhancement job status updates
 - Token balance updates
 - Connection per user with authentication

 3.3 Scheduler for Auto-Scraping
 - Replace global scheduler with Celery Beat
 - User-configurable scraping schedules
 - Store schedules in user_configs table
 - Dynamic schedule updates

 ---
 Phase 4: Admin Panel Backend (Week 4)

 4.1 Admin Authentication
 - Admin role flag in User model
 - Admin-only middleware decorator
 - Separate JWT claim for admin users

 4.2 Admin APIs
 - GET /api/admin/users - List all users + stats
 - PUT /api/admin/users/{id}/tokens - Manually adjust user tokens
 - POST /api/admin/sites - Add/edit scraper configurations
 - GET /api/admin/analytics - System-wide analytics
 - PUT /api/admin/users/{id}/formats - Configure allowed formats per user

 4.3 User-Specific Site Configs
 - Store site configs per user in database (not shared JSON)
 - Users can choose: Travel, Politics, Sports, etc.
 - Admin can create site config templates
 - Users select from templates or request custom

 ---
 Phase 5: Frontend - React App (Week 5-6)

 5.1 Project Setup
 - Create React app with TypeScript + Vite
 - Set up React Router for navigation
 - Axios instance with JWT interceptors
 - Material-UI or Ant Design for components

 5.2 Authentication UI
 - Login page with email/password
 - Registration page
 - JWT token storage (localStorage/cookies)
 - Auto-refresh token logic
 - Protected route wrapper

 5.3 User Dashboard
 - Token usage widget (remaining/total)
 - Recent articles feed
 - Translation history
 - Quick actions (scrape/translate/enhance)

 5.4 Scraper Interface
 - Manual scrape trigger button
 - Real-time progress bar (WebSocket)
 - Site selection (user's configured sites)
 - Schedule configuration

 5.5 Translation Interface
 - Paste content textarea
 - OpenAI translation button
 - Display: Bengali translation + tokens used
 - Save to history

 5.6 Enhancement Interface
 - Format selection based on user tier
 - Multi-format generation
 - Display all formats side-by-side
 - Download/copy buttons
 - Token cost preview before generation

 5.7 History & Files
 - Paginated translation history
 - Paginated enhancement history
 - Filter by date/format/source
 - Delete functionality

 ---
 Phase 6: Admin Panel Frontend (Week 6)

 6.1 Admin Dashboard
 - Total users count
 - System-wide token usage
 - Active jobs monitoring
 - Revenue analytics (if payment integrated)

 6.2 User Management
 - User list with search/filter
 - View user details (tokens, tier, activity)
 - Manually add/remove tokens
 - Enable/disable users
 - Configure allowed formats per user

 6.3 Site Configuration Manager
 - Visual editor for scraper sites
 - Playwright integration for testing selectors
 - Add/edit/delete site configs
 - Assign sites to specific users

 ---
 Phase 7: Playwright Integration (Week 7)

 7.1 Scraper Config Testing
 - Use Playwright MCP server to test selectors
 - Admin endpoint: POST /api/admin/sites/test
 - Returns: Sample scraped articles + screenshots
 - Validate selector effectiveness
 - Save working configs

 7.2 Interactive Selector Builder
 - Admin UI: Point-and-click selector builder
 - Playwright navigates to site
 - Admin clicks elements to generate selectors
 - Auto-test and validate

 ---
 Phase 8: Cleanup & Optimization (Week 8)

 8.1 Remove Groq Provider
 - Delete Groq-related code from ai_providers.py
 - Remove Groq API key from env
 - Simplify provider logic (OpenAI only)
 - Update all references

 8.2 Performance Optimization
 - Database query optimization (indexes)
 - API response caching (Redis)
 - File upload optimization (direct S3 if needed)
 - Lazy loading in React
 - Bundle size optimization

 8.3 Testing
 - Backend unit tests (pytest)
 - API endpoint tests
 - Frontend component tests (Jest)
 - E2E tests (Playwright)

 ---
 🚀 Deployment Strategy

 Development:
 - Docker Compose: Backend + Frontend + Redis + Celery Worker + SQLite

 Production:
 - Backend: Docker container on cloud (AWS/DigitalOcean)
 - Frontend: Static hosting (Vercel/Netlify) or same container with Nginx
 - Database: Managed SQLite or upgrade to PostgreSQL
 - Redis: Managed Redis (Redis Cloud/AWS ElastiCache)
 - Celery Worker: Separate container

 ---
 📦 Deliverables

 1. Backend API (FastAPI + SQLite + Celery)
 2. Frontend App (React + TypeScript)
 3. Admin Panel (React components + API)
 4. User Authentication (JWT-based)
 5. Token Management System
 6. Per-User Data Isolation
 7. Real-Time Updates (WebSocket)
 8. Playwright Scraper Testing
 9. OpenAI-Only Integration
 10. Docker Deployment Setup

 ---
 💰 Payment Integration (Future - Week 9+)

 - Webhook handler for payment events
 - Auto-upgrade user tier on payment
 - Auto-pause on payment failure
 - Bkash integration (Bangladesh)



-also, you can add agents/sub agents if you need anywhere in any part of the project 
 ---



