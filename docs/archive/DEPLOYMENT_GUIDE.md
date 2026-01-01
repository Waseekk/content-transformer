# 🚀 PRODUCTION DEPLOYMENT GUIDE - Hostinger/VPS

Complete guide to deploy your Travel News Translator to production using Docker.

---

## 📋 **PREREQUISITES**

On your server (Hostinger VPS / any Linux server):
- [x] Ubuntu 20.04+ or similar Linux distribution
- [x] Root or sudo access
- [x] Domain name pointing to your server IP (optional but recommended)

---

## 🔧 **STEP 1: PREPARE YOUR SERVER**

### **1.1 Connect to Server**
```bash
ssh root@your-server-ip
# Or with username:
ssh username@your-server-ip
```

### **1.2 Update System**
```bash
sudo apt update && sudo apt upgrade -y
```

### **1.3 Install Docker**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

### **1.4 Install Git** (if not installed)
```bash
sudo apt install git -y
```

---

## 📦 **STEP 2: DEPLOY YOUR APPLICATION**

### **2.1 Clone Repository**
```bash
# Create app directory
mkdir -p /var/www
cd /var/www

# Clone your repo (replace with your repo URL)
git clone https://github.com/YOUR_USERNAME/travel-news.git
cd travel-news
```

**OR Upload via SFTP:**
- Use FileZilla or WinSCP
- Upload entire project folder to `/var/www/travel-news/`

### **2.2 Configure Environment**
```bash
# Copy environment template
cp .env.production .env

# Edit environment file
nano .env
```

**Update these values in `.env`:**
```bash
# Database - Create strong password!
POSTGRES_PASSWORD=YOUR_SUPER_SECURE_PASSWORD_HERE_123!

# OpenAI API Key
OPENAI_API_KEY=sk-your-actual-openai-key-here

# JWT Secret - Generate with: openssl rand -hex 32
SECRET_KEY=abc123def456... # Paste generated secret

# Your domain
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

**Generate Secret Key:**
```bash
openssl rand -hex 32
# Copy output to SECRET_KEY in .env
```

Save and exit (Ctrl+X, Y, Enter)

### **2.3 Deploy with Docker**
```bash
# Make deploy script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

**This will:**
1. ✅ Build Docker images
2. ✅ Start PostgreSQL database
3. ✅ Start FastAPI backend
4. ✅ Start React frontend with Nginx
5. ✅ Run database migrations

---

## 🌐 **STEP 3: CONFIGURE DOMAIN (Optional but Recommended)**

### **3.1 Point Domain to Server**
In your domain registrar (e.g., Namecheap, GoDaddy):
- Create **A record**: `yourdomain.com` → `YOUR_SERVER_IP`
- Create **A record**: `www.yourdomain.com` → `YOUR_SERVER_IP`

Wait 5-60 minutes for DNS propagation.

### **3.2 Install SSL Certificate (HTTPS)**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Follow prompts:
# - Enter email
# - Agree to terms
# - Choose: Redirect HTTP to HTTPS (option 2)
```

SSL auto-renews! Certificate valid for 90 days.

### **3.3 Update CORS in .env**
```bash
nano .env

# Update:
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Restart services:
docker-compose -f docker-compose.prod.yml restart
```

---

## ✅ **STEP 4: VERIFY DEPLOYMENT**

### **4.1 Check Services Status**
```bash
docker-compose -f docker-compose.prod.yml ps

# Should show:
# ✅ travel_news_db        (healthy)
# ✅ travel_news_backend   (healthy)
# ✅ travel_news_frontend  (healthy)
```

### **4.2 View Logs**
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
```

### **4.3 Access Your App**
Open browser:
- **Without domain**: `http://YOUR_SERVER_IP`
- **With domain**: `https://yourdomain.com`
- **API Docs**: `https://yourdomain.com/api/docs`

---

## 🔐 **STEP 5: CREATE ADMIN USER**

```bash
# Enter backend container
docker-compose -f docker-compose.prod.yml exec backend bash

# Run Python shell
python

# Create admin user
from app.database import SessionLocal
from app.models.user import User
from passlib.context import CryptContext

db = SessionLocal()
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

admin = User(
    email='admin@yourdomain.com',
    hashed_password=pwd_context.hash('YourSecurePassword123!'),
    full_name='Admin User',
    is_admin=True,
    is_active=True,
    monthly_token_limit=1000000,
    tokens_used=0
)

db.add(admin)
db.commit()
print('Admin user created!')

# Exit Python
exit()

# Exit container
exit
```

---

## 🛠️ **MAINTENANCE COMMANDS**

### **View Logs**
```bash
docker-compose -f docker-compose.prod.yml logs -f
```

### **Restart Services**
```bash
docker-compose -f docker-compose.prod.yml restart
```

