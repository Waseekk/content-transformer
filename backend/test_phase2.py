"""
Phase 2 API Testing Script
Tests all Phase 2 endpoints: Translation, Enhancement, Articles, and Scraper
"""

import requests
import time
import json
from datetime import datetime

# Base URL
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api"

# Test credentials
TEST_EMAIL = f"phase2_test_{int(time.time())}@example.com"
TEST_PASSWORD = "Test1234"

# Global variables
access_token = None
user_id = None
translation_id = None
enhancement_job_id = None
scraper_job_id = None
article_id = None


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 60)
    print(f"{title}")
    print("=" * 60)


def print_result(success, message, data=None):
    """Print test result"""
    status = "PASS" if success else "FAIL"
    print(f"[{status}] {message}")
    if data:
        print(f"   Data: {json.dumps(data, indent=2)[:200]}...")


def register_user():
    """Register a new test user"""
    global access_token, user_id

    print_section("1. USER REGISTRATION")

    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/auth/register",
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "full_name": "Phase 2 Test User",
            "subscription_tier": "premium"  # Premium for all formats
        }
    )

    if response.status_code == 201:
        data = response.json()
        access_token = data["access_token"]
        user_id = data["id"]
        print_result(True, "User registered successfully", {
            "email": data["email"],
            "tier": data["subscription_tier"],
            "tokens": f"{data['tokens_remaining']}/{data['tokens_total']}"
        })
        return True
    else:
        print_result(False, f"Registration failed: {response.text}")
        return False


