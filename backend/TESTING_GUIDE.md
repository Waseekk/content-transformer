# 🧪 Testing Guide - Travel News API

## **Quick Start (3 Easy Steps)**

### **Step 1: Start the Server**

**Option A: Double-click (Easiest)**
```
Double-click: start_server.bat
```

**Option B: Command Line**
```bash
cd backend
start_server.bat
```

**Option C: Manual**
```bash
cd backend
set DATABASE_URL=sqlite:///./test_fresh.db
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

You should see:
```
>>> Travel News API starting up...
>>> Creating database tables...
>>> Database tables created successfully!
INFO:     Uvicorn running on http://127.0.0.1:8000
```

---

### **Step 2: Run Automated Tests**

**In a NEW terminal window:**

```bash
cd backend
python test_api_manual.py
```

This will automatically test:
- ✅ Server health
- ✅ User login
- ✅ User profile
- ✅ Token balance
- ✅ Available formats
- ✅ Translation (optional - asks for permission)
- ✅ Enhancement (optional - asks for permission)
- ✅ API documentation

---

### **Step 3: Explore the API (Interactive)**

**Open your browser:**

**Swagger UI (Recommended):**
```
http://127.0.0.1:8000/docs
```

**ReDoc (Alternative):**
```
http://127.0.0.1:8000/redoc
```

**In Swagger UI, you can:**
1. Click "Authorize" button
2. Login to get your token
3. Test any endpoint interactively
4. See request/response examples

---

## **Manual Testing (Using curl or Postman)**

### **1. Health Check**
```bash
curl http://127.0.0.1:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "services": {
    "scraper": "available",
    "translator": "available",
    "enhancer": "available"
  }
}
```

---

### **2. Login**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"test@example.com\",\"password\":\"Test1234\"}"
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGci...",
  "refresh_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

**Save the access_token for next steps!**

---

### **3. Get User Profile**
```bash
curl -X GET http://127.0.0.1:8000/api/auth/me ^
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Expected Response:**
```json
{
  "id": 1,
  "email": "test@example.com",
  "full_name": "Test User",
  "subscription_tier": "free",
  "tokens_remaining": 5000,
  "tokens_used": 0,
  ...
}
```

---

### **4. Check Token Balance**
```bash
curl -X GET http://127.0.0.1:8000/api/auth/token-balance ^
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

### **5. Translate Text**
```bash
curl -X POST http://127.0.0.1:8000/api/translate/translate-text ^
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" ^
  -H "Content-Type: application/json" ^
  -d "{\"text\":\"The Maldives is a beautiful tropical paradise.\",\"title\":\"Maldives Travel\"}"
```

**This will:**
- Use ~500-1000 tokens
- Return Bengali translation
- Save to your history

---

### **6. Get Translation History**
```bash
curl -X GET http://127.0.0.1:8000/api/translate/ ^
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

### **7. Get Available Formats**
```bash
curl -X GET http://127.0.0.1:8000/api/enhance/formats ^
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

### **8. Generate Enhanced Content**
```bash
curl -X POST http://127.0.0.1:8000/api/enhance/ ^
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" ^
  -H "Content-Type: application/json" ^
  -d "{\"translation_id\":1,\"formats\":[\"hard_news\"]}"
```

---

## **Using Postman**

### **Setup:**
1. Create a new Collection: "Travel News API"
2. Set Collection Variable:
   - `base_url` = `http://127.0.0.1:8000`
   - `token` = (leave empty, will be filled after login)

### **Requests to Create:**

**1. Login**
- Method: POST
- URL: `{{base_url}}/api/auth/login`
- Body (JSON):
```json
{
  "email": "test@example.com",
  "password": "Test1234"
}
```
- Test Script (save token):
```javascript
pm.collectionVariables.set("token", pm.response.json().access_token);
```

**2. Get Profile**
- Method: GET
- URL: `{{base_url}}/api/auth/me`
- Headers:
  - `Authorization`: `Bearer {{token}}`

**3. Translate Text**
- Method: POST
- URL: `{{base_url}}/api/translate/translate-text`
- Headers:
  - `Authorization`: `Bearer {{token}}`
- Body (JSON):
```json
{
  "text": "Your text here...",
  "title": "Article Title"
}
```

---

## **Testing Checklist**

