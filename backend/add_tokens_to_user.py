"""
Add tokens to a user for testing
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.user import User

def add_tokens(email: str, tokens: int):
    """Add tokens to user"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"[ERROR] User {email} not found!")
            return

        old_tokens = user.tokens_remaining
        old_limit = user.monthly_token_limit

        # Use the User model's add_tokens method
        user.add_tokens(tokens)

        db.commit()
        db.refresh(user)

        print(f"[SUCCESS] Updated {email}:")
        print(f"   Old tokens remaining: {old_tokens}")
        print(f"   New tokens remaining: {user.tokens_remaining}")
        print(f"   Old monthly limit: {old_limit}")
        print(f"   New monthly limit: {user.monthly_token_limit}")
        print(f"   Subscription: {user.subscription_tier}")
        print(f"   Status: {user.subscription_status}")

    except Exception as e:
        print(f"[ERROR] Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Add 100,000 tokens to test user
    add_tokens("test@example.com", 100000)

    print("\n[SUCCESS] Test user now has 100,000 tokens!")
    print("You can now use translation and enhancement features!")
