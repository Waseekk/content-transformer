"""
Migration: Add hard_news_generic format

Identical to hard_news_automate_content — same prompt, rules, tokens.
Only difference: byline is 'নিউজ ডেস্ক' (no newspaper name).

Run from backend directory:
    python -m migrations.add_hard_news_generic
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models.format_config import FormatConfig


def run():
    db = SessionLocal()
    try:
        existing = db.query(FormatConfig).filter(FormatConfig.slug == "hard_news_generic").first()
        if existing:
            print("hard_news_generic already exists, skipping.")
            return

        # Copy everything from hard_news_automate_content, only change byline
        src = db.query(FormatConfig).filter(FormatConfig.slug == "hard_news_automate_content").first()
        if not src:
            print("ERROR: hard_news_automate_content not found in DB. Run seed_formats first.")
            return

        new_prompt = src.system_prompt.replace(
            'নিউজ ডেস্ক, বাংলার কলম্বাস',
            'নিউজ ডেস্ক'
        ).replace(
            'আপনি "বাংলার কলম্বাস" পত্রিকার একজন অভিজ্ঞ ভ্রমণ সাংবাদিক। এটি বাংলাদেশের একটি ভ্রমণ-বিশেষায়িত পত্রিকা — ভিসা নীতি, এয়ারলাইন খবর, গন্তব্য পরিচিতি, ট্রাভেল গাইড — সব কিছুই আপনার লেখার বিষয়।',
            'আপনি একজন অভিজ্ঞ ভ্রমণ সাংবাদিক। ভিসা নীতি, এয়ারলাইন খবর, গন্তব্য পরিচিতি, ট্রাভেল গাইড — সব কিছুই আপনার লেখার বিষয়।'
        )

        fmt = FormatConfig(
            slug="hard_news_generic",
            display_name="হার্ড নিউজ (জেনেরিক)",
            description="Professional hard news — neutral byline (নিউজ ডেস্ক only, no newspaper name)",
            icon="newspaper",
            system_prompt=new_prompt,
            temperature=src.temperature,
            max_tokens=src.max_tokens,
            rules=src.rules.copy() if src.rules else {},
            is_active=True
        )

        db.add(fmt)
        db.commit()
        print("Created hard_news_generic format.")
        print(f"  temperature: {fmt.temperature}, max_tokens: {fmt.max_tokens}, rules: {fmt.rules}")
        print("To enable for a client, add its ID to that client's allowed_format_ids via Admin > Clients.")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()
