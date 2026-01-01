"""
Comprehensive API Endpoint Testing Script
Tests all endpoints and reports which are working/broken
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://127.0.0.1:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}→ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

# Test results storage
results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

def test_endpoint(name: str, method: str, url: str, headers: Dict = None, data: Dict = None, expected_status: int = 200):
    """Test an API endpoint"""
    try:
        print_info(f"Testing: {name}")

        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")

        if response.status_code == expected_status:
            print_success(f"{name} - Status {response.status_code}")
            results["passed"].append(name)
            return True, response
        else:
            print_error(f"{name} - Expected {expected_status}, got {response.status_code}")
            print_error(f"Response: {response.text[:200]}")
            results["failed"].append(f"{name} (Status: {response.status_code})")
            return False, response

    except Exception as e:
        print_error(f"{name} - Exception: {str(e)}")
        results["failed"].append(f"{name} (Exception: {str(e)})")
        return False, None

def main():
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Travel News API - Comprehensive Endpoint Test{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")

    # Track token
    access_token = None

    # ========================================================================
    # 1. HEALTH CHECK ENDPOINTS
    # ========================================================================
    print(f"\n{Colors.YELLOW}[1] HEALTH CHECK ENDPOINTS{Colors.END}")
    print("-" * 60)

    test_endpoint(
        "Root Endpoint",
        "GET",
        f"{BASE_URL}/"
    )

    test_endpoint(
        "Health Check",
        "GET",
        f"{BASE_URL}/health"
    )

    # ========================================================================
    # 2. AUTHENTICATION ENDPOINTS
    # ========================================================================
    print(f"\n{Colors.YELLOW}[2] AUTHENTICATION ENDPOINTS{Colors.END}")
    print("-" * 60)

    # Register new user (should fail - user already exists)
    success, response = test_endpoint(
        "Register User (existing)",
        "POST",
        f"{BASE_URL}/api/auth/register",
        data={
            "email": "test@example.com",
            "password": "Test1234",
            "full_name": "Test User"
        },
        expected_status=400
    )

    # Login
    success, response = test_endpoint(
        "Login",
        "POST",
        f"{BASE_URL}/api/auth/login",
        data={
            "username": "test@example.com",
            "password": "Test1234"
        }
    )

    if success and response:
        data = response.json()
        access_token = data.get("access_token")
        print_success(f"Access token obtained: {access_token[:20]}...")
    else:
        print_error("Failed to get access token - remaining tests will fail")
        return

    headers = {"Authorization": f"Bearer {access_token}"}

    # Get current user
    test_endpoint(
        "Get Current User",
        "GET",
        f"{BASE_URL}/api/auth/me",
        headers=headers
    )

    # ========================================================================
    # 3. TRANSLATION ENDPOINTS
    # ========================================================================
    print(f"\n{Colors.YELLOW}[3] TRANSLATION ENDPOINTS{Colors.END}")
    print("-" * 60)

    # Translate raw text
    success, response = test_endpoint(
        "Translate Raw Text",
        "POST",
        f"{BASE_URL}/api/translate/translate-text",
        headers=headers,
        data={
            "text": "This is a test article about travel destinations.",
            "title": "Test Article",
            "save_to_history": True
        },
        expected_status=201
    )

    translation_id = None
    if success and response:
        translation_id = response.json().get("id")
        print_info(f"Translation ID: {translation_id}")

    # List translations
    test_endpoint(
        "List Translations",
        "GET",
        f"{BASE_URL}/api/translate/?page=1&page_size=20",
        headers=headers
    )

    # Get specific translation
    if translation_id:
        test_endpoint(
            "Get Translation by ID",
            "GET",
            f"{BASE_URL}/api/translate/{translation_id}",
            headers=headers
        )

    # ========================================================================
    # 4. ENHANCEMENT ENDPOINTS
    # ========================================================================
    print(f"\n{Colors.YELLOW}[4] ENHANCEMENT ENDPOINTS{Colors.END}")
    print("-" * 60)

    # Get available formats
    test_endpoint(
        "Get Available Formats",
        "GET",
        f"{BASE_URL}/api/enhance/formats",
        headers=headers
    )

    # Enhance content (single format)
    success, response = test_endpoint(
        "Enhance Content (Single Format)",
        "POST",
        f"{BASE_URL}/api/enhance/enhance",
        headers=headers,
        data={
            "original_text": "মালদ্বীপ একটি সুন্দর পর্যটন গন্তব্য।",
            "format_types": ["facebook"],
            "save_to_history": True
        },
        expected_status=201
    )

    enhancement_id = None
    if success and response:
        enhancement_id = response.json().get("id")
        print_info(f"Enhancement ID: {enhancement_id}")

    # List enhancements
    test_endpoint(
        "List Enhancements",
        "GET",
        f"{BASE_URL}/api/enhance/?page=1&page_size=20",
        headers=headers
    )

    # Get specific enhancement
    if enhancement_id:
        test_endpoint(
            "Get Enhancement by ID",
            "GET",
            f"{BASE_URL}/api/enhance/{enhancement_id}",
            headers=headers
        )

    # ========================================================================
    # 5. SCRAPER ENDPOINTS
    # ========================================================================
    print(f"\n{Colors.YELLOW}[5] SCRAPER ENDPOINTS{Colors.END}")
    print("-" * 60)

    # Get available sites
    test_endpoint(
        "Get Available Sites",
        "GET",
        f"{BASE_URL}/api/scraper/sites",
        headers=headers
    )

    # Get enabled sites
    test_endpoint(
        "Get Enabled Sites",
        "GET",
        f"{BASE_URL}/api/scraper/sites/enabled",
        headers=headers
    )

    # ========================================================================
    # 6. ARTICLES ENDPOINTS
    # ========================================================================
    print(f"\n{Colors.YELLOW}[6] ARTICLES ENDPOINTS{Colors.END}")
    print("-" * 60)

    # List articles
    test_endpoint(
        "List Articles",
        "GET",
        f"{BASE_URL}/api/articles/?page=1&page_size=20",
        headers=headers
    )

    # Get article stats
    test_endpoint(
        "Get Article Stats",
        "GET",
        f"{BASE_URL}/api/articles/stats",
        headers=headers
    )

    # ========================================================================
    # FINAL REPORT
    # ========================================================================
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}TEST SUMMARY{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")

    print(f"{Colors.GREEN}✓ PASSED: {len(results['passed'])}{Colors.END}")
    for test in results['passed']:
        print(f"  - {test}")

    if results['failed']:
        print(f"\n{Colors.RED}✗ FAILED: {len(results['failed'])}{Colors.END}")
        for test in results['failed']:
            print(f"  - {test}")

    if results['warnings']:
        print(f"\n{Colors.YELLOW}⚠ WARNINGS: {len(results['warnings'])}{Colors.END}")
        for test in results['warnings']:
            print(f"  - {test}")

    total = len(results['passed']) + len(results['failed'])
    success_rate = (len(results['passed']) / total * 100) if total > 0 else 0

    print(f"\n{Colors.BLUE}Success Rate: {success_rate:.1f}% ({len(results['passed'])}/{total}){Colors.END}\n")

if __name__ == "__main__":
    main()
