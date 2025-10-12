"""
News Scraper Module
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
from datetime import datetime
from pathlib import Path
import time

# Import settings and logger
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config.settings import SCRAPER_CONFIG, RAW_DATA_DIR
from utils.logger import get_scraper_logger

logger = get_scraper_logger()


class NewsScraperStatus:
    """Track scraper status"""
    
    def __init__(self):
        self.is_running = False
        self.progress = 0
        self.status_message = "Idle"
        self.articles_count = 0
        self.current_view = ""
        self.error = None
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """Start scraping"""
        self.is_running = True
        self.progress = 0
        self.status_message = "Starting scraper..."
        self.articles_count = 0
        self.error = None
        self.start_time = datetime.now()
        self.end_time = None
        logger.info("Scraper started")
    
    def update(self, progress, message, view="", count=0):
        """Update status"""
        self.progress = progress
        self.status_message = message
        self.current_view = view
        self.articles_count = count
        logger.debug(f"Status update: {message} ({progress}%)")
    
    def complete(self, articles_count):
        """Complete scraping"""
        self.is_running = False
        self.progress = 100
        self.status_message = f"Completed! Scraped {articles_count} articles"
        self.articles_count = articles_count
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        logger.info(f"Scraper completed. Articles: {articles_count}, Duration: {duration:.2f}s")
    
    def fail(self, error_message):
        """Mark as failed"""
        self.is_running = False
        self.error = error_message
        self.status_message = f"Failed: {error_message}"
        self.end_time = datetime.now()
        logger.error(f"Scraper failed: {error_message}")


class TravelNewsScraper:
    """Enhanced travel news scraper"""
    
    def __init__(self, status_callback=None):
        """
        Initialize scraper
        
        Args:
            status_callback: Optional callback function(status) for status updates
        """
        self.base_url = SCRAPER_CONFIG['base_url']
        self.headers = SCRAPER_CONFIG['headers']
        self.views = SCRAPER_CONFIG['views']
        self.timeout = SCRAPER_CONFIG['timeout']
        self.delay = SCRAPER_CONFIG['delay_between_requests']
        
        self.status = NewsScraperStatus()
        self.status_callback = status_callback
        
        logger.info("TravelNewsScraper initialized")
    
    def _update_status(self, progress, message, view="", count=0):
        """Update and notify status"""
        self.status.update(progress, message, view, count)
        if self.status_callback:
            self.status_callback(self.status)
    
    def extract_articles_from_html(self, html_content, view_name):
        """Extract articles from HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        articles = []
        article_cards = soup.find_all('article', class_='article-card')
        
        logger.debug(f"Found {len(article_cards)} articles in '{view_name}' view")
        
        for idx, card in enumerate(article_cards, 1):
            try:
                article_data = {}
                
                # Headline
                headline_elem = card.find('span', class_='article-title')
                if headline_elem:
                    article_data['headline'] = headline_elem.get_text(strip=True)
                
                # Article URL
                link_elem = card.find('a', class_='article-card__headline')
                if link_elem:
                    article_data['article_url'] = link_elem.get('href')
                
                # Publisher
                publisher_elem = card.find('span', class_='article-publisher__name')
                if publisher_elem:
                    article_data['publisher'] = publisher_elem.get_text(strip=True)
                
                # Timestamp
                time_elem = card.find('span', class_='article-publisher__timestamp')
                if time_elem:
                    article_data['published_time'] = time_elem.get_text(strip=True)
                
                # Country
                country = 'Unknown'
                flag_elem = card.find('img', class_='article-card__flag-inner')
                if flag_elem:
                    country = flag_elem.get('alt', 'Unknown')
                    if not country or country == '':
                        src = flag_elem.get('src', '')
                        if '/flags/' in src:
                            country_code = src.split('/')[-1].replace('.png', '')
                            country = country_code
                
                if country == 'Unknown':
                    flag_div = card.find('div', class_='with-tooltip')
                    if flag_div and flag_div.get('data-tooltip'):
                        country = flag_div.get('data-tooltip')
                
                article_data['country'] = country
                
                # Tags
                tags = []
                tag_elements = card.find_all('a', class_='tag')
                for tag in tag_elements:
                    tag_text = tag.get_text(strip=True)
                    if tag_text:
                        tags.append(tag_text)
                article_data['tags'] = tags
                
                # Metadata
                article_data['view'] = view_name
                article_data['scraped_at'] = datetime.now().isoformat()
                
                if article_data.get('headline'):
                    articles.append(article_data)
                
            except Exception as e:
                logger.warning(f"Error extracting article {idx}: {e}")
                continue
        
        return articles
    
    def scrape_view(self, view_name, view_param):
        """Scrape a specific view"""
        url = self.base_url + view_param
        
        logger.info(f"Scraping '{view_name}' view: {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            articles = self.extract_articles_from_html(response.text, view_name)
            logger.info(f"Extracted {len(articles)} articles from '{view_name}' view")
            
            return articles
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout scraping '{view_name}' view")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error scraping '{view_name}' view: {e}")
            raise
    
    def scrape_all_views(self):
        """Scrape all views and combine results"""
        self.status.start()
        self._update_status(5, "Initializing scraper...")
        
        all_articles = []
        seen_urls = set()
        total_views = len(self.views)
        
        try:
            for idx, (view_name, view_param) in enumerate(self.views.items(), 1):
                progress = int(5 + (idx / total_views) * 85)  # 5% to 90%
                
                self._update_status(
                    progress, 
                    f"Scraping {view_name} view...", 
                    view_name
                )
                
                articles = self.scrape_view(view_name, view_param)
                
                # Remove duplicates
                for article in articles:
                    url = article.get('article_url', '')
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        all_articles.append(article)
                
                self._update_status(
                    progress,
                    f"Completed {view_name} view - {len(all_articles)} unique articles so far",
                    view_name,
                    len(all_articles)
                )
                
                # Delay between requests
                if idx < total_views:
                    time.sleep(self.delay)
            
            # Save to file
            self._update_status(95, "Saving data...")
            filepath = self.save_to_file(all_articles)
            
            # Complete
            self.status.complete(len(all_articles))
            self._update_status(100, f"Success! Saved {len(all_articles)} articles", "", len(all_articles))
            
            return all_articles, filepath
            
        except Exception as e:
            error_msg = str(e)
            self.status.fail(error_msg)
            self._update_status(0, f"Failed: {error_msg}")
            raise
    
    def save_to_file(self, articles):
        """Save articles to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"travel_news_{timestamp}.json"
        filepath = RAW_DATA_DIR / filename
        
        # Organize by view
        by_view = {}
        for article in articles:
            view = article.get('view', 'unknown')
            if view not in by_view:
                by_view[view] = []
            by_view[view].append(article)
        
        output = {
            'total_articles': len(articles),
            'scraped_at': datetime.now().isoformat(),
            'source_url': self.base_url,
            'views_scraped': list(by_view.keys()),
            'articles_by_view': by_view,
            'all_articles': articles
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(articles)} articles to {filepath}")
        
        # Also save CSV
        csv_path = filepath.with_suffix('.csv')
        self.save_to_csv(articles, csv_path)
        
        return str(filepath)
    
    def save_to_csv(self, articles, filepath):
        """Save articles to CSV"""
        fieldnames = ['headline', 'publisher', 'published_time', 'country', 
                     'article_url', 'tags', 'view', 'scraped_at']
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for article in articles:
                row = article.copy()
                row['tags'] = ', '.join(article.get('tags', []))
                writer.writerow({k: row.get(k, '') for k in fieldnames})
        
        logger.debug(f"Saved CSV to {filepath}")


# Convenience function
def run_scraper(status_callback=None):
    """
    Run scraper and return results
    
    Args:
        status_callback: Optional callback function for status updates
    
    Returns:
        tuple: (articles list, filepath string)
    """
    scraper = TravelNewsScraper(status_callback=status_callback)
    return scraper.scrape_all_views()


if __name__ == "__main__":
    # Test scraper
    print("Testing scraper...")
    articles, filepath = run_scraper()
    print(f"\nScraped {len(articles)} articles")
    print(f"Saved to: {filepath}")