### **Basic Tests (No Token Usage)**
- [ ] Server health check
- [ ] Login (get JWT token)
- [ ] Get user profile
- [ ] Get token balance
- [ ] Get available formats
- [ ] Get translation history (empty initially)
- [ ] View API documentation

### **Token-Using Tests (Optional)**
- [ ] Translate text (~500-1000 tokens)
- [ ] Generate hard_news format (~500-1000 tokens)
- [ ] Check token balance again (should be reduced)
- [ ] View translation history (should show new entry)
- [ ] View enhancement history

### **Error Testing**
- [ ] Login with wrong password (should fail)
- [ ] Access endpoint without token (should return 401)
- [ ] Try to access premium format on free tier (should return 403)
- [ ] Translate empty text (should return 400)

---

## **Troubleshooting**

### **Server Won't Start**

**Problem:** Port 8000 already in use

**Solution:**
```bash
# Kill all Python processes
taskkill /F /IM python.exe

# Then start again
start_server.bat
```

---

### **Login Fails**

**Problem:** "User not found" or "Incorrect password"

**Solution:** Recreate test user
```bash
cd backend
set DATABASE_URL=sqlite:///./test_fresh.db
python create_test_user.py
```

---

### **"Insufficient tokens" Error**

**Problem:** Ran out of test tokens

**Solution:** Two options:

**Option 1: Create new user**
```python
# Edit create_test_user.py, change email to test2@example.com
python create_test_user.py
```

**Option 2: Reset tokens manually**
```bash
cd backend
sqlite3 test_fresh.db
UPDATE users SET tokens_remaining = 5000, tokens_used = 0 WHERE email = 'test@example.com';
.quit
```

---

### **Database Errors**

**Problem:** Schema mismatch or corrupted database

**Solution:** Delete and recreate
```bash
cd backend
del test_fresh.db
# Restart server (will create fresh database)
start_server.bat
# Recreate test user
python create_test_user.py
```

---

## **Advanced Testing**

### **Test URL Extraction + Translation**

**Note:** This requires a real, accessible URL

```bash
curl -X POST http://127.0.0.1:8000/api/translate/extract-and-translate ^
  -H "Authorization: Bearer YOUR_TOKEN" ^
  -H "Content-Type: application/json" ^
  -d "{\"url\":\"https://www.bbc.com/travel\"}"
```

**This will:**
1. Extract content from the URL
2. Translate to Bengali
3. Use ~1000-3000 tokens (depending on article length)

---

### **Test Multiple Formats**

```bash
curl -X POST http://127.0.0.1:8000/api/enhance/ ^
  -H "Authorization: Bearer YOUR_TOKEN" ^
  -H "Content-Type: application/json" ^
  -d "{\"translation_id\":1,\"formats\":[\"hard_news\",\"soft_news\"]}"
```

**Note:** `soft_news` requires Premium tier. Free tier only has `hard_news`.

---

## **Performance Testing**

### **Check Response Times**

```bash
# Windows (PowerShell)
Measure-Command { curl http://127.0.0.1:8000/health }

# Expected: < 100ms for health check
# Expected: 1-3 seconds for translation
# Expected: 5-10 seconds for enhancement
```

---

## **Database Inspection**

### **View Database Contents**

```bash
cd backend
sqlite3 test_fresh.db

# Show all tables
.tables

# View users
SELECT id, email, tokens_remaining, subscription_tier FROM users;

# View translations
SELECT id, original_title, tokens_used, created_at FROM translations LIMIT 5;

# View enhancements
SELECT id, format_type, headline, tokens_used FROM enhancements LIMIT 5;

# Exit
.quit
```

---

## **Next Steps After Testing**

Once all tests pass:

1. ✅ **Review API documentation** at `/docs`
2. ✅ **Test with real URLs** for extraction
3. ✅ **Try different content formats**
4. ✅ **Monitor token usage**
5. ✅ **Prepare for Docker deployment**

---

## **Quick Reference**

**Server:**
- Start: `start_server.bat`
- URL: `http://127.0.0.1:8000`
- Docs: `http://127.0.0.1:8000/docs`

**Test User:**
- Email: `test@example.com`
- Password: `Test1234`
- Tokens: 5,000

**Test Scripts:**
- Automated: `python test_api_manual.py`
- Integration: `python test_scraper_api.py`
- Create User: `python create_test_user.py`

**Database:**
- File: `test_fresh.db`
- View: `sqlite3 test_fresh.db`
- Reset: Delete file and restart server

---

**🎉 Happy Testing!**
