"""
FastAPI Application Entry Point
Swiftor - Hard News & Soft News Backend API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api import scraper, articles, auth, translation, enhancement, scheduler, oauth
from app.config import get_settings

settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title="Swiftor API",
    description="Hard News & Soft News - Translation and Content Enhancement API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add session middleware for OAuth
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# Mount API routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(oauth.router, prefix="/api/oauth", tags=["oauth"])
app.include_router(translation.router, prefix="/api/translate", tags=["translation"])
app.include_router(enhancement.router, prefix="/api/enhance", tags=["enhancement"])
app.include_router(scraper.router, prefix="/api/scraper", tags=["scraper"])
app.include_router(scheduler.router, prefix="/api/scraper/scheduler", tags=["scheduler"])
app.include_router(articles.router, prefix="/api/articles", tags=["articles"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Swiftor API is running",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",  # TODO: Add actual DB health check
        "services": {
            "scraper": "available",
            "translator": "available",
            "enhancer": "available"
        }
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print(">>> Swiftor API starting up...")

    # Create database tables
    from app.database import engine, Base
    from app.models import user, article, job, translation, enhancement, token_usage, user_config
    from sqlalchemy import text, inspect

    print(">>> Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print(">>> Database tables created successfully!")

    # Run migrations for existing tables
    print(">>> Checking for migrations...")
    with engine.connect() as conn:
        inspector = inspect(engine)
        if 'articles' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('articles')]
            if 'job_id' not in columns:
                print(">>> Adding job_id column to articles table...")
                conn.execute(text("ALTER TABLE articles ADD COLUMN job_id INTEGER REFERENCES jobs(id)"))
                conn.commit()
                print(">>> job_id column added successfully!")
            else:
                print(">>> job_id column already exists")
    print(">>> Migrations complete!")

    # TODO: Initialize Redis connection
    # TODO: Start Celery workers


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print(">>> Swiftor API shutting down...")
    # TODO: Close database connections
    # TODO: Close Redis connections