def test_translation():
    """Test translation endpoint"""
    global translation_id

    print_section("2. TRANSLATION API")

    # Sample pasted content
    pasted_content = """
    Travel News Today

    New UNESCO World Heritage Site Announced in Bangladesh
    By Sarah Johnson | November 26, 2025

    The United Nations Educational, Scientific and Cultural Organization (UNESCO)
    has announced a new World Heritage Site in Bangladesh. The Sundarbans mangrove
    forest has been recognized for its unique biodiversity and ecological importance.

    This designation is expected to boost tourism significantly in the region,
    bringing economic benefits to local communities while promoting conservation efforts.

    Local tour operators are already preparing new packages to showcase the
    magnificent wildlife and natural beauty of this UNESCO-protected site.
    """

    headers = {"Authorization": f"Bearer {access_token}"}

    print("\n2.1 Translate Content")
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/translate/",
        headers=headers,
        json={
            "pasted_content": pasted_content,
            "target_lang": "bn",
            "provider": "openai"
        }
    )

    if response.status_code == 201:
        data = response.json()
        translation_id = data["id"]
        print_result(True, "Translation successful", {
            "id": data["id"],
            "headline": data["headline"][:50] + "...",
            "tokens_used": data["tokens_used"]
        })
    else:
        print_result(False, f"Translation failed: {response.text}")
        return False

    print("\n2.2 Get Translation List")
    response = requests.get(
        f"{BASE_URL}{API_PREFIX}/translate/?page=1&per_page=10",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        print_result(True, "Translation list retrieved", {
            "total": data["total"],
            "page": data["page"],
            "count": len(data["translations"])
        })
    else:
        print_result(False, f"Failed to get list: {response.text}")

    print("\n2.3 Get Translation Detail")
    response = requests.get(
        f"{BASE_URL}{API_PREFIX}/translate/{translation_id}",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        print_result(True, "Translation detail retrieved", {
            "id": data["id"],
            "content_length": len(data["content"])
        })
    else:
        print_result(False, f"Failed to get detail: {response.text}")

    return True


def test_enhancement():
    """Test enhancement endpoint"""
    global enhancement_job_id

    print_section("3. ENHANCEMENT API")

    headers = {"Authorization": f"Bearer {access_token}"}

    print("\n3.1 Get Available Formats")
    response = requests.get(
        f"{BASE_URL}{API_PREFIX}/enhance/formats/available",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        print_result(True, "Available formats retrieved", {
            "tier": data["tier"],
            "formats": data["available_formats"]
        })
    else:
        print_result(False, f"Failed to get formats: {response.text}")

    print("\n3.2 Create Enhancement Job")
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/enhance/",
        headers=headers,
        json={
            "translation_id": translation_id,
            "formats": ["facebook", "blog"],  # Test with 2 formats for speed
            "provider": "openai",
            "save_to_files": True
        }
    )

    if response.status_code == 202:
        data = response.json()
        enhancement_job_id = data["job_id"]
        print_result(True, "Enhancement job created", {
            "job_id": data["job_id"],
            "status": data["status"],
            "formats": data["formats_requested"]
        })
    else:
        print_result(False, f"Failed to create job: {response.text}")
        return False

    print("\n3.3 Poll Enhancement Status")
    for i in range(30):  # Poll for up to 30 seconds
        time.sleep(2)
        response = requests.get(
            f"{BASE_URL}{API_PREFIX}/enhance/status/{enhancement_job_id}",
            headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {data['status']} | Progress: {data['progress']}% | {data.get('status_message', '')}")

            if data['status'] == 'completed':
                print_result(True, "Enhancement completed", {
                    "formats_completed": data["formats_completed"],
                    "total_formats": data["total_formats"]
                })
                break
            elif data['status'] == 'failed':
                print_result(False, f"Enhancement failed: {data.get('error')}")
                return False
        else:
            print_result(False, f"Failed to get status: {response.text}")
            break

    print("\n3.4 Get Enhancement Result")
    response = requests.get(
        f"{BASE_URL}{API_PREFIX}/enhance/result/{enhancement_job_id}",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        print_result(True, "Enhancement result retrieved", {
            "job_id": data["job_id"],
            "total_tokens": data["total_tokens"],
            "formats_count": len(data["formats"])
        })
    else:
        print_result(False, f"Failed to get result: {response.text}")

    print("\n3.5 Get Enhancement List")
    response = requests.get(
        f"{BASE_URL}{API_PREFIX}/enhance/?page=1&per_page=10",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        print_result(True, "Enhancement list retrieved", {
            "total": data["total"],
            "count": len(data["enhancements"])
        })
    else:
        print_result(False, f"Failed to get list: {response.text}")

    return True


def test_scraper():
    """Test scraper endpoint"""
    global scraper_job_id, article_id

    print_section("4. SCRAPER API")

    headers = {"Authorization": f"Bearer {access_token}"}

    print("\n4.1 Get User Sites")
    response = requests.get(
        f"{BASE_URL}{API_PREFIX}/scraper/sites",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        print_result(True, "User sites retrieved", {
            "enabled_sites": len(data["enabled_sites"]),
            "available_sites": len(data["available_sites"])
        })
    else:
        print_result(False, f"Failed to get sites: {response.text}")

    print("\n4.2 Trigger Scraping")
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/scraper/run",
        headers=headers,
        json={
            "sites": None,  # All enabled sites
            "save_to_db": True
        }
    )

    if response.status_code == 202:
        data = response.json()
        scraper_job_id = data["job_id"]
        print_result(True, "Scraper job created", {
            "job_id": data["job_id"],
            "status": data["status"]
        })
    else:
        print_result(False, f"Failed to trigger scraping: {response.text}")
        return False

    print("\n4.3 Poll Scraper Status")
    for i in range(60):  # Poll for up to 2 minutes
        time.sleep(2)
        response = requests.get(
            f"{BASE_URL}{API_PREFIX}/scraper/status/{scraper_job_id}",
            headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {data['status']} | Progress: {data['progress']}% | {data.get('status_message', '')}")

            if data['status'] == 'completed':
                print_result(True, "Scraping completed", {
                    "articles_count": data.get("articles_count", 0)
                })
                break
            elif data['status'] == 'failed':
                print_result(False, f"Scraping failed: {data.get('error')}")
                return False
        else:
            print_result(False, f"Failed to get status: {response.text}")
            break

    return True


def test_articles():
    """Test articles endpoint"""
    global article_id

    print_section("5. ARTICLES API")

    headers = {"Authorization": f"Bearer {access_token}"}

    print("\n5.1 Get Article Sources")
    response = requests.get(
        f"{BASE_URL}{API_PREFIX}/articles/sources/list",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        print_result(True, "Article sources retrieved", {
            "total_sources": data["total_sources"],
            "sources": [s["name"] for s in data["sources"][:3]]
        })
    else:
        print_result(False, f"Failed to get sources: {response.text}")

    print("\n5.2 Get Articles List")
    response = requests.get(
        f"{BASE_URL}{API_PREFIX}/articles/?days=7&page=1&per_page=10",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        print_result(True, "Articles list retrieved", {
            "total": data["total"],
            "count": len(data["articles"]),
            "date_range_days": data["date_range_days"]
        })

        # Get first article ID if available
        if data["articles"]:
            article_id = data["articles"][0]["id"]
    else:
        print_result(False, f"Failed to get articles: {response.text}")
        return False

    if article_id:
        print("\n5.3 Get Article Detail")
        response = requests.get(
            f"{BASE_URL}{API_PREFIX}/articles/{article_id}",
            headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            print_result(True, "Article detail retrieved", {
                "id": data["id"],
                "source": data["source"],
                "headline": data["headline"][:50] + "..."
            })
        else:
            print_result(False, f"Failed to get article detail: {response.text}")

    return True


def test_token_balance():
    """Test token balance"""
    print_section("6. TOKEN BALANCE CHECK")

    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(
        f"{BASE_URL}{API_PREFIX}/auth/token-balance",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        print_result(True, "Token balance retrieved", {
            "remaining": data["tokens_remaining"],
            "total": data["tokens_total"],
            "tier": data["subscription_tier"],
            "can_use": data["can_use_tokens"]
        })
    else:
        print_result(False, f"Failed to get balance: {response.text}")


def main():
    """Run all tests"""
    print("\n")
    print("*" * 60)
    print(" PHASE 2 API TESTING")
    print(" Travel News SaaS Backend")
    print("*" * 60)
    print(f"\nBase URL: {BASE_URL}")
    print(f"Test Email: {TEST_EMAIL}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # Run tests in sequence
        if not register_user():
            print("\n❌ Registration failed. Stopping tests.")
            return

        if not test_translation():
            print("\n⚠️  Translation tests failed. Continuing with other tests...")

        if translation_id and not test_enhancement():
            print("\n⚠️  Enhancement tests failed. Continuing with other tests...")

        if not test_scraper():
            print("\n⚠️  Scraper tests failed. Continuing with other tests...")

        test_articles()

        test_token_balance()

        print_section("TEST SUMMARY")
        print("✅ Phase 2 testing completed!")
        print(f"\nTest user: {TEST_EMAIL}")
        print(f"Translation ID: {translation_id}")
        print(f"Enhancement Job ID: {enhancement_job_id}")
        print(f"Scraper Job ID: {scraper_job_id}")
        print("\nCheck the Swagger docs at: http://localhost:8000/docs")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
