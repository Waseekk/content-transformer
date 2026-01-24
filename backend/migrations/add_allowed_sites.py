"""
Migration: Add allowed_sites column to user_configs table

Run this script to add the allowed_sites column:
    python -m migrations.add_allowed_sites

Or from the backend directory:
    python migrations/add_allowed_sites.py
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import engine, SessionLocal


def migrate():
    """Add allowed_sites column to user_configs table"""
    db = SessionLocal()
    try:
        # Check if column already exists
        check_query = text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'user_configs' AND column_name = 'allowed_sites'
        """)

        # For SQLite, use a different approach
        try:
            result = db.execute(check_query).fetchone()
            column_exists = result is not None
        except Exception:
            # SQLite doesn't support information_schema, check with pragma
            try:
                pragma_result = db.execute(text("PRAGMA table_info(user_configs)")).fetchall()
                column_exists = any(row[1] == 'allowed_sites' for row in pragma_result)
            except Exception:
                column_exists = False

        if column_exists:
            print("Column 'allowed_sites' already exists. Skipping migration.")
            return True

        # Add the column
        # SQLite syntax (also works for PostgreSQL with slight modification)
        alter_query = text("""
            ALTER TABLE user_configs
            ADD COLUMN allowed_sites JSON DEFAULT '[]'
        """)

        db.execute(alter_query)
        db.commit()

        print("Successfully added 'allowed_sites' column to user_configs table.")
        print("Default value: [] (empty list = access to all sites)")
        return True

    except Exception as e:
        print(f"Migration failed: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def rollback():
    """Remove allowed_sites column (rollback)"""
    db = SessionLocal()
    try:
        # Note: SQLite doesn't support DROP COLUMN directly
        # For SQLite, you'd need to recreate the table
        alter_query = text("""
            ALTER TABLE user_configs
            DROP COLUMN allowed_sites
        """)

        db.execute(alter_query)
        db.commit()

        print("Successfully removed 'allowed_sites' column from user_configs table.")
        return True

    except Exception as e:
        print(f"Rollback failed: {e}")
        print("Note: SQLite doesn't support DROP COLUMN. Manual table recreation needed.")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--rollback":
        rollback()
    else:
        migrate()
