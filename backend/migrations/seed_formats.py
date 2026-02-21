"""
Seed Format Configurations Migration

Migrates format configurations from JSON to database.
Creates default client configuration for "Banglar Columbus".

Run from backend directory:
    python -m migrations.seed_formats
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal, engine, Base
from app.models.format_config import FormatConfig
from app.models.client_config import ClientConfig
from app.models.user import User


def load_json_config():
    """Load existing JSON configuration"""
    json_path = Path(__file__).parent.parent / 'app' / 'config' / 'formats' / 'bengali_news_styles.json'
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load JSON config: {e}")
        return None


def seed_hard_news(db, json_config, admin_id=None):
    """Create hard_news format config"""
    existing = db.query(FormatConfig).filter(FormatConfig.slug == "hard_news").first()
    if existing:
        print("  - hard_news already exists, skipping...")
        return existing

    hard_news_json = json_config.get("hard_news", {}) if json_config else {}

    hard_news = FormatConfig(
        slug="hard_news",
        display_name=hard_news_json.get("name", "Hard News"),
        description=hard_news_json.get("description", "Professional factual news reporting"),
        icon=hard_news_json.get("icon", "newspaper"),
        system_prompt=hard_news_json.get("system_prompt", """You are a journalist for Banglar Columbus.

Format:
**Headline** (bold, no prefix)
নিউজ ডেস্ক, বাংলার কলম্বাস (NOT bold!)
**Intro paragraph** (bold, 2-3 lines)
Body paragraphs (NOT bold, 2 lines max each)

Rules: NO subheads, byline NOT bold, body NOT bold, NO brackets."""),
        temperature=hard_news_json.get("temperature", 0.5),
        max_tokens=hard_news_json.get("max_tokens", 2000),
        rules={
            "max_sentences_per_paragraph": 2,
            "quotation_on_last_line": False,
            "allow_subheads": False,
            "intro_max_sentences": 3,
            "min_words": 220,
            "max_words": 450
        },
        is_active=True,
        created_by=admin_id
    )

    db.add(hard_news)
    print("  - Created hard_news format")
    return hard_news


def seed_soft_news(db, json_config, admin_id=None):
    """Create soft_news format config"""
    existing = db.query(FormatConfig).filter(FormatConfig.slug == "soft_news").first()
    if existing:
        print("  - soft_news already exists, skipping...")
        return existing

    soft_news_json = json_config.get("soft_news", {}) if json_config else {}

    soft_news = FormatConfig(
        slug="soft_news",
        display_name=soft_news_json.get("name", "Soft News"),
        description=soft_news_json.get("description", "Literary travel feature article"),
        icon=soft_news_json.get("icon", "book"),
        system_prompt=soft_news_json.get("system_prompt", """You are a feature writer for Banglar Columbus.

Format:
**Headline** (bold, no prefix)
নিউজ ডেস্ক, বাংলার কলম্বাস (NOT bold!)
**Intro 1** (bold, 2-4 lines - hook)
Intro 2 (NOT bold - REQUIRED before subhead!)
**Subhead** (bold, no brackets)
Body paragraphs (NOT bold, 2 lines max each)

Rules: Byline NOT bold, non-bold para required before first subhead, NO brackets."""),
        temperature=soft_news_json.get("temperature", 0.7),
        max_tokens=soft_news_json.get("max_tokens", 3000),
        rules={
            "max_sentences_per_paragraph": 2,
            "quotation_on_last_line": False,
            "allow_subheads": True,
            "intro_max_sentences": 4,
            "min_words": 400,
            "max_words": 800,
            "intro_paragraphs_before_subhead": 2
        },
        is_active=True,
        created_by=admin_id
    )

    db.add(soft_news)
    print("  - Created soft_news format")
    return soft_news


def seed_default_client(db, hard_news, soft_news):
    """Create default Banglar Columbus client config"""
    existing = db.query(ClientConfig).filter(ClientConfig.slug == "banglar_columbus").first()
    if existing:
        print("  - banglar_columbus client already exists, skipping...")
        return existing

    client = ClientConfig(
        name="Banglar Columbus",
        slug="banglar_columbus",
        allowed_format_ids=[hard_news.id, soft_news.id],
        default_format_id=hard_news.id,
        ui_settings={
            "show_content_preview": True,
            "workflow_type": "full",
            "show_format_selection": True,
            "app_title": "Swiftor"
        },
        display_overrides={},
        is_active=True
    )

    db.add(client)
    print("  - Created banglar_columbus client config")
    return client


def assign_users_to_default_client(db, client):
    """Assign all users without client config to default client"""
    users_without_client = db.query(User).filter(User.client_config_id == None).all()

    if not users_without_client:
        print("  - No users to assign")
        return

    for user in users_without_client:
        user.client_config_id = client.id

    print(f"  - Assigned {len(users_without_client)} users to banglar_columbus client")


def run_migration():
    """Run the migration"""
    print("\n" + "="*60)
    print("SEED FORMATS MIGRATION")
    print("="*60 + "\n")

    # Create tables if they don't exist
    print("1. Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("   Done.\n")

    # Load JSON config
    print("2. Loading JSON configuration...")
    json_config = load_json_config()
    if json_config:
        print("   Loaded bengali_news_styles.json")
    else:
        print("   Using default configuration")
    print()

    # Create database session
    db = SessionLocal()

    try:
        # Find admin user for created_by
        admin = db.query(User).filter(User.is_admin == True).first()
        admin_id = admin.id if admin else None

        # Seed formats
        print("3. Creating format configurations...")
        hard_news = seed_hard_news(db, json_config, admin_id)
        soft_news = seed_soft_news(db, json_config, admin_id)
        db.commit()
        db.refresh(hard_news)
        db.refresh(soft_news)
        print()

        # Seed default client
        print("4. Creating default client configuration...")
        client = seed_default_client(db, hard_news, soft_news)
        db.commit()
        db.refresh(client)
        print()

        # Assign users
        print("5. Assigning users to default client...")
        assign_users_to_default_client(db, client)
        db.commit()
        print()

        print("="*60)
        print("MIGRATION COMPLETE")
        print("="*60)
        print(f"\nFormats created: hard_news (ID: {hard_news.id}), soft_news (ID: {soft_news.id})")
        print(f"Default client: {client.name} (ID: {client.id})")
        print()

    except Exception as e:
        db.rollback()
        print(f"\nERROR: Migration failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_migration()
