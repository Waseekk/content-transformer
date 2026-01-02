# Travel News SaaS - Deployment Guide

## 🚀 Quick Start with Docker

### Prerequisites
- Docker and Docker Compose installed
- OpenAI API key

### 1. Environment Setup

**Backend:**
```bash
cd backend
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY and SECRET_KEY
```

**Frontend:**
```bash
cd frontend
# Update VITE_API_URL in .env.production to your backend URL
```

### 2. Deploy with Docker Compose

From the project root:

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

The application will be available at:
- **Frontend:** http://localhost
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### 3. Create Test User

```bash
# Access backend container
docker exec -it travel-news-backend bash

# Run the test user creation script
python create_test_user.py
```

Default test credentials:
- Email: test@example.com
- Password: Test1234
- Tokens: 5000 (free tier)

---

## 📦 Manual Deployment

### Backend (FastAPI)

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export SECRET_KEY="your-secret-key"
export OPENAI_API_KEY="your-api-key"
export DATABASE_URL="sqlite:///./test_fresh.db"

# Run migrations (if needed)
# alembic upgrade head

# Start server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend (React + Vite)

```bash
cd frontend

# Install dependencies
npm install

# Build for production
npm run build

# Serve with a static server (e.g., serve, nginx)
npx serve -s dist -l 3000
```

---

## ☁️ Cloud Deployment Options

### Option 1: DigitalOcean App Platform

1. **Backend:**
   - Create new app from GitHub repository
   - Select `/backend` as source directory
   - Build command: `pip install -r requirements.txt`
   - Run command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Add environment variables (OPENAI_API_KEY, SECRET_KEY, etc.)

2. **Frontend:**
   - Create new static site from GitHub repository
   - Select `/frontend` as source directory
   - Build command: `npm run build`
   - Output directory: `dist`
   - Update `VITE_API_URL` to backend URL

### Option 2: AWS (EC2 + S3)

1. **Backend on EC2:**
   - Launch Ubuntu 22.04 instance
   - Install Docker and Docker Compose
   - Clone repository
   - Run `docker-compose up -d`
   - Configure security group (port 8000)

2. **Frontend on S3 + CloudFront:**
   - Build frontend: `npm run build`
   - Upload `dist/` to S3 bucket
   - Enable static website hosting
   - Set up CloudFront distribution
   - Update `VITE_API_URL` to EC2 backend URL

### Option 3: Heroku

**Backend:**
```bash
cd backend
heroku create travel-news-backend
heroku config:set OPENAI_API_KEY=your-key
heroku config:set SECRET_KEY=your-secret
git push heroku main
```

**Frontend:**
```bash
cd frontend
# Update VITE_API_URL to Heroku backend URL
npm run build
# Deploy to Netlify/Vercel or Heroku static buildpack
```

### Option 4: Render

1. Create new Web Service for backend
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

2. Create new Static Site for frontend
   - Build command: `npm run build`
   - Publish directory: `dist`

---

## 🔒 Production Checklist

### Security
- [ ] Change `SECRET_KEY` to a random 32+ character string
- [ ] Set `DEBUG=false` in production
- [ ] Use environment variables for all secrets
- [ ] Enable HTTPS/SSL
- [ ] Set up CORS properly
- [ ] Enable rate limiting
- [ ] Use strong database passwords (if using PostgreSQL)

### Performance
- [ ] Enable Gzip compression
- [ ] Set up CDN for frontend
- [ ] Configure caching headers
- [ ] Enable database connection pooling
- [ ] Set up Redis for caching (optional)

### Monitoring
- [ ] Set up error tracking (Sentry, Rollbar)
- [ ] Configure logging aggregation
- [ ] Set up uptime monitoring
- [ ] Create database backups
- [ ] Monitor API rate limits

### Database
- [ ] For production, consider PostgreSQL instead of SQLite
- [ ] Set up automated backups
- [ ] Enable WAL mode for SQLite (if using SQLite)
- [ ] Run migrations on deployment

---

## 🛠️ Troubleshooting

### Backend won't start
- Check if `sites_config.json` exists in `backend/config/`
- Verify environment variables are set correctly
- Check logs: `docker-compose logs backend`
- Ensure port 8000 is not in use

### Frontend can't connect to backend
- Verify `VITE_API_URL` is correct
- Check CORS settings in backend
- Test backend API: `curl http://localhost:8000/health`
- Check browser console for errors

### Database errors
- Ensure `test_fresh.db` has write permissions
- For Docker, check volume mounts
- Run migrations if schema changed

---

## 📊 Monitoring & Maintenance

### Health Checks
- Backend: `http://localhost:8000/health`
- Frontend: `http://localhost/`

### Logs
```bash
# View all logs
docker-compose logs

# View backend logs only
docker-compose logs backend

# Follow logs in real-time
docker-compose logs -f backend
```

### Database Backup
```bash
# Backup SQLite database
docker exec travel-news-backend cp test_fresh.db backup_$(date +%Y%m%d).db

# Copy backup to host
docker cp travel-news-backend:/app/backup_$(date +%Y%m%d).db ./
```

---

## 🔄 Updates & Maintenance

### Update Application
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose up -d --build

# Check status
docker-compose ps
```

### Scale Services (if needed)
```bash
# Run multiple backend instances
docker-compose up -d --scale backend=3
```

---

## 📞 Support

For issues or questions:
1. Check logs: `docker-compose logs`
2. Review environment variables
3. Verify API keys are valid
4. Check network connectivity
5. Review backend API docs: `http://localhost:8000/docs`
