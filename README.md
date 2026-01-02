# Swiftor - Hard News & Soft News Platform

AI-powered translation and content generation platform focused on **Hard News** (factual journalism) and **Soft News** (feature writing) in Bangladeshi Bengali.

## Quick Start

### Start All Services
```bash
START_ALL.bat
```

This launches:
- **Backend API** at `http://localhost:8000` (FastAPI)
- **Frontend UI** at `http://localhost:5173` (React + Vite)
- **API Docs** at `http://localhost:8000/docs` (Swagger)

### Stop All Services
```bash
STOP_ALL.bat
```

---

## Core Features

### Hard News (হার্ড নিউজ)
- Factual, objective reporting
- Inverted pyramid structure
- Professional "বাংলার কলম্বাস" newspaper format
- 300-500 words
- Markdown formatting with bold headlines

### Soft News (সফট নিউজ)
- Literary, descriptive feature writing
- Storytelling approach
- Engaging travel features
- 500-800 words
- Immersive content that transports readers

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI + Python |
| Frontend | React + TypeScript + Tailwind CSS |
| Translation | OpenAI API |
| Database | SQLite (dev) / PostgreSQL (prod) |

---

## Project Structure

```
swiftor/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/       # API routes
│   │   ├── core/      # Business logic
│   │   ├── models/    # Database models
│   │   └── services/  # Services
├── frontend/          # React frontend
│   └── src/
├── core/              # Shared business logic
├── config/            # Configuration files
└── START_ALL.bat      # Start script
```

---

## Environment Variables

Create `.env` file in root:
```env
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your_secret_key
```

---

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /api/translate` | Translate content |
| `POST /api/enhance` | Generate hard/soft news |
| `GET /api/articles` | List scraped articles |
| `POST /api/scraper/run` | Run scraper |

Full API docs: `http://localhost:8000/docs`

---

## License

MIT License