### **Stop Services**
```bash
docker-compose -f docker-compose.prod.yml down
```

### **Start Services**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### **Rebuild After Code Changes**
```bash
git pull origin main  # Pull latest code
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

### **Database Backup**
```bash
# Backup
docker-compose -f docker-compose.prod.yml exec db pg_dump -U postgres travel_news > backup_$(date +%Y%m%d).sql

# Restore
docker-compose -f docker-compose.prod.yml exec -T db psql -U postgres travel_news < backup_20231201.sql
```

### **View Resource Usage**
```bash
docker stats
```

---

## 🔥 **TROUBLESHOOTING**

### **Services not starting:**
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs

# Check specific service
docker-compose -f docker-compose.prod.yml logs backend
```

### **Port 80 already in use:**
```bash
# Find process using port 80
sudo lsof -i :80

# Kill process
sudo kill -9 <PID>

# Restart
docker-compose -f docker-compose.prod.yml up -d
```

### **Database connection errors:**
```bash
# Check database is running
docker-compose -f docker-compose.prod.yml ps db

# Check database logs
docker-compose -f docker-compose.prod.yml logs db

# Restart database
docker-compose -f docker-compose.prod.yml restart db
```

### **Frontend shows 502 Bad Gateway:**
- Backend is not ready yet (wait 30 seconds)
- Check backend logs: `docker-compose -f docker-compose.prod.yml logs backend`

### **CORS errors:**
- Update `ALLOWED_ORIGINS` in `.env`
- Restart: `docker-compose -f docker-compose.prod.yml restart`

---

## 🔒 **SECURITY CHECKLIST**

- [x] Strong database password set
- [x] Secret key generated (not default)
- [x] SSL certificate installed (HTTPS)
- [x] Firewall configured (allow only 80, 443, 22)
- [x] Default passwords changed
- [x] Database not exposed (port 5432 not public)
- [x] CORS properly configured

### **Configure Firewall (UFW)**
```bash
# Enable firewall
sudo ufw enable

# Allow SSH (IMPORTANT - don't lock yourself out!)
sudo ufw allow 22

# Allow HTTP and HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Check status
sudo ufw status
```

---

## 📊 **MONITORING**

### **Check Disk Space**
```bash
df -h
```

### **Check Memory**
```bash
free -h
```

### **Check CPU**
```bash
top
# Press 'q' to exit
```

### **Docker Resource Usage**
```bash
docker stats
```

---

## 🚀 **PERFORMANCE OPTIMIZATION**

### **1. Enable Docker Logging Limits**
Edit `docker-compose.prod.yml`:
```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### **2. Database Optimization**
```bash
# Enter database container
docker-compose -f docker-compose.prod.yml exec db psql -U postgres travel_news

# Run vacuum
VACUUM ANALYZE;

# Exit
\q
```

### **3. Monitor Logs Size**
```bash
du -sh backend/logs/
# If too large, clean old logs:
find backend/logs/ -name "*.log" -mtime +30 -delete
```

---

## 🔄 **UPDATING YOUR APP**

### **Deploy New Version**
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Run migrations (if any)
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

---

## 📞 **QUICK REFERENCE**

| Task | Command |
|------|---------|
| Deploy | `./deploy.sh` |
| View logs | `docker-compose -f docker-compose.prod.yml logs -f` |
| Restart | `docker-compose -f docker-compose.prod.yml restart` |
| Stop | `docker-compose -f docker-compose.prod.yml down` |
| Start | `docker-compose -f docker-compose.prod.yml up -d` |
| Update | `git pull && docker-compose -f docker-compose.prod.yml up -d --build` |
| Backup DB | `docker-compose -f docker-compose.prod.yml exec db pg_dump -U postgres travel_news > backup.sql` |

---

## ✅ **DEPLOYMENT CHECKLIST**

- [ ] Server prepared (Docker installed)
- [ ] Repository cloned/uploaded
- [ ] .env configured (strong passwords!)
- [ ] ./deploy.sh executed successfully
- [ ] All services healthy (docker-compose ps)
- [ ] Domain pointed to server IP
- [ ] SSL certificate installed
- [ ] CORS configured correctly
- [ ] Admin user created
- [ ] Can login and test features
- [ ] Firewall configured
- [ ] Backups scheduled

---

## 🎉 **CONGRATULATIONS!**

Your Travel News Translator is now LIVE in production!

**Access URLs:**
- Frontend: `https://yourdomain.com`
- API Docs: `https://yourdomain.com/api/docs`
- Admin Panel: Create admin via Python shell

**Next Steps:**
1. Test all features
2. Set up regular database backups
3. Monitor server resources
4. Configure monitoring (optional: Sentry, New Relic)

---

**Need Help?** Check logs: `docker-compose -f docker-compose.prod.yml logs -f`
