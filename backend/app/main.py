"""
FastAPI Application Entry Point
Travel News SaaS Backend API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import scraper, articles, auth, translation, enhancement, scheduler

# Create FastAPI application
app = FastAPI(
    title="Travel News API",
    description="Multi-user travel news scraping, translation, and content enhancement API",
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

# Mount API routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(translation.router, prefix="/api/translate", tags=["translation"])
app.include_router(enhancement.router, prefix="/api/enhance", tags=["enhancement"])
app.include_router(scraper.router, prefix="/api/scraper", tags=["scraper"])
app.include_router(scheduler.router, prefix="/api/scraper/scheduler", tags=["scheduler"])
app.include_router(articles.router, prefix="/api/articles", tags=["articles"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Travel News API is running",
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
    print(">>> Travel News API starting up...")

    # Create database tables
    from app.database import engine, Base
    from app.models import user, article, job, translation, enhancement, token_usage, user_config

    print(">>> Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print(">>> Database tables created successfully!")

    # TODO: Initialize Redis connection
    # TODO: Start Celery workers


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print(">>> Travel News API shutting down...")
    # TODO: Close database connections
    # TODO: Close Redis connections
