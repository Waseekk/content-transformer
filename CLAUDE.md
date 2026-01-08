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

---

## TODO List (Last Updated: 2026-01-08)

### Critical Security Fixes (Before Production)

- [ ] **Fix OAuth tokens in URL** - `backend/app/api/oauth.py:126`
  - Use HTTP-only cookies instead of query parameters
  - Tokens currently exposed in browser history/logs

- [ ] **Fix database session management** - `backend/app/api/oauth.py:81`
  - Replace `SessionLocal()` with `db: Session = Depends(get_db)`
  - Prevents connection leaks

- [ ] **Add OAuth CSRF protection** - `backend/app/api/oauth.py`
  - Implement state parameter validation in OAuth flow

- [ ] **Fix empty password for OAuth users** - `backend/app/api/oauth.py:102`
  - Use secure random hash or special marker instead of empty string

### Performance Optimizations

- [ ] **Fix N+1 query in session history** - `backend/app/api/articles.py:361-366`
  - Use single GROUP BY query instead of separate query per job

- [ ] **Remove duplicate database query** - `backend/app/api/articles.py:74-78, 108-113`
  - Store "latest job" query result and reuse

### Code Cleanup

- [ ] Remove console.log statements from frontend files:
  - `frontend/src/api/auth.ts`
  - `frontend/src/api/axios.ts`
  - `frontend/src/services/api.ts`
  - `frontend/src/services/axios.ts`
  - `frontend/src/hooks/useArticles.ts`
  - `frontend/src/pages/ArticlesPage.tsx`

- [ ] Add loading states to `SearchableMultiSelect` component

- [ ] Improve exception handling (avoid exposing error details to clients)

### Future Improvements

- [ ] Set up Alembic for proper database migrations
- [ ] Add unit/integration tests
- [ ] Add monitoring and logging
