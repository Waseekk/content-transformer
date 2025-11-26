"""
FastAPI Application Entry Point
Main application setup with middleware, routers, and startup events
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.database import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting Travel News SaaS Backend...")
    init_db()
    print("✅ Database initialized")
    yield
    # Shutdown
    print("👋 Shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Multi-user platform for news scraping, translation, and AI enhancement",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Register API routers
from app.api import auth, scraper, translation, enhancement, articles

app.include_router(auth.router, prefix=f"{settings.API_PREFIX}/auth", tags=["Authentication"])
app.include_router(scraper.router, prefix=f"{settings.API_PREFIX}/scraper", tags=["Scraper"])
app.include_router(translation.router, prefix=f"{settings.API_PREFIX}/translate", tags=["Translation"])
app.include_router(enhancement.router, prefix=f"{settings.API_PREFIX}/enhance", tags=["Enhancement"])
app.include_router(articles.router, prefix=f"{settings.API_PREFIX}/articles", tags=["Articles"])

# TODO: Add admin router in Phase 4
# from app.api import admin
# app.include_router(admin.router, prefix=f"{settings.API_PREFIX}/admin", tags=["Admin"])
