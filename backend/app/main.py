"""
FastAPI Application Entry Point
Swiftor - Hard News & Soft News Backend API
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.api import scraper, articles, auth, translation, enhancement, scheduler, oauth, extraction, search, support, admin_formats, admin_clients, user_config
from app.config import get_settings
from app.database import get_db
from app.utils.logger import LoggerManager

# Use centralized LoggerManager (no duplicate basicConfig)
logger = LoggerManager.get_logger('main')

settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title="Swiftor API",
    description="Hard News & Soft News - Translation and Content Enhancement API",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Configure CORS - Use FRONTEND_URL from environment in production
# In development, allow localhost origins
allowed_origins = [
    settings.FRONTEND_URL,
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5175",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
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
app.include_router(extraction.router, prefix="/api/extract", tags=["extraction"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(support.router, prefix="/api/support", tags=["support"])
app.include_router(admin_formats.router, prefix="/api/admin/formats", tags=["admin-formats"])
app.include_router(admin_clients.router, prefix="/api/admin/clients", tags=["admin-clients"])
app.include_router(user_config.router, prefix="/api/user", tags=["user-config"])

# Mount uploads directory for serving attachments
uploads_dir = settings.UPLOADS_DIR
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads/support", StaticFiles(directory=str(uploads_dir)), name="support_uploads")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Swiftor API is running",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Detailed health check with database verification"""
    db_status = "connected"
    try:
        # Verify database connection
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "disconnected"  # Never expose raw error to unauthenticated callers
        return {
            "status": "unhealthy",
            "database": db_status,
            "services": {
                "scraper": "unknown",
                "translator": "unknown",
                "enhancer": "unknown"
            }
        }

    return {
        "status": "healthy",
        "database": db_status,
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
    logger.info("Swiftor API starting up...")

    # Create database tables
    from app.database import engine, Base
    from app.models import user, article, job, translation, enhancement, token_usage, user_config, support_ticket, password_reset, format_config, client_config
    from sqlalchemy import text, inspect

    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

    # Run migrations for existing tables
    logger.info("Checking for migrations...")
    with engine.connect() as conn:
        inspector = inspect(engine)
        if 'articles' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('articles')]
            if 'job_id' not in columns:
                logger.info("Adding job_id column to articles table...")
                conn.execute(text("ALTER TABLE articles ADD COLUMN job_id INTEGER REFERENCES jobs(id)"))
                conn.commit()
                logger.info("job_id column added successfully")
            else:
                logger.debug("job_id column already exists")

        # Update user limits from old default (600) to new default (450)
        if 'users' in inspector.get_table_names():
            result = conn.execute(text("""
                UPDATE users
                SET monthly_translation_limit = :new_limit,
                    monthly_enhancement_limit = :new_limit
                WHERE monthly_translation_limit = :old_limit
                   OR monthly_enhancement_limit = :old_limit
            """), {"old_limit": 600, "new_limit": 450})
            conn.commit()
            if result.rowcount > 0:
                logger.info(f"Updated {result.rowcount} users' limits from 600 to 450")
            else:
                logger.debug("No users needed limit updates")

    logger.info("Migrations complete")

    # Pre-warm Playwright browser — eliminates cold-start latency on first URL request
    try:
        from app.services.playwright_extractor import warm_up_browser
        await warm_up_browser()
    except Exception as e:
        logger.warning(f"Playwright browser pre-warm failed (non-fatal): {e}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown - close scheduler and database connections"""
    logger.info("Swiftor API shutting down...")

    # Stop scheduler service
    try:
        from app.services.scheduler_service import SchedulerService
        scheduler_service = SchedulerService()
        if scheduler_service.is_running:
            scheduler_service.stop()
            logger.info("Scheduler stopped successfully")
    except Exception as e:
        logger.warning(f"Error stopping scheduler: {e}")

    # Close database connections
    try:
        from app.database import engine
        engine.dispose()
        logger.info("Database connections closed successfully")
    except Exception as e:
        logger.warning(f"Error closing database connections: {e}")

    logger.info("Swiftor API shutdown complete")
