"""
Fix Format Rules Migration

Patches existing format_configs rows to include missing rules:
- hard_news: adds intro_max_sentences: 3
- soft_news: adds intro_max_sentences: 4
- hard_news_automate_content: sets full hard_news rules + appends structure to prompt

Run from backend directory:
    python -m migrations.fix_format_rules
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal, engine, Base
from app.models.format_config import FormatConfig


# Structure instructions to append to custom prompts that lack them
HARD_NEWS_STRUCTURE_INSTRUCTIONS = """

## আউটপুট ফরম্যাট (অবশ্যই মানতে হবে):
**শিরোনাম** (বোল্ড, কোনো প্রিফিক্স নেই)
নিউজ ডেস্ক, বাংলার কলম্বাস (বোল্ড নয়!)
**ভূমিকা** (বোল্ড, ২-৩ বাক্য)
বডি প্যারাগ্রাফ (বোল্ড নয়, প্রতিটি সর্বোচ্চ ২ লাইন)
কোনো সাবহেড নেই।"""

# Full hard_news rules for formats that have empty rules
HARD_NEWS_RULES = {
    "allow_subheads": False,
    "intro_max_sentences": 3,
    "min_words": 220,
    "max_words": 450,
    "max_sentences_per_paragraph": 2,
}


def fix_hard_news(db):
    """Add intro_max_sentences to hard_news rules"""
    fmt = db.query(FormatConfig).filter(FormatConfig.slug == "hard_news").first()
    if not fmt:
        print("  - hard_news not found, skipping")
        return

    rules = dict(fmt.rules or {})
    if "intro_max_sentences" in rules:
        print(f"  - hard_news already has intro_max_sentences={rules['intro_max_sentences']}, skipping")
        return

    rules["intro_max_sentences"] = 3
    fmt.rules = rules
    print(f"  - hard_news: added intro_max_sentences=3 -> {json.dumps(rules)}")


def fix_soft_news(db):
    """Add intro_max_sentences to soft_news rules"""
    fmt = db.query(FormatConfig).filter(FormatConfig.slug == "soft_news").first()
    if not fmt:
        print("  - soft_news not found, skipping")
        return

    rules = dict(fmt.rules or {})
    if "intro_max_sentences" in rules:
        print(f"  - soft_news already has intro_max_sentences={rules['intro_max_sentences']}, skipping")
        return

    rules["intro_max_sentences"] = 4
    fmt.rules = rules
    print(f"  - soft_news: added intro_max_sentences=4 -> {json.dumps(rules)}")


def fix_hard_news_automate_content(db):
    """Set full hard_news rules and append structure instructions to prompt"""
    fmt = db.query(FormatConfig).filter(FormatConfig.slug == "hard_news_automate_content").first()
    if not fmt:
        print("  - hard_news_automate_content not found, skipping")
        return

    # Fix rules: merge missing keys from HARD_NEWS_RULES (keep user's existing values)
    rules = dict(fmt.rules or {})
    merged = False
    for key, default_val in HARD_NEWS_RULES.items():
        if key not in rules:
            rules[key] = default_val
            print(f"  - hard_news_automate_content: added {key}={default_val}")
            merged = True
    if merged:
        fmt.rules = rules
        print(f"  - hard_news_automate_content: final rules -> {json.dumps(rules)}")
    else:
        print(f"  - hard_news_automate_content: all rule keys present, skipping")

    # Fix prompt: append structure instructions if missing
    prompt = fmt.system_prompt or ""
    if "বাংলার কলম্বাস" not in prompt and "নিউজ ডেস্ক" not in prompt:
        fmt.system_prompt = prompt + HARD_NEWS_STRUCTURE_INSTRUCTIONS
        print(f"  - hard_news_automate_content: appended structure instructions to prompt")
    else:
        print(f"  - hard_news_automate_content: prompt already has byline/structure, skipping")


def run_migration():
    """Run the migration"""
    print("\n" + "=" * 60)
    print("FIX FORMAT RULES MIGRATION")
    print("=" * 60 + "\n")

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        print("Patching format rules...\n")

        fix_hard_news(db)
        fix_soft_news(db)
        fix_hard_news_automate_content(db)

        db.commit()
        print("\n" + "=" * 60)
        print("MIGRATION COMPLETE")
        print("=" * 60)

        # Verify
        print("\nVerification:")
        for slug in ["hard_news", "soft_news", "hard_news_automate_content"]:
            fmt = db.query(FormatConfig).filter(FormatConfig.slug == slug).first()
            if fmt:
                print(f"  {slug}: rules = {json.dumps(fmt.rules or {})}")
            else:
                print(f"  {slug}: NOT FOUND")

    except Exception as e:
        db.rollback()
        print(f"\nERROR: Migration failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_migration()
