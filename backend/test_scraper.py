"""
Test script for scraper - Tests specific sites and shows output
Run from backend folder: python test_scraper.py
"""

import sys
import os

# Add the backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.scraper import MultiSiteScraper


def test_sites(site_names: list = None):
    """
    Test scraping specific sites and display results

    Args:
        site_names: List of site names to test. If None, tests all enabled sites.
    """
    print("\n" + "=" * 70)
    print("SCRAPER TEST")
    print("=" * 70)

    # Initialize scraper with specific sites or all
    if site_names:
        print(f"Testing sites: {', '.join(site_names)}")
        scraper = MultiSiteScraper(enabled_sites=site_names)
    else:
        print("Testing all enabled sites")
        scraper = MultiSiteScraper()

    print(f"Loaded {len(scraper.sites_config)} sites\n")

    total_articles = 0
    results = {}

    for site in scraper.sites_config:
        site_name = site['name']
        site_url = site['url']

        print("\n" + "-" * 70)
        print(f"SCRAPING: {site_name}")
        print(f"URL: {site_url}")
        print("-" * 70)

        try:
            articles = scraper.scrape_site(site)
            results[site_name] = len(articles)
            total_articles += len(articles)

            if articles:
                print(f"\n[OK] Found {len(articles)} articles:\n")

                # Show first 10 articles
                for i, art in enumerate(articles[:10], 1):
                    title = art.get('title', art.get('headline', 'No title'))
                    # Truncate long titles
                    if len(title) > 70:
                        title = title[:67] + "..."

                    link = art.get('link', art.get('article_url', 'No link'))

                    print(f"  {i:2d}. {title}")
                    print(f"      -> {link}")
                    print()

                if len(articles) > 10:
                    print(f"  ... and {len(articles) - 10} more articles")
            else:
                print("\n[WARNING] No articles found!")
                print("  -> Check if selectors need updating")

        except Exception as e:
            print(f"\n[ERROR] Failed to scrape: {e}")
            results[site_name] = f"ERROR: {e}"

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    for site_name, count in results.items():
        if isinstance(count, int):
            status = f"{count:4d} articles" if count > 0 else "  NO ARTICLES"
            print(f"  {site_name:20s} : {status}")
        else:
            print(f"  {site_name:20s} : {count}")

    print("-" * 70)
    print(f"  TOTAL: {total_articles} articles")
    print("=" * 70)

    return results


if __name__ == "__main__":
    # Default: test only skift, unwto, phocuswire
    # Change this list to test different sites
    TEST_SITES = ['skift', 'unwto', 'phocuswire']

    # To test all enabled sites, use:
    # TEST_SITES = None

    # To test specific sites, use:
    # TEST_SITES = ['tourism_review', 'skift', 'bbc_travel']

    test_sites(TEST_SITES)
