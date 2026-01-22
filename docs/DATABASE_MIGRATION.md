# Database Migration Guide

Safe migration from SQLite to PostgreSQL for Swiftor deployment.

## Table of Contents

1. [Overview](#overview)
2. [Pre-Migration Checklist](#pre-migration-checklist)
3. [Backup SQLite Data](#backup-sqlite-data)
4. [Export to JSON](#export-to-json)
5. [PostgreSQL Setup](#postgresql-setup)
6. [Import Data](#import-data)
7. [Verify Migration](#verify-migration)
8. [Rollback Plan](#rollback-plan)

---

## Overview

**Current State:** SQLite database at `backend/app.db`

**Target State:** PostgreSQL 16 in Docker container

**Data to Preserve:**
| Table | Purpose |
|-------|---------|
| users | User accounts and credentials |
| articles | Scraped news articles |
| jobs | Scraping job history |
| translations | Translation records |
| enhancements | Enhanced content |
| token_usage | API token tracking |

---

## Pre-Migration Checklist

- [ ] Backup current SQLite database
- [ ] Export all tables to JSON
- [ ] Note current row counts for verification
- [ ] Test migration on copy first
- [ ] Have rollback plan ready

---

## Backup SQLite Data

### Step 1: Create Backup Directory
```bash
mkdir -p backups/$(date +%Y%m%d)
```

### Step 2: Copy SQLite Database
```bash
cp backend/app.db backups/$(date +%Y%m%d)/app.db.backup
```

### Step 3: Verify Backup
```bash
sqlite3 backups/$(date +%Y%m%d)/app.db.backup "SELECT COUNT(*) FROM users;"
```

---

## Export to JSON

### Automated Export Script

Create `scripts/export_sqlite.py`:
```python
import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = "backend/app.db"
OUTPUT_DIR = f"backups/{datetime.now().strftime('%Y%m%d')}"

Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall()]

data = {}
counts = {}

for table in tables:
    cursor.execute(f"SELECT * FROM {table}")
    rows = cursor.fetchall()
    data[table] = [dict(row) for row in rows]
    counts[table] = len(rows)
    print(f"Exported {table}: {counts[table]} rows")

# Save to JSON
with open(f"{OUTPUT_DIR}/full_backup.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, default=str, ensure_ascii=False)

# Save counts for verification
with open(f"{OUTPUT_DIR}/row_counts.json", "w") as f:
    json.dump(counts, f, indent=2)

print(f"\nBackup saved to {OUTPUT_DIR}/")
print(f"Total tables: {len(tables)}")
print(f"Total rows: {sum(counts.values())}")

conn.close()
```

### Run Export
```bash
cd "E:\data_insightopia\travel_news\v1_all\0. travel_news_"
python scripts/export_sqlite.py
```

---

## PostgreSQL Setup

### Docker-Based (Recommended)

PostgreSQL is configured in `docker-compose.yml`:
```yaml
postgres:
  image: postgres:16-alpine
  environment:
    POSTGRES_USER: swiftor
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    POSTGRES_DB: swiftor
  volumes:
    - postgres_data:/var/lib/postgresql/data
```

Tables are created automatically by SQLAlchemy on first run.

### Manual Setup (Alternative)
```bash
# Start only PostgreSQL
docker compose up -d postgres

# Wait for startup
sleep 5

# Connect and verify
docker compose exec postgres psql -U swiftor -d swiftor -c "\dt"
```

---

## Import Data

### Automated Import Script

Create `scripts/import_postgres.py`:
```python
import json
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://swiftor:password@localhost:5432/swiftor")
BACKUP_FILE = "backups/YYYYMMDD/full_backup.json"  # Update date

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

with open(BACKUP_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

# Import order (respect foreign keys)
import_order = [
    "users",
    "articles",
    "jobs",
    "translations",
    "enhancements",
    "token_usage"
]

session = Session()

for table in import_order:
    if table not in data:
        print(f"Skipping {table} (not in backup)")
        continue

    rows = data[table]
    if not rows:
        print(f"Skipping {table} (empty)")
        continue

    # Build insert statement
    columns = rows[0].keys()
    placeholders = ", ".join([f":{col}" for col in columns])
    columns_str = ", ".join(columns)

    sql = text(f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders}) ON CONFLICT DO NOTHING")

    for row in rows:
        try:
            session.execute(sql, row)
        except Exception as e:
            print(f"Error importing {table}: {e}")

    session.commit()
    print(f"Imported {table}: {len(rows)} rows")

session.close()
print("\nImport complete!")
```

### Run Import
```bash
# Set database URL
export DATABASE_URL="postgresql://swiftor:yourpassword@localhost:5432/swiftor"

# Run import
python scripts/import_postgres.py
```

---

## Verify Migration

### Step 1: Compare Row Counts
```bash
# Get PostgreSQL counts
docker compose exec postgres psql -U swiftor -d swiftor -c "
SELECT 'users' as table_name, COUNT(*) FROM users
UNION ALL SELECT 'articles', COUNT(*) FROM articles
UNION ALL SELECT 'jobs', COUNT(*) FROM jobs
UNION ALL SELECT 'translations', COUNT(*) FROM translations
UNION ALL SELECT 'enhancements', COUNT(*) FROM enhancements;
"
```

Compare with `row_counts.json` from backup.

### Step 2: Spot Check Data
```bash
# Check a few users
docker compose exec postgres psql -U swiftor -d swiftor -c "SELECT id, email FROM users LIMIT 5;"

# Check recent articles
docker compose exec postgres psql -U swiftor -d swiftor -c "SELECT id, title FROM articles ORDER BY created_at DESC LIMIT 5;"
```

### Step 3: Test Application
1. Start all services: `docker compose up -d`
2. Login with existing user
3. View existing articles
4. Create new translation

### Verification Checklist
- [ ] Row counts match SQLite backup
- [ ] User login works
- [ ] Existing articles visible
- [ ] New operations work
- [ ] No errors in logs

---

## Rollback Plan

### Scenario 1: Migration Failed, Keep SQLite

If PostgreSQL import fails:
1. Stop Docker services
2. Revert to SQLite configuration
3. Restore from backup if needed

```bash
# Stop services
docker compose down

# Restore SQLite backup
cp backups/YYYYMMDD/app.db.backup backend/app.db

# Update DATABASE_URL to SQLite (if changed)
# Restart with local dev setup
```

### Scenario 2: PostgreSQL Issues After Migration

If issues appear after successful migration:

```bash
# Export current PostgreSQL data first!
docker compose exec postgres pg_dump -U swiftor swiftor > emergency_backup.sql

# Restore from last good PostgreSQL backup
cat last_good_backup.sql | docker compose exec -T postgres psql -U swiftor -d swiftor

# Or restore from SQLite
python scripts/import_postgres.py
```

### Keep Backups For 30 Days

```bash
# Don't delete backups until PostgreSQL is verified stable
ls -la backups/

# Only after 30 days of stable operation:
rm -rf backups/YYYYMMDD/
```

---

## Notes

### Password Hashing
- User passwords are stored as bcrypt hashes
- Hashes are portable between SQLite and PostgreSQL
- No re-hashing needed

### Datetime Fields
- SQLite stores datetimes as strings
- PostgreSQL uses native TIMESTAMP
- SQLAlchemy handles conversion automatically

### Auto-Increment IDs
- PostgreSQL uses SERIAL/BIGSERIAL
- Sequence may need reset after import:
```sql
SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));
SELECT setval('articles_id_seq', (SELECT MAX(id) FROM articles));
```

### Foreign Keys
- Import in correct order (users first, then dependent tables)
- Use ON CONFLICT DO NOTHING to handle duplicates
