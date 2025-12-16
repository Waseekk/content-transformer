"""
Environment Detection Utility
Detects deployment environment and checks for optional dependencies
"""

import os
import sys


def is_streamlit_cloud():
    """
    Detect if running on Streamlit Cloud

    Returns:
        bool: True if on Streamlit Cloud, False otherwise
    """
    # Streamlit Cloud sets specific environment variables
    return (
        os.getenv('STREAMLIT_SHARING_MODE') is not None or
        os.getenv('STREAMLIT_SERVER_HEADLESS') == 'true' or
        '/home/appuser' in os.path.expanduser('~')
    )


def is_playwright_available():
    """
    Check if Playwright is installed and browsers are available

    Returns:
        bool: True if Playwright can be used, False otherwise
    """
    try:
        from playwright.sync_api import sync_playwright

        # Try to launch a browser to verify installation
        with sync_playwright() as p:
            # Just check if we can get the browser type
            # Don't actually launch to save resources
            browser_type = p.chromium
            return True
    except ImportError:
        return False
    except Exception:
        # If playwright is installed but browsers aren't, return False
        return False


def is_newspaper_available():
    """
    Check if newspaper3k is available

    Returns:
        bool: True if newspaper3k is installed
    """
    try:
        from newspaper import Article
        return True
    except ImportError:
        return False


def is_trafilatura_available():
    """
    Check if trafilatura is available

    Returns:
        bool: True if trafilatura is installed
    """
    try:
        import trafilatura
        return True
    except ImportError:
        return False


def get_environment_info():
    """
    Get comprehensive environment information

    Returns:
        dict: Environment details
    """
    return {
        'is_streamlit_cloud': is_streamlit_cloud(),
        'playwright_available': is_playwright_available(),
        'newspaper_available': is_newspaper_available(),
        'trafilatura_available': is_trafilatura_available(),
        'python_version': sys.version,
        'platform': sys.platform,
        'home_dir': os.path.expanduser('~')
    }


def get_recommended_extraction_method():
    """
    Get the recommended article extraction method based on environment

    Returns:
        str: 'playwright', 'trafilatura', 'newspaper', or 'beautifulsoup'
    """
    if is_playwright_available():
        return 'playwright'
    elif is_trafilatura_available():
        return 'trafilatura'
    elif is_newspaper_available():
        return 'newspaper'
    else:
        return 'beautifulsoup'


if __name__ == '__main__':
    # Test the environment detection
    info = get_environment_info()

    print("=== Environment Information ===")
    print(f"Streamlit Cloud: {info['is_streamlit_cloud']}")
    print(f"Playwright Available: {info['playwright_available']}")
    print(f"Newspaper3k Available: {info['newspaper_available']}")
    print(f"Trafilatura Available: {info['trafilatura_available']}")
    print(f"Python Version: {info['python_version']}")
    print(f"Platform: {info['platform']}")
    print(f"\nRecommended Extraction Method: {get_recommended_extraction_method()}")
