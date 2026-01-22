# ============================================================
# Swiftor Dockerfile - Multi-Stage Build
# ============================================================
# Stages:
# 1. frontend-builder - Build React app with Vite
# 2. backend - Python API with Playwright/Chromium
# 3. frontend - Nginx serving static files + reverse proxy
# ============================================================

# ------------------------------------------------------------
# Stage 1: Frontend Builder
# ------------------------------------------------------------
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files for dependency caching
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci --silent

# Copy frontend source
COPY frontend/ ./

# Build production bundle
ENV NODE_ENV=production
RUN npm run build

# ------------------------------------------------------------
# Stage 2: Backend (FastAPI + Playwright)
# ------------------------------------------------------------
FROM python:3.12-slim AS backend

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    # Playwright settings for Docker
    PLAYWRIGHT_BROWSERS_PATH=/app/.playwright

WORKDIR /app

# Install system dependencies for Playwright and general use
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Playwright dependencies
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    libatspi2.0-0 \
    # Fonts for rendering
    fonts-liberation \
    fonts-noto-cjk \
    # Utilities
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r swiftor && useradd -r -g swiftor swiftor

# Copy backend requirements
COPY backend/requirements.txt ./requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir playwright

# Install Playwright Chromium browser
RUN playwright install chromium && \
    playwright install-deps chromium

# Copy backend application
COPY backend/app ./app

# Copy config files
COPY config ./config

# Create directories for runtime data
RUN mkdir -p /app/data /app/logs /app/translations && \
    chown -R swiftor:swiftor /app

# Switch to non-root user
USER swiftor

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start FastAPI with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ------------------------------------------------------------
# Stage 3: Frontend (Nginx)
# ------------------------------------------------------------
FROM nginx:alpine AS frontend

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx config
COPY docker/nginx.conf /etc/nginx/nginx.conf

# Copy built frontend from builder stage
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html

# Expose HTTP/HTTPS ports
EXPOSE 80 443

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
