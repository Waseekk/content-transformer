"""
Create a test user directly in the database
"""

import sys
sys.path.insert(0, '.')

from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.middleware.auth import get_password_hash

# Create database tables
Base.metadata.create_all(bind=engine)

# Create session
db = SessionLocal()

try:
    # Check if user exists
    existing_user = db.query(User).filter(User.email == "test@example.com").first()

    if existing_user:
        print("Test user already exists!")
        print(f"Email: {existing_user.email}")
        print(f"ID: {existing_user.id}")
        print(f"Tokens remaining: {existing_user.tokens_remaining}")
    else:
        # Create new user
        test_user = User(
            email="test@example.com",
            hashed_password=get_password_hash("Test1234"),
            full_name="Test User",
            subscription_tier="free",
            subscription_status="active",
            tokens_remaining=5000,
            monthly_token_limit=5000
        )

        db.add(test_user)
        db.commit()
        db.refresh(test_user)

        print("Test user created successfully!")
        print(f"Email: {test_user.email}")
        print(f"ID: {test_user.id}")
        print(f"Tokens remaining: {test_user.tokens_remaining}")
        print(f"Subscription tier: {test_user.subscription_tier}")

finally:
    db.close()
