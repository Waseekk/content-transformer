"""
Script to create an admin user or promote existing user to admin
Run from backend directory: python create_admin.py
"""

import sys
import os

# Add the backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app.models.user import User
from app.middleware.auth import get_password_hash
from app.config import get_settings

settings = get_settings()


def create_admin_user(email: str, password: str, full_name: str = "Admin"):
    """Create a new admin user"""
    db = SessionLocal()
    try:
        # Check if user exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"User {email} already exists!")
            print(f"  - Is Admin: {existing.is_admin}")
            print(f"  - Is Active: {existing.is_active}")

            # Offer to promote to admin
            if not existing.is_admin:
                confirm = input("Do you want to promote this user to admin? (y/n): ")
                if confirm.lower() == 'y':
                    existing.is_admin = True
                    db.commit()
                    print(f"User {email} is now an admin!")
            return existing

        # Create new admin user
        new_user = User(
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            is_admin=True,
            is_active=True,
            is_verified=True,
            subscription_tier="enterprise",
            subscription_status="active",
            monthly_token_limit=settings.DEFAULT_MONTHLY_TOKENS,
            tokens_remaining=settings.DEFAULT_MONTHLY_TOKENS,
            tokens_used=0,
            monthly_enhancement_limit=settings.DEFAULT_MONTHLY_ENHANCEMENTS,
            enhancements_used_this_month=0
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        print(f"\nAdmin user created successfully!")
        print(f"  Email: {email}")
        print(f"  Password: {password}")
        print(f"  Is Admin: True")
        print(f"  Token Limit: {new_user.monthly_token_limit:,}")
        print(f"  Enhancement Limit: {new_user.monthly_enhancement_limit}")

        return new_user

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        return None
    finally:
        db.close()


def promote_to_admin(email: str):
    """Promote existing user to admin"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"User {email} not found!")
            return None

        user.is_admin = True
        db.commit()
        print(f"User {email} is now an admin!")
        return user

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        return None
    finally:
        db.close()


def list_users():
    """List all users"""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        if not users:
            print("No users found in database.")
            return

        print(f"\n{'='*60}")
        print(f"{'ID':<5} {'Email':<30} {'Admin':<8} {'Active':<8}")
        print(f"{'='*60}")
        for u in users:
            print(f"{u.id:<5} {u.email:<30} {str(u.is_admin):<8} {str(u.is_active):<8}")
        print(f"{'='*60}")
        print(f"Total: {len(users)} users")

    finally:
        db.close()


if __name__ == "__main__":
    print("\n" + "="*50)
    print("  SWIFTOR ADMIN USER MANAGEMENT")
    print("="*50)

    print("\nOptions:")
    print("1. Create new admin user")
    print("2. Promote existing user to admin")
    print("3. List all users")
    print("4. Quick create (test@example.com / Test1234)")

    choice = input("\nEnter choice (1-4): ").strip()

    if choice == "1":
        email = input("Enter email: ").strip()
        password = input("Enter password (min 8 chars): ").strip()
        full_name = input("Enter full name (optional): ").strip() or "Admin"
        create_admin_user(email, password, full_name)

    elif choice == "2":
        email = input("Enter email to promote: ").strip()
        promote_to_admin(email)

    elif choice == "3":
        list_users()

    elif choice == "4":
        # Quick create the demo user as admin
        create_admin_user("test@example.com", "Test1234", "Test Admin")

    else:
        print("Invalid choice")
