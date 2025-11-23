# Travel News SaaS - Backend

Multi-user FastAPI backend for news scraping, translation, and AI enhancement.

## 🎯 Features

- **User Authentication:** JWT-based auth with registration/login
- **Token Management:** Track and limit AI token usage per user
- **Multi-Site Scraping:** Configurable news scraping from multiple sources
- **AI Translation:** OpenAI-powered content extraction and translation to Bengali
- **Multi-Format Enhancement:** Generate 6 different content formats
- **Background Jobs:** Celery-based async task processing
- **Real-Time Updates:** WebSocket support for live progress updates
- **Admin Panel:** User management, site configuration, analytics

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/                   # API route handlers
│   ├── models/                # SQLAlchemy database models ✅
│   ├── schemas/               # Pydantic validation schemas
│   ├── services/              # Business logic layer
│   ├── tasks/                 # Celery background tasks
│   ├── core/                  # Core modules (scraper, translator, enhancer) ✅
│   ├── utils/                 # Utility functions ✅
│   ├── middleware/            # Custom middleware
│   ├── config.py              # Application configuration ✅
│   ├── database.py            # Database setup ✅
│   └── main.py                # FastAPI app entry point ✅
├── migrations/                # Alembic database migrations ✅
├── config/                    # Configuration files ✅
├── tests/                     # Test suite
├── requirements.txt           # Python dependencies ✅
├── alembic.ini                # Alembic configuration ✅
└── .env.example               # Environment variables template ✅
```

## ⚙️ Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys and settings
```

Required environment variables:
- `SECRET_KEY` - JWT secret key
- `OPENAI_API_KEY` - OpenAI API key
- `REDIS_URL` - Redis connection URL (default: redis://localhost:6379/0)

### 3. Initialize Database

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 4. Run the Application

```bash
# Development server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

API documentation: `http://localhost:8000/docs` (Swagger UI)

### 5. Run Celery Worker (for background tasks)

```bash
# In a separate terminal
celery -A app.tasks.celery_app worker --loglevel=info
```

### 6. Run Celery Beat (for scheduled tasks)

```bash
# In a separate terminal
celery -A app.tasks.celery_app beat --loglevel=info
```

## 🗄️ Database Models

### User
- User accounts with email/password authentication
- Subscription tiers (free/premium)
- Token balance and limits
- Admin role flag

### Article
- Scraped news articles (user-specific)
- Source, publisher, headline, URL
- Metadata and timestamps

### Translation
- Translation history
- Original and translated text
- AI provider and token usage tracking

### Enhancement
- AI-enhanced content in multiple formats
- Format type (newspaper, blog, social media)
- Token usage per enhancement

### Job
- Background job tracking
- Status, progress, results
- Celery task integration

### TokenUsage
- Detailed token consumption tracking
- Cost calculation per operation
- Analytics and billing data

### UserConfig
- User-specific settings
- Enabled sites and formats
- Scraping schedules
- AI preferences

## 🔐 Authentication

JWT-based authentication with access and refresh tokens.

**Register:**
```bash
POST /api/auth/register
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Login:**
```bash
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "password"
}
```

**Protected Endpoints:**
Add `Authorization: Bearer <token>` header to requests.

## 🚀 API Endpoints (To be implemented in Phase 2)

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh access token

### Scraper
- `POST /api/scraper/run` - Trigger scraping
- `GET /api/scraper/status/{job_id}` - Get job status
- `GET /api/scraper/sites` - List available sites

### Translation
- `POST /api/translate` - Translate content
- `GET /api/translations` - List translation history
- `DELETE /api/translations/{id}` - Delete translation

### Enhancement
- `POST /api/enhance` - Generate enhanced content
- `GET /api/enhancements` - List enhancements
- `GET /api/enhancements/{id}` - Get enhancement details

### Articles
- `GET /api/articles` - List articles
- `GET /api/articles/{id}` - Get article details

### Admin (Admin only)
- `GET /api/admin/users` - List all users
- `PUT /api/admin/users/{id}/tokens` - Adjust user tokens
- `POST /api/admin/sites` - Manage scraper sites
- `GET /api/admin/analytics` - System analytics

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app
```

## 📝 Development

### Code Style
- Use `black` for code formatting
- Use `flake8` for linting

```bash
black app/
flake8 app/
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build
```

## 📊 Monitoring

- Logs: `logs/` directory
- Database: SQLite `app.db` file (or PostgreSQL in production)
- Redis: Monitor with `redis-cli monitor`
- Celery: Flower dashboard `celery -A app.tasks.celery_app flower`

## 🔧 Configuration

All settings in `app/config.py` can be overridden with environment variables.

Key settings:
- `FREE_TIER_MONTHLY_TOKENS` - Default: 10,000
- `PREMIUM_TIER_MONTHLY_TOKENS` - Default: 100,000
- `TOKEN_RESET_DAY` - Day of month for token reset
- `SUBSCRIPTION_TIERS` - Tier definitions and permissions

## 📦 Next Steps (Phase 2-8)

- [ ] Phase 2: Implement API endpoints
- [ ] Phase 3: Set up Celery and WebSocket
- [ ] Phase 4: Create admin panel APIs
- [ ] Phase 5: Build React frontend
- [ ] Phase 6: Admin panel UI
- [ ] Phase 7: Playwright integration
- [ ] Phase 8: Testing and optimization
