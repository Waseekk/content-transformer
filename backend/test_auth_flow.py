"""
Test Authentication Flow
Complete test of register → login → protected routes
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"


def print_test(name, status="RUNNING"):
    """Print test status"""
    symbols = {"RUNNING": "🔄", "PASS": "✅", "FAIL": "❌"}
    print(f"{symbols.get(status, '●')} {name}")


def test_auth_flow():
    """Test complete authentication flow"""

    print("\n" + "="*60)
    print("TESTING AUTHENTICATION FLOW")
    print("="*60 + "\n")

    # Test data
    test_user = {
        "email": f"test_{datetime.now().timestamp()}@example.com",
        "password": "Test1234",
        "full_name": "Test User",
        "subscription_tier": "free"
    }

    # Step 1: Register
    print_test("1. User Registration", "RUNNING")
    try:
        response = requests.post(
            f"{API_URL}/auth/register",
            json=test_user
        )

        if response.status_code == 201:
            user_data = response.json()
            access_token = user_data["access_token"]
            refresh_token = user_data["refresh_token"]

            print_test("1. User Registration", "PASS")
            print(f"   User ID: {user_data['id']}")
            print(f"   Email: {user_data['email']}")
            print(f"   Tokens: {user_data['tokens_remaining']}/{user_data['tokens_total']}")
            print(f"   Access Token: {access_token[:20]}...")
        else:
            print_test("1. User Registration", "FAIL")
            print(f"   Error: {response.json()}")
            return False

    except Exception as e:
        print_test("1. User Registration", "FAIL")
        print(f"   Exception: {e}")
        return False

    # Step 2: Login
    print("\n" + "-"*60 + "\n")
    print_test("2. User Login", "RUNNING")
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json={
                "email": test_user["email"],
                "password": test_user["password"]
            }
        )

        if response.status_code == 200:
            login_data = response.json()
            access_token = login_data["access_token"]

            print_test("2. User Login", "PASS")
            print(f"   Last Login: {login_data.get('last_login', 'N/A')}")
        else:
            print_test("2. User Login", "FAIL")
            print(f"   Error: {response.json()}")
            return False

    except Exception as e:
        print_test("2. User Login", "FAIL")
        print(f"   Exception: {e}")
        return False

    # Step 3: Access Protected Route (Get Me)
    print("\n" + "-"*60 + "\n")
    print_test("3. Protected Route (/auth/me)", "RUNNING")
    try:
        response = requests.get(
            f"{API_URL}/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        if response.status_code == 200:
            me_data = response.json()

            print_test("3. Protected Route (/auth/me)", "PASS")
            print(f"   User: {me_data['email']}")
            print(f"   Active: {me_data['is_active']}")
            print(f"   Admin: {me_data['is_admin']}")
        else:
            print_test("3. Protected Route (/auth/me)", "FAIL")
            print(f"   Error: {response.json()}")
            return False

    except Exception as e:
        print_test("3. Protected Route (/auth/me)", "FAIL")
        print(f"   Exception: {e}")
        return False

    # Step 4: Get Token Balance
    print("\n" + "-"*60 + "\n")
    print_test("4. Token Balance Check", "RUNNING")
    try:
        response = requests.get(
            f"{API_URL}/auth/token-balance",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        if response.status_code == 200:
            balance_data = response.json()

            print_test("4. Token Balance Check", "PASS")
            print(f"   Tokens Remaining: {balance_data['tokens_remaining']}")
            print(f"   Total Tokens: {balance_data['tokens_total']}")
            print(f"   Can Use: {balance_data['can_use_tokens']}")
            print(f"   Tier: {balance_data['subscription_tier']}")
        else:
            print_test("4. Token Balance Check", "FAIL")
            print(f"   Error: {response.json()}")
            return False

    except Exception as e:
        print_test("4. Token Balance Check", "FAIL")
        print(f"   Exception: {e}")
        return False

    # Step 5: Refresh Token
    print("\n" + "-"*60 + "\n")
    print_test("5. Token Refresh", "RUNNING")
    try:
        response = requests.post(
            f"{API_URL}/auth/refresh",
            json={"refresh_token": refresh_token}
        )

        if response.status_code == 200:
            new_tokens = response.json()

            print_test("5. Token Refresh", "PASS")
            print(f"   New Access Token: {new_tokens['access_token'][:20]}...")
            print(f"   Token Type: {new_tokens['token_type']}")
        else:
            print_test("5. Token Refresh", "FAIL")
            print(f"   Error: {response.json()}")
            return False

    except Exception as e:
        print_test("5. Token Refresh", "FAIL")
        print(f"   Exception: {e}")
        return False

    # Step 6: Invalid Token Test
    print("\n" + "-"*60 + "\n")
    print_test("6. Invalid Token (should fail)", "RUNNING")
    try:
        response = requests.get(
            f"{API_URL}/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"}
        )

        if response.status_code == 401:
            print_test("6. Invalid Token (should fail)", "PASS")
            print(f"   Correctly rejected with 401 Unauthorized")
        else:
            print_test("6. Invalid Token (should fail)", "FAIL")
            print(f"   Should have returned 401, got {response.status_code}")
            return False

    except Exception as e:
        print_test("6. Invalid Token (should fail)", "FAIL")
        print(f"   Exception: {e}")
        return False

    # All tests passed
    print("\n" + "="*60)
    print("✅ ALL AUTHENTICATION TESTS PASSED!")
    print("="*60 + "\n")

    return True


if __name__ == "__main__":
    print("\nStarting authentication flow test...")
    print("Make sure the FastAPI server is running at http://localhost:8000\n")

    try:
        # Check if server is running
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code != 200:
            print("❌ Server not responding correctly")
            print("   Run: uvicorn app.main:app --reload")
            exit(1)

    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server at http://localhost:8000")
        print("   Run: uvicorn app.main:app --reload")
        exit(1)

    # Run tests
    success = test_auth_flow()

    if success:
        print("✅ Authentication system is fully functional!\n")
        exit(0)
    else:
        print("❌ Some tests failed\n")
        exit(1)
