"""
Show full article data from scraper
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.scraper import MultiSiteScraper


def show_article_details(site_name: str, limit: int = 2):
    """Show full details of scraped articles"""

    print(f"\n{'='*70}")
    print(f"ARTICLE DETAILS: {site_name}")
    print(f"{'='*70}\n")

    scraper = MultiSiteScraper(enabled_sites=[site_name])

    if not scraper.sites_config:
        print(f"Site '{site_name}' not found or disabled")
        return

    site = scraper.sites_config[0]
    articles = scraper.scrape_site(site)

    print(f"Found {len(articles)} articles. Showing first {limit}:\n")

    for i, article in enumerate(articles[:limit], 1):
        print(f"\n{'-'*70}")
        print(f"ARTICLE {i}")
        print(f"{'-'*70}")

        # Print each field
        for key, value in article.items():
            if isinstance(value, str) and len(value) > 100:
                value = value[:100] + "..."
            print(f"  {key:20s}: {value}")

        print()


if __name__ == "__main__":
    # Show 2 articles from unwto (the working one)
    show_article_details('unwto', limit=2)
