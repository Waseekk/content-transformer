"""
Debug registration to see actual error
"""

from app.database import SessionLocal
from app.schemas.auth import UserRegister
from app.services.auth_service import AuthService

# Test data
test_user = UserRegister(
    email="debug@example.com",
    password="Test1234",
    full_name="Debug User",
    subscription_tier="free"
)

print("Testing user registration...")
print(f"Email: {test_user.email}")
print(f"Tier: {test_user.subscription_tier}\n")

try:
    db = SessionLocal()
    result = AuthService.register_user(db, test_user)
    print("✅ Registration successful!")
    print(f"User ID: {result.id}")
    print(f"Tokens: {result.tokens_remaining}/{result.tokens_total}")
    print(f"Access Token: {result.access_token[:30]}...")

except Exception as e:
    print(f"❌ Registration failed!")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")

    import traceback
    print("\nFull traceback:")
    traceback.print_exc()

finally:
    db.close()
