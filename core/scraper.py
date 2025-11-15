"""
Multi-Site News Scraper Module
Supports scraping multiple websites configured in sites_config.json
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
from datetime import datetime
from pathlib import Path
import time
from typing import List, Dict, Optional, Tuple

# Import settings and logger
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config.settings import SCRAPER_CONFIG, RAW_DATA_DIR, SITES_CONFIG_PATH
from utils.logger import get_scraper_logger

logger = get_scraper_logger()


class NewsScraperStatus:
    """Track scraper status"""

    def __init__(self):
        self.is_running = False
        self.progress = 0
        self.status_message = "Idle"
        self.articles_count = 0
        self.current_site = ""
        self.error = None
        self.start_time = None
        self.end_time = None
        self.site_stats = {}  # Track per-site statistics

    def start(self):
        """Start scraping"""
        self.is_running = True
        self.progress = 0
        self.status_message = "Starting scraper..."
        self.articles_count = 0
        self.error = None
        self.start_time = datetime.now()
        self.end_time = None
        self.site_stats = {}
        logger.info("=" * 80)
        logger.info("SCRAPER STARTED")
        logger.info("=" * 80)

    def update(self, progress, message, site="", count=0):
        """Update status"""
        self.progress = progress
        self.status_message = message
        self.current_site = site
        self.articles_count = count
        logger.debug(f"Status update: {message} ({progress}%)")

    def add_site_stats(self, site_name: str, article_count: int):
        """Record statistics for a scraped site"""
        self.site_stats[site_name] = article_count
        logger.info(f"[OK] {site_name}: {article_count} articles scraped")

    def complete(self, articles_count):
        """Complete scraping"""
        self.is_running = False
        self.progress = 100
        self.status_message = f"Completed! Scraped {articles_count} articles"
        self.articles_count = articles_count
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()

        logger.info("=" * 80)
        logger.info("SCRAPING COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        logger.info(f"Total articles scraped: {articles_count}")
        logger.info(f"Total duration: {duration:.2f} seconds")
        logger.info("")
        logger.info("PER-SITE BREAKDOWN:")
        logger.info("-" * 80)

        for site_name, count in self.site_stats.items():
            logger.info(f"  • {site_name:30s} : {count:4d} articles")

        logger.info("=" * 80)

    def fail(self, error_message):
        """Mark as failed"""
        self.is_running = False
        self.error = error_message
        self.status_message = f"Failed: {error_message}"
        self.end_time = datetime.now()
        logger.error("=" * 80)
        logger.error(f"SCRAPER FAILED: {error_message}")
        logger.error("=" * 80)


class MultiSiteScraper:
    """Multi-site news scraper using sites_config.json"""

    def __init__(self, status_callback=None):
        """
        Initialize multi-site scraper

        Args:
            status_callback: Optional callback function(status) for status updates
        """
        self.headers = SCRAPER_CONFIG['headers']
        self.timeout = SCRAPER_CONFIG['timeout']
        self.delay = SCRAPER_CONFIG['delay_between_requests']

        self.status = NewsScraperStatus()
        self.status_callback = status_callback

        # Load site configurations
        self.sites_config = self.load_sites_config()

        logger.info(f"MultiSiteScraper initialized with {len(self.sites_config)} sites")
        for site in self.sites_config:
            logger.info(f"  - {site['name']}: {site['url']}")

    def load_sites_config(self) -> List[Dict]:
        """Load site configurations from JSON file"""
        try:
            with open(SITES_CONFIG_PATH, 'r', encoding='utf-8') as f:
                sites = json.load(f)
            logger.info(f"Loaded configuration for {len(sites)} sites from {SITES_CONFIG_PATH}")
            return sites
        except FileNotFoundError:
            logger.error(f"Config file not found: {SITES_CONFIG_PATH}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            raise

    def _update_status(self, progress, message, site="", count=0):
        """Update and notify status"""
        self.status.update(progress, message, site, count)
        if self.status_callback:
            self.status_callback(self.status)

    def extract_articles_from_selector(self, soup: BeautifulSoup, selector: Dict, site_name: str) -> List[Dict]:
        """Extract articles using a specific selector configuration"""
        articles = []

        # Find containers
        container_tag = selector.get('container_tag')
        container_class = selector.get('container_class')

        if container_class:
            containers = soup.find_all(container_tag, class_=container_class)
        else:
            containers = soup.find_all(container_tag)

        logger.debug(f"Found {len(containers)} containers with {container_tag}.{container_class}")

        for container in containers:
            try:
                article_data = {}

                # Extract title
                title_tag = selector.get('title_tag')
                title_class = selector.get('title_class')

                if title_class:
                    title_elem = container.find(title_tag, class_=title_class)
                else:
                    title_elem = container.find(title_tag)

                if title_elem:
                    article_data['title'] = title_elem.get_text(strip=True)
                else:
                    # If title not found, skip this container
                    continue

                # Extract link
                link_attribute = selector.get('link_attribute', 'href')
                link_tag = selector.get('link_tag')
                link_class = selector.get('link_class')

                if link_tag:
                    # Link is in a separate tag
                    if link_class:
                        link_elem = container.find(link_tag, class_=link_class)
                    else:
                        link_elem = container.find(link_tag)

                    if link_elem:
                        article_data['link'] = link_elem.get(link_attribute, '')
                else:
                    # Link is in the container itself
                    article_data['link'] = container.get(link_attribute, '')

                # Extract additional metadata if available
                # Publisher
                publisher_tag = selector.get('publisher_tag')
                publisher_class = selector.get('publisher_class')
                if publisher_tag:
                    if publisher_class:
                        publisher_elem = container.find(publisher_tag, class_=publisher_class)
                    else:
                        publisher_elem = container.find(publisher_tag)
                    if publisher_elem:
                        article_data['publisher'] = publisher_elem.get_text(strip=True)

                # Published time
                time_tag = selector.get('time_tag')
                time_class = selector.get('time_class')
                if time_tag:
                    if time_class:
                        time_elem = container.find(time_tag, class_=time_class)
                    else:
                        time_elem = container.find(time_tag)
                    if time_elem:
                        article_data['published_time'] = time_elem.get_text(strip=True)

                # Country (from flag or other source)
                flag_tag = selector.get('flag_tag')
                flag_class = selector.get('flag_class')
                if flag_tag:
                    if flag_class:
                        flag_elem = container.find(flag_tag, class_=flag_class)
                    else:
                        flag_elem = container.find(flag_tag)
                    if flag_elem:
                        # Try to get country from alt attribute or src
                        country = flag_elem.get('alt', '')
                        if not country and 'src' in flag_elem.attrs:
                            src = flag_elem.get('src', '')
                            if '/flags/' in src:
                                # Extract country code from path like /flags/large/US.png
                                country = src.split('/')[-1].replace('.png', '')
                        if country:
                            article_data['country'] = country

                # Add metadata
                article_data['source'] = site_name
                article_data['scraped_at'] = datetime.now().isoformat()

                # Map to app's expected format for backward compatibility
                if article_data.get('title'):
                    article_data['headline'] = article_data['title']  # Map title to headline
                if article_data.get('link'):
                    article_data['article_url'] = article_data['link']  # Map link to article_url
                if not article_data.get('publisher'):
                    article_data['publisher'] = site_name  # Default to site_name
                if not article_data.get('published_time'):
                    article_data['published_time'] = 'N/A'  # Default value
                if not article_data.get('country'):
                    article_data['country'] = 'Unknown'  # Default value

                # Only add if we have both title and link
                if article_data.get('title') and article_data.get('link'):
                    # Make link absolute if needed
                    link = article_data['link']
                    if link.startswith('/'):
                        # Extract base URL from site config
                        base_url = selector.get('base_url', '')
                        if base_url:
                            article_data['link'] = base_url + link

                    articles.append(article_data)

            except Exception as e:
                logger.debug(f"Error extracting article from container: {e}")
                continue

        return articles

    def scrape_site(self, site_config: Dict) -> List[Dict]:
        """Scrape a single site using its configuration"""
        site_name = site_config['name']
        site_url = site_config['url']
        selectors = site_config.get('selectors', [])
        multi_view = site_config.get('multi_view', False)
        views = site_config.get('views', {})

        logger.info(f"Scraping site: {site_name} ({site_url})")

        all_articles = []
        seen_links = set()

        try:
            # Check if multi-view scraping is enabled
            if multi_view and views:
                logger.info(f"  Multi-view scraping enabled with {len(views)} views")

                for view_name, view_param in views.items():
                    view_url = site_url + view_param
                    logger.info(f"  Scraping '{view_name}' view: {view_url}")

                    try:
                        # Fetch the view page
                        response = requests.get(view_url, headers=self.headers, timeout=self.timeout)
                        response.raise_for_status()
                        soup = BeautifulSoup(response.text, 'html.parser')

                        view_articles = []
                        # Try each selector method
                        for idx, selector in enumerate(selectors, 1):
                            articles = self.extract_articles_from_selector(soup, selector, site_name)

                            # Remove duplicates based on link
                            for article in articles:
                                link = article.get('link', '')
                                if link and link not in seen_links:
                                    seen_links.add(link)
                                    article['view'] = view_name  # Tag which view it came from
                                    all_articles.append(article)
                                    view_articles.append(article)

                        logger.info(f"    '{view_name}' view: {len(view_articles)} new articles")

                        # Delay between views
                        if view_name != list(views.keys())[-1]:  # Don't delay after last view
                            time.sleep(2)

                    except Exception as e:
                        logger.error(f"    Error scraping '{view_name}' view: {e}")
                        continue
            else:
                # Standard single-page scraping
                response = requests.get(site_url, headers=self.headers, timeout=self.timeout)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')

                # Try each selector method
                for idx, selector in enumerate(selectors, 1):
                    logger.debug(f"Trying selector {idx}/{len(selectors)} for {site_name}")

                    articles = self.extract_articles_from_selector(soup, selector, site_name)

                    # Remove duplicates based on link
                    for article in articles:
                        link = article.get('link', '')
                        if link and link not in seen_links:
                            seen_links.add(link)
                            all_articles.append(article)

            logger.info(f"[OK] {site_name}: Found {len(all_articles)} unique articles")
            return all_articles

        except requests.exceptions.Timeout:
            logger.error(f"[ERROR] {site_name}: Timeout error")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"[ERROR] {site_name}: Request error - {e}")
            return []
        except Exception as e:
            logger.error(f"[ERROR] {site_name}: Unexpected error - {e}")
            return []

    def scrape_all_sites(self) -> Tuple[List[Dict], str]:
        """Scrape all configured sites"""
        self.status.start()
        self._update_status(5, "Initializing multi-site scraper...")

        all_articles = []
        total_sites = len(self.sites_config)

        try:
            for idx, site_config in enumerate(self.sites_config, 1):
                site_name = site_config['name']
                progress = int(5 + (idx / total_sites) * 85)  # 5% to 90%

                self._update_status(
                    progress,
                    f"Scraping {site_name} ({idx}/{total_sites})...",
                    site_name
                )

                # Scrape the site
                site_articles = self.scrape_site(site_config)

                # Add to total
                all_articles.extend(site_articles)

                # Record stats
                self.status.add_site_stats(site_name, len(site_articles))

                self._update_status(
                    progress,
                    f"Completed {site_name} - {len(all_articles)} total articles",
                    site_name,
                    len(all_articles)
                )

                # Delay between sites
                if idx < total_sites:
                    time.sleep(self.delay)

            # Save to file
            self._update_status(95, "Saving data...")
            filepath = self.save_to_file(all_articles)

            # Log sample headlines from this scrape run
            if all_articles:
                logger.info("")
                logger.info("SAMPLE HEADLINES FROM THIS SCRAPE:")
                logger.info("-" * 80)
                for i, article in enumerate(all_articles[:10], 1):  # Log first 10 headlines
                    headline = article.get('headline', article.get('title', 'No headline'))[:70]
                    source = article.get('source', 'unknown')
                    publisher = article.get('publisher', '')
                    view = article.get('view', '')

                    if view:
                        logger.info(f"  {i:2d}. [{source}/{view}] {headline}")
                    else:
                        logger.info(f"  {i:2d}. [{source}] {headline}")

                    if publisher and publisher != source:
                        logger.info(f"      Publisher: {publisher}")

                if len(all_articles) > 10:
                    logger.info(f"  ... and {len(all_articles) - 10} more articles")
                logger.info("-" * 80)

            # Complete
            self.status.complete(len(all_articles))
            self._update_status(100, f"Success! Saved {len(all_articles)} articles", "", len(all_articles))

            return all_articles, filepath

        except Exception as e:
            error_msg = str(e)
            self.status.fail(error_msg)
            self._update_status(0, f"Failed: {error_msg}")
            raise

    def scrape_all_views(self) -> Tuple[List[Dict], str]:
        """Backward compatibility method - calls scrape_all_sites()"""
        return self.scrape_all_sites()

    def save_to_file(self, articles: List[Dict]) -> str:
        """Save articles to JSON and CSV files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"travel_news_multisite_{timestamp}.json"
        filepath = RAW_DATA_DIR / filename

        # Organize by source
        by_source = {}
        for article in articles:
            source = article.get('source', 'unknown')
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(article)

        output = {
            'total_articles': len(articles),
            'scraped_at': datetime.now().isoformat(),
            'total_sites': len(by_source),
            'sites_scraped': list(by_source.keys()),
            'articles_by_source': by_source,
            'all_articles': articles,
            'statistics': {
                site: len(arts) for site, arts in by_source.items()
            }
        }

        # Save JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(articles)} articles to {filepath}")

        # Save CSV
        csv_path = filepath.with_suffix('.csv')
        self.save_to_csv(articles, csv_path)

        return str(filepath)

    def save_to_csv(self, articles: List[Dict], filepath: Path):
        """Save articles to CSV"""
        fieldnames = ['title', 'link', 'source', 'scraped_at']

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for article in articles:
                writer.writerow({k: article.get(k, '') for k in fieldnames})

        logger.info(f"Saved CSV to {filepath}")


# Backward compatibility alias
TravelNewsScraper = MultiSiteScraper


# Convenience function
def run_scraper(status_callback=None):
    """
    Run multi-site scraper and return results

    Args:
        status_callback: Optional callback function for status updates

    Returns:
        tuple: (articles list, filepath string)
    """
    scraper = MultiSiteScraper(status_callback=status_callback)
    return scraper.scrape_all_sites()


if __name__ == "__main__":
    # Test scraper
    print("Testing multi-site scraper...")
    articles, filepath = run_scraper()
    print(f"\nScraped {len(articles)} articles from all sites")
    print(f"Saved to: {filepath}")
