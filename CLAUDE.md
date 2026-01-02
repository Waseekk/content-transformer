# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Project Overview

**Swiftor** is an AI-powered translation and content generation platform focused on:
- **Hard News** (হার্ড নিউজ) - Factual, objective journalism
- **Soft News** (সফট নিউজ) - Literary, descriptive feature writing

The platform translates content to Bangladeshi Bengali and generates professional news articles in the "বাংলার কলম্বাস" newspaper style.

## Project Structure

```
swiftor/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   │   ├── auth.py        # JWT authentication
│   │   │   ├── translation.py # Translation endpoints
│   │   │   ├── enhancement.py # Hard/Soft news generation
│   │   │   ├── articles.py    # Article management
│   │   │   └── scraper.py     # News scraping
│   │   ├── core/              # Business logic
│   │   │   ├── prompts.py     # Hard/Soft news prompts
│   │   │   ├── enhancer.py    # Content enhancement
│   │   │   └── translator.py  # Translation logic
│   │   ├── models/            # Database models
│   │   └── services/          # Background services
├── frontend/                   # React Frontend
│   └── src/
│       ├── components/        # UI components
│       ├── pages/             # Route pages
│       └── api/               # API client
├── core/                       # Shared logic (Streamlit app)
├── config/
│   └── formats/
│       └── bengali_news_styles.json  # News format configs
├── START_ALL.bat              # Start all services
├── STOP_ALL.bat               # Stop all services
└── .claude/agents/            # Claude Code agents
```

## Running the Application

### Start Full Stack
```bash
START_ALL.bat
```
- Backend: http://localhost:8000 (FastAPI)
- Frontend: http://localhost:5173 (React)
- API Docs: http://localhost:8000/docs

### Start Backend Only
```bash
START_BACKEND.bat
```

### Start Frontend Only
```bash
START_FRONTEND.bat
```

## Key Components

### Hard News Format
- Professional newspaper style
- Inverted pyramid structure
- 300-500 words
- Bold headline and lead paragraph
- Factual, objective tone

### Soft News Format
- Literary travel features
- Storytelling approach
- 500-800 words
- Immersive descriptions
- Emotional engagement

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register user |
| POST | `/api/auth/login` | Login |
| POST | `/api/translate` | Translate content |
| POST | `/api/enhance` | Generate hard/soft news |
| GET | `/api/articles` | List articles |
| POST | `/api/scraper/run` | Run scraper |

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Frontend**: React, TypeScript, Tailwind CSS, React Query
- **AI**: OpenAI API (gpt-4o-mini)
- **Database**: SQLite (dev) / PostgreSQL (prod)

## Environment Variables

```env
OPENAI_API_KEY=your_key
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your_secret
```

## Claude Agents

Located in `.claude/agents/`:
- `news-scraper.md` - Web scraping agent
- `code-reviewer-optimizer.md` - Code review agent
- `ux-design-advisor.md` - UX design agent
