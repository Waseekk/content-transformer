# Swiftor - AI-Powered News Translation & Generation Platform

> **Swiftor** is a production-grade content transformation platform that automates the translation and formatting of international news into professional Bengali journalism.

**Live Production**: [swiftor.online](https://swiftor.online)

---

## Project Overview

**Project Role**: Full Stack AI Automation Engineer
**Status**: Delivered & In Production

**Swiftor** transforms how newsrooms handle international content by automating:
- Content extraction from any news URL
- Translation to Bangladeshi Bengali
- Professional formatting in two distinct styles

### The Problem
Manual translation and formatting of international news was time-consuming and inconsistent. Journalists spent hours per article ensuring proper Bengali linguistic standards.

### The Solution
An AI-powered pipeline that reduces article processing from hours to seconds while maintaining professional newspaper quality standards.

---

## Key Features

### Dual Content Formats
- **Hard News** - Factual, objective journalism
- **Soft News** - Literary feature writing

### Smart Content Pipeline

```
URL → Extract → Clean → Translate → Enhance → Format → Output
        │                    │           │
   Multi-method         OpenAI      Post-process
   (Trafilatura,       GPT-4o      (Bengali word
    Playwright)                    corrections)
```

### Additional Features
- Multi-source news scraping with scheduling
- User quota management (monthly limits)
- Translation history & saved articles
- Google OAuth authentication
- Support ticket system

---

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 16
- **Cache**: Redis 7
- **AI**: OpenAI GPT-4o-mini
- **Extraction**: Trafilatura, Playwright, Newspaper3k
- **Auth**: JWT + OAuth2

### Frontend
- **Framework**: React 19 + TypeScript
- **Styling**: Tailwind CSS
- **State**: React Query + Zustand
- **Build**: Vite 7

### DevOps
- **Containers**: Docker + Docker Compose
- **Proxy**: Caddy (SSL termination)
- **CI/CD**: GitHub

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     SWIFTOR PLATFORM                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   ┌─────────┐    ┌──────────┐    ┌─────────────────┐   │
│   │  Caddy  │───▶│  React   │───▶│    FastAPI      │   │
│   │  (SSL)  │    │ Frontend │    │    Backend      │   │
│   └─────────┘    └──────────┘    └────────┬────────┘   │
│                                           │            │
│              ┌────────────────────────────┼────────┐   │
│              │  ┌──────────┐  ┌───────────▼──────┐ │   │
│              │  │PostgreSQL│  │   OpenAI API     │ │   │
│              │  └──────────┘  └──────────────────┘ │   │
│              │  ┌──────────┐  ┌──────────────────┐ │   │
│              │  │  Redis   │  │Content Extractors│ │   │
│              │  └──────────┘  └──────────────────┘ │   │
│              └────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
swiftor/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── api/            # 10 API endpoint modules
│   │   ├── core/           # Business logic (translator, enhancer)
│   │   ├── models/         # 9 SQLAlchemy models
│   │   └── services/       # Scraper, scheduler, extraction
│   └── requirements.txt
│
├── frontend/                # React Frontend
│   ├── src/
│   │   ├── pages/          # 9 page components
│   │   ├── components/     # 30+ UI components
│   │   └── api/            # API client modules
│   └── package.json
│
├── config/formats/          # Bengali news style configs
├── docs/                    # Technical documentation
├── docker-compose.yml       # Production deployment
└── deploy.sh               # Deployment script
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | User authentication |
| POST | `/api/translate` | Translate content to Bengali |
| POST | `/api/enhance` | Generate hard/soft news |
| GET | `/api/articles` | List scraped articles |
| POST | `/api/scraper/run` | Trigger news scraping |

Full API documentation available at `/docs` (Swagger UI)

---

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- OpenAI API key

### Quick Start

```bash
# Clone repository
git clone https://github.com/Waseekk/content-transformer.git
cd content-transformer

# Set environment variables
cp .env.example .env
# Edit .env with your OPENAI_API_KEY

# Start all services (Windows)
START_ALL.bat

# Or manually:
# Backend: cd backend && pip install -r requirements.txt && uvicorn app.main:app
# Frontend: cd frontend && npm install && npm run dev
```

**Access Points**:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Production Deployment

```bash
# Deploy with Docker
docker-compose up -d

# Or use deployment script
./deploy.sh
```

**Production Stack**:
- PostgreSQL 16 (database)
- Redis 7 (caching)
- Caddy (reverse proxy + SSL)
- Docker containers

---

## Results & Impact

| Metric | Achievement |
|--------|-------------|
| Processing Time | Hours → Seconds (90%+ reduction) |
| Monthly Capacity | 450+ articles |
| Uptime | 99%+ |
| Format Consistency | Standardized across all content |

---

## Documentation

- [Project Analysis](docs/PROJECT_ANALYSIS.md) - Technical deep-dive
- [Deployment Guide](docs/DEPLOYMENT.md) - Production setup
- [Troubleshooting](docs/DEPLOYMENT_TROUBLESHOOTING.md) - Common issues

---

## License

Proprietary

---

*Developed by [Waseek](https://github.com/Waseekk)*
