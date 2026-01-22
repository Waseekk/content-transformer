#!/usr/bin/env python3
"""Export SQLite database to JSON backup."""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / "backend" / "app.db"
OUTPUT_DIR = Path(__file__).parent.parent / "backups" / datetime.now().strftime("%Y%m%d")

def export_database():
    """Export all tables from SQLite to JSON."""
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}")
        return False

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cursor.fetchall()]

    data = {}
    counts = {}

    for table in tables:
        try:
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            data[table] = [dict(row) for row in rows]
            counts[table] = len(rows)
            print(f"Exported {table}: {counts[table]} rows")
        except Exception as e:
            print(f"Error exporting {table}: {e}")

    # Save to JSON
    backup_file = OUTPUT_DIR / "full_backup.json"
    with open(backup_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str, ensure_ascii=False)

    # Save counts for verification
    counts_file = OUTPUT_DIR / "row_counts.json"
    with open(counts_file, "w") as f:
        json.dump(counts, f, indent=2)

    print(f"\n{'='*50}")
    print(f"Backup saved to: {OUTPUT_DIR}")
    print(f"Total tables: {len(tables)}")
    print(f"Total rows: {sum(counts.values())}")
    print(f"{'='*50}")

    conn.close()
    return True


if __name__ == "__main__":
    export_database()
