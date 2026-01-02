"""
Utility script to enable scraper sites for a user
Run this to give users access to scraping
"""

import sys
from app.database import SessionLocal
from app.models.user import User
from app.models.user_config import UserConfig


def enable_sites_for_user(email: str, sites: list = None):
    """Enable scraper sites for a user"""

    if sites is None:
        # Enable all available sites by default
        sites = ["newsuk_travel", "tourism_review", "travelandleisure"]

    db = SessionLocal()

    try:
        # Find user
        user = db.query(User).filter(User.email == email).first()

        if not user:
            print(f"User not found: {email}")
            return

        # Get or create user config
        config = db.query(UserConfig).filter(UserConfig.user_id == user.id).first()

        if not config:
            print(f"User config not found for {email}")
            return

        # Update enabled sites
        config.enabled_sites = sites
        db.commit()

        print(f"Successfully enabled sites for {email}:")
        for site in sites:
            print(f"  - {site}")

    finally:
        db.close()


def list_users():
    """List all users"""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"\nTotal users: {len(users)}\n")
        for user in users:
            config = db.query(UserConfig).filter(UserConfig.user_id == user.id).first()
            enabled_sites = config.enabled_sites if config else []
            print(f"- {user.email}")
            print(f"  Tier: {user.subscription_tier}")
            print(f"  Enabled sites: {enabled_sites}")
            print()
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) > 1 and (sys.argv[1] in ["--list", "-l"]):
        list_users()
    elif len(sys.argv) > 1:
        user_email = sys.argv[1]
        enable_sites_for_user(user_email)
    else:
        print("Usage: python enable_sites_for_user.py <user_email>")
        print("\nOr list all users:")
        print("python enable_sites_for_user.py --list")
        print()
