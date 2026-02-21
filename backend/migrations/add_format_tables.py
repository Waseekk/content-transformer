"""
Add Format Configuration Tables Migration

Adds the new tables and columns for multi-tenant format configuration:
- format_configs table
- client_configs table
- users.client_config_id column

Run from backend directory:
    python -m migrations.add_format_tables
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text, inspect
from app.database import engine, Base


def run_migration():
    """Run the migration to add format config tables"""
    print("\n" + "="*60)
    print("ADD FORMAT TABLES MIGRATION")
    print("="*60 + "\n")

    with engine.connect() as conn:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        # Step 1: Create format_configs table if not exists
        print("1. Checking format_configs table...")
        if 'format_configs' not in existing_tables:
            print("   Creating format_configs table...")
            conn.execute(text("""
                CREATE TABLE format_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    slug VARCHAR(50) UNIQUE NOT NULL,
                    display_name VARCHAR(100) NOT NULL,
                    description TEXT,
                    icon VARCHAR(50) DEFAULT 'newspaper',
                    system_prompt TEXT NOT NULL,
                    temperature FLOAT DEFAULT 0.5,
                    max_tokens INTEGER DEFAULT 4096,
                    rules JSON DEFAULT '{}',
                    is_active BOOLEAN DEFAULT 1 NOT NULL,
                    created_by INTEGER REFERENCES users(id),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
                )
            """))
            conn.execute(text("CREATE INDEX ix_format_configs_slug ON format_configs(slug)"))
            conn.commit()
            print("   Done!")
        else:
            print("   Table already exists, skipping...")

        # Step 2: Create client_configs table if not exists
        print("\n2. Checking client_configs table...")
        if 'client_configs' not in existing_tables:
            print("   Creating client_configs table...")
            conn.execute(text("""
                CREATE TABLE client_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL,
                    slug VARCHAR(50) UNIQUE NOT NULL,
                    allowed_format_ids JSON DEFAULT '[]',
                    default_format_id INTEGER REFERENCES format_configs(id),
                    ui_settings JSON DEFAULT '{}',
                    display_overrides JSON DEFAULT '{}',
                    is_active BOOLEAN DEFAULT 1 NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
                )
            """))
            conn.execute(text("CREATE INDEX ix_client_configs_slug ON client_configs(slug)"))
            conn.commit()
            print("   Done!")
        else:
            print("   Table already exists, skipping...")

        # Step 3: Add client_config_id column to users table if not exists
        print("\n3. Checking users.client_config_id column...")
        if 'users' in existing_tables:
            columns = [col['name'] for col in inspector.get_columns('users')]
            if 'client_config_id' not in columns:
                print("   Adding client_config_id column to users table...")
                conn.execute(text("""
                    ALTER TABLE users ADD COLUMN client_config_id INTEGER REFERENCES client_configs(id)
                """))
                conn.commit()
                print("   Done!")
            else:
                print("   Column already exists, skipping...")
        else:
            print("   Users table not found!")

        print("\n" + "="*60)
        print("MIGRATION COMPLETE")
        print("="*60)
        print("\nNext step: Run 'python -m migrations.seed_formats' to seed default formats")
        print()


if __name__ == "__main__":
    run_migration()
