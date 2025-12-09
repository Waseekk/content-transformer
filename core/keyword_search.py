"""
Keyword-Based News Search using Playwright MCP
Searches Prothom Alo (Bengali) and Daily Star (English) news sites
"""

from pathlib import Path
import sys
import json
import time
import re
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, urlparse
sys.path.append(str(Path(__file__).parent.parent))

from utils.logger import LoggerManager

logger = LoggerManager.get_logger('keyword_search')

# Try to import newspaper3k for article extraction (install if needed)
try:
    from newspaper import Article
    NEWSPAPER_AVAILABLE = True
except ImportError:
    NEWSPAPER_AVAILABLE = False
    logger.warning("newspaper3k not installed. Install with: pip install newspaper3k")

# Import ddgs package (formerly duckduckgo-search)
try:
    from ddgs import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False
    logger.warning("ddgs not installed. Install with: pip install ddgs")


class KeywordSearcher:
    """
    Search Bengali news sites using Playwright MCP for browser automation
    Supports Prothom Alo (Bengali) and Daily Star (English)

    Note: This class is designed to be called from Streamlit which has
    access to Playwright MCP tools via Claude Code
    """

    def __init__(self):
        """Initialize the keyword searcher"""
        self.search_urls = {
            'prothom_alo': 'https://www.prothomalo.com/search',
            'daily_star': 'https://www.thedailystar.net/search',
            'duckduckgo': 'https://html.duckduckgo.com/html/'
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        logger.info("KeywordSearcher initialized")

    def search_web(self, keyword: str, max_results: int = 10) -> List[Dict]:
        """
        Search the entire web using DuckDuckGo
        Returns news articles from any source

        Args:
            keyword: Search query
            max_results: Maximum number of results to return

        Returns:
            List of dicts with article info including source
        """
        logger.info(f"Searching web for: {keyword} (max {max_results} results)")

        # Try using duckduckgo-search package first (better results)
        if DDGS_AVAILABLE:
            try:
                articles = []

                # Use DDGS for text search
                with DDGS() as ddgs:
                    results = list(ddgs.text(keyword, max_results=max_results))

                    for result in results:
                        try:
                            # Extract data from DDGS result
                            # DDGS returns: {'title', 'href', 'body'}
                            headline = result.get('title', '')
                            url = result.get('href', '')
                            snippet = result.get('body', '')

                            if not headline or not url:
                                continue

                            # Extract source from URL
                            source = self._extract_source_from_url(url)

                            # Detect language
                            language = self._detect_language(headline + ' ' + snippet)

                            articles.append({
                                'headline': headline,
                                'url': url,
                                'snippet': snippet,
                                'source': source,
                                'language': language
                            })

                        except Exception as e:
                            logger.error(f"Error parsing DDGS result: {e}")
                            continue

                logger.info(f"Found {len(articles)} articles using DDGS")
                return articles

            except Exception as e:
                logger.error(f"DDGS search failed: {e}, falling back to HTML method")
                # Fall through to HTML method

        # Fallback: DuckDuckGo HTML search (if DDGS not available or failed)
        try:
            search_url = 'https://html.duckduckgo.com/html/'
            data = {
                'q': keyword,
                'kl': 'wt-wt',  # All regions
            }

            response = requests.post(search_url, data=data, headers=self.headers, timeout=15)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                articles = []

                # Find search result elements
                results = soup.find_all('div', class_='result')[:max_results]

                for result in results:
                    try:
                        # Extract title and link
                        title_elem = result.find('a', class_='result__a')
                        if not title_elem:
                            continue

                        headline = title_elem.get_text(strip=True)
                        url = title_elem.get('href', '')

                        # Extract snippet
                        snippet = ''
                        snippet_elem = result.find('a', class_='result__snippet')
                        if snippet_elem:
                            snippet = snippet_elem.get_text(strip=True)

                        # Extract source from URL
                        source = self._extract_source_from_url(url)

                        # Detect language (simple heuristic)
                        language = self._detect_language(headline + ' ' + snippet)

                        articles.append({
                            'headline': headline,
                            'url': url,
                            'snippet': snippet,
                            'source': source,
                            'language': language
                        })

                    except Exception as e:
                        logger.error(f"Error parsing search result: {e}")
                        continue

                logger.info(f"Found {len(articles)} articles from HTML search")
                return articles

            else:
                logger.error(f"DuckDuckGo returned HTTP {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return []

    def _extract_source_from_url(self, url: str) -> str:
        """Extract source/domain name from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.replace('www.', '')
            # Capitalize first letter
            source = domain.split('.')[0].capitalize()
            return source
        except:
            return "Unknown"

    def _detect_language(self, text: str) -> str:
        """
        Simple language detection
        Checks for Bengali characters
        """
        # Bengali Unicode range: \u0980-\u09FF
        bengali_chars = re.findall(r'[\u0980-\u09FF]', text)
        if len(bengali_chars) > 5:  # If more than 5 Bengali chars, likely Bengali
            return 'bn'
        return 'en'

    def _search_with_requests(self, site: str, keyword: str) -> List[Dict]:
        """
        Fallback: Use requests + BeautifulSoup for simple scraping
        This works without Playwright but may have limitations
        """
        try:
            if site == 'prothom_alo':
                # Prothom Alo search URL
                search_url = f"https://www.prothomalo.com/search?q={quote(keyword)}"
                response = requests.get(search_url, headers=self.headers, timeout=10)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    articles = []

                    # Find article elements (this is a guess - needs verification)
                    article_elements = soup.find_all('div', class_=['story-card', 'col-sm-6', 'col-md-4'])[:5]

                    for elem in article_elements:
                        try:
                            headline_elem = elem.find(['h2', 'h3', 'a'])
                            link_elem = elem.find('a', href=True)

                            if headline_elem and link_elem:
                                headline = headline_elem.get_text(strip=True)
                                url = link_elem['href']
                                if not url.startswith('http'):
                                    url = f"https://www.prothomalo.com{url}"

                                snippet = ''
                                snippet_elem = elem.find('p')
                                if snippet_elem:
                                    snippet = snippet_elem.get_text(strip=True)

                                articles.append({
                                    'headline': headline,
                                    'url': url,
                                    'snippet': snippet or f'Search result for {keyword}',
                                    'language': 'bn',
                                    'source': 'Prothom Alo'
                                })
                        except Exception as e:
                            logger.error(f"Error parsing article element: {e}")
                            continue

                    if articles:
                        logger.info(f"Found {len(articles)} real articles from Prothom Alo")
                        return articles
                    else:
                        logger.warning("No articles found with requests method, using mock data")
                        return self._get_mock_results('prothom_alo', keyword)
                else:
                    logger.error(f"HTTP {response.status_code} from Prothom Alo")
                    return self._get_mock_results('prothom_alo', keyword)

            elif site == 'daily_star':
                # Daily Star search URL
                search_url = f"https://www.thedailystar.net/search?query={quote(keyword)}"
                response = requests.get(search_url, headers=self.headers, timeout=10)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    articles = []

                    # Find article elements
                    article_elements = soup.find_all(['article', 'div'], class_=['article', 'news-item', 'story'])[:5]

                    for elem in article_elements:
                        try:
                            headline_elem = elem.find(['h2', 'h3', 'h4', 'a'])
                            link_elem = elem.find('a', href=True)

                            if headline_elem and link_elem:
                                headline = headline_elem.get_text(strip=True)
                                url = link_elem['href']
                                if not url.startswith('http'):
                                    url = f"https://www.thedailystar.net{url}"

                                snippet = ''
                                snippet_elem = elem.find('p')
                                if snippet_elem:
                                    snippet = snippet_elem.get_text(strip=True)

                                articles.append({
                                    'headline': headline,
                                    'url': url,
                                    'snippet': snippet or f'Search result for {keyword}',
                                    'language': 'en',
                                    'source': 'Daily Star'
                                })
                        except Exception as e:
                            logger.error(f"Error parsing article element: {e}")
                            continue

                    if articles:
                        logger.info(f"Found {len(articles)} real articles from Daily Star")
                        return articles
                    else:
                        logger.warning("No articles found with requests method, using mock data")
                        return self._get_mock_results('daily_star', keyword)
                else:
                    logger.error(f"HTTP {response.status_code} from Daily Star")
                    return self._get_mock_results('daily_star', keyword)

        except Exception as e:
            logger.error(f"Requests-based search failed for {site}: {e}")
            return self._get_mock_results(site, keyword)

    def search_prothom_alo(self, keyword: str, playwright_tools=None) -> List[Dict]:
        """
        Search Prothom Alo using Playwright MCP or fallback to requests

        Args:
            keyword: Search keyword (Bengali or English)
            playwright_tools: Dict of Playwright MCP tool functions

        Returns:
            List of dicts: [{'headline', 'url', 'snippet', 'language': 'bn'}, ...]
        """
        logger.info(f"Searching Prothom Alo for: {keyword}")

        if not playwright_tools:
            logger.info("Playwright tools not provided, using requests fallback")
            return self._search_with_requests('prothom_alo', keyword)

        try:
            # Navigate to search page
            playwright_tools['navigate'](url=self.search_urls['prothom_alo'])
            time.sleep(2)

            # Get snapshot to find search input
            snapshot = playwright_tools['snapshot']()

            # Type keyword (simplified - actual implementation needs ref from snapshot)
            # For now, construct search URL directly
            search_url = f"https://www.prothomalo.com/search?q={keyword}"
            playwright_tools['navigate'](url=search_url)
            time.sleep(3)

            # Get results
            results_snapshot = playwright_tools['snapshot']()

            # Parse results from snapshot
            articles = self._parse_prothom_alo_results(results_snapshot, keyword)

            logger.info(f"Found {len(articles)} articles from Prothom Alo")
            return articles

        except Exception as e:
            logger.error(f"Prothom Alo search failed: {e}")
            return self._get_mock_results('prothom_alo', keyword)

    def search_daily_star(self, keyword: str, playwright_tools=None) -> List[Dict]:
        """
        Search Daily Star using Playwright MCP or fallback to requests

        Args:
            keyword: Search keyword (English)
            playwright_tools: Dict of Playwright MCP tool functions

        Returns:
            List of dicts: [{'headline', 'url', 'snippet', 'language': 'en'}, ...]
        """
        logger.info(f"Searching Daily Star for: {keyword}")

        if not playwright_tools:
            logger.info("Playwright tools not provided, using requests fallback")
            return self._search_with_requests('daily_star', keyword)

        try:
            # Direct search URL approach
            search_url = f"https://www.thedailystar.net/search?query={keyword}"
            playwright_tools['navigate'](url=search_url)
            time.sleep(3)

            # Get results
            results_snapshot = playwright_tools['snapshot']()

            # Parse results
            articles = self._parse_daily_star_results(results_snapshot, keyword)

            logger.info(f"Found {len(articles)} articles from Daily Star")
            return articles

        except Exception as e:
            logger.error(f"Daily Star search failed: {e}")
            return self._get_mock_results('daily_star', keyword)

    def search_all_sites(self, keyword: str, sites: List[str] = None, playwright_tools=None) -> Dict:
        """
        Search multiple sites and return combined results

        Args:
            keyword: Search keyword
            sites: List of site names ['prothom_alo', 'daily_star']
            playwright_tools: Playwright MCP tools

        Returns:
            Dict with results per site:
            {
                'prothom_alo': [...],
                'daily_star': [...],
                'total_results': int
            }
        """
        if sites is None:
            sites = ['prothom_alo', 'daily_star']

        results = {}
        total = 0

        for site in sites:
            if site == 'prothom_alo' or site == 'Prothom Alo':
                articles = self.search_prothom_alo(keyword, playwright_tools)
                results['prothom_alo'] = articles
                total += len(articles)

            elif site == 'daily_star' or site == 'Daily Star':
                articles = self.search_daily_star(keyword, playwright_tools)
                results['daily_star'] = articles
                total += len(articles)

            # Small delay between sites
            time.sleep(2)

        results['total_results'] = total
        logger.info(f"Total articles found: {total}")

        return results

    def extract_article_from_url(self, url: str) -> Dict:
        """
        Extract article content from any URL using newspaper3k or BeautifulSoup

        Args:
            url: Article URL

        Returns:
            Article data dict
        """
        logger.info(f"Extracting article from URL: {url}")

        # Try newspaper3k first (best for news articles)
        if NEWSPAPER_AVAILABLE:
            try:
                article = Article(url)
                article.download()
                article.parse()

                # Detect language
                language = self._detect_language(article.title + ' ' + article.text)

                # Extract source from URL
                source = self._extract_source_from_url(url)

                return {
                    'headline': article.title or 'No Title',
                    'content': article.text or 'Content extraction failed',
                    'author': ', '.join(article.authors) if article.authors else None,
                    'publish_date': str(article.publish_date) if article.publish_date else None,
                    'url': url,
                    'language': language,
                    'source': source
                }
            except Exception as e:
                logger.error(f"newspaper3k extraction failed: {e}")
                # Fall through to BeautifulSoup method

        # Fallback: Simple BeautifulSoup extraction
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Try to find title
                title = soup.find('title')
                headline = title.get_text(strip=True) if title else 'No Title'

                # Try to extract main content (common patterns)
                content = ''

                # Try article tag first
                article_elem = soup.find('article')
                if article_elem:
                    paragraphs = article_elem.find_all('p')
                    content = '\n\n'.join([p.get_text(strip=True) for p in paragraphs])

                # Fallback: all paragraphs
                if not content:
                    paragraphs = soup.find_all('p')
                    content = '\n\n'.join([p.get_text(strip=True) for p in paragraphs[:10]])  # First 10 paragraphs

                language = self._detect_language(headline + ' ' + content)
                source = self._extract_source_from_url(url)

                return {
                    'headline': headline,
                    'content': content or 'Could not extract content',
                    'author': None,
                    'publish_date': None,
                    'url': url,
                    'language': language,
                    'source': source
                }
            else:
                logger.error(f"HTTP {response.status_code} when fetching {url}")
                return self._get_mock_article(url)

        except Exception as e:
            logger.error(f"Article extraction failed: {e}")
            return self._get_mock_article(url)

    def extract_article_content(self, url: str, playwright_tools=None) -> Dict:
        """
        Extract full article content from URL using Playwright MCP

        Args:
            url: Article URL
            playwright_tools: Playwright MCP tools

        Returns:
            Dict: {
                'headline': str,
                'content': str,
                'author': str,
                'publish_date': str,
                'url': str,
                'language': 'bn' or 'en'
            }
        """
        logger.info(f"Extracting article from: {url}")

        if not playwright_tools:
            logger.error("Playwright tools not provided")
            return self._get_mock_article(url)

        try:
            # Navigate to article
            playwright_tools['navigate'](url=url)
            time.sleep(3)

            # Get page snapshot
            snapshot = playwright_tools['snapshot']()

            # Parse article content
            article_data = self._parse_article_content(snapshot, url)

            logger.info(f"Extracted article: {article_data.get('headline', 'Unknown')[:50]}...")
            return article_data

        except Exception as e:
            logger.error(f"Article extraction failed: {e}")
            return self._get_mock_article(url)

    def _parse_prothom_alo_results(self, snapshot: str, keyword: str) -> List[Dict]:
        """
        Parse Prothom Alo search results from snapshot

        Args:
            snapshot: Browser snapshot text
            keyword: Search keyword

        Returns:
            List of article dicts
        """
        # TODO: Implement proper parsing of accessibility tree from snapshot
        # For now, return mock data to demonstrate functionality

        logger.info("Parsing Prothom Alo results from snapshot")

        # Mock results for demonstration
        return [
            {
                'headline': f'প্রথম আলো: {keyword} সম্পর্কিত খবর ১',
                'url': 'https://www.prothomalo.com/bangladesh/article-1',
                'snippet': f'{keyword} নিয়ে বিস্তারিত প্রতিবেদন প্রথম আলোতে প্রকাশিত...',
                'language': 'bn',
                'source': 'Prothom Alo'
            },
            {
                'headline': f'প্রথম আলো: {keyword} সম্পর্কিত খবর ২',
                'url': 'https://www.prothomalo.com/bangladesh/article-2',
                'snippet': f'{keyword} বিষয়ক আরও তথ্য এবং বিশ্লেষণ...',
                'language': 'bn',
                'source': 'Prothom Alo'
            }
        ]

    def _parse_daily_star_results(self, snapshot: str, keyword: str) -> List[Dict]:
        """
        Parse Daily Star search results from snapshot

        Args:
            snapshot: Browser snapshot text
            keyword: Search keyword

        Returns:
            List of article dicts
        """
        # TODO: Implement proper parsing

        logger.info("Parsing Daily Star results from snapshot")

        # Mock results
        return [
            {
                'headline': f'Daily Star: News about {keyword} (1)',
                'url': 'https://www.thedailystar.net/news/article-1',
                'snippet': f'Latest updates and analysis on {keyword} from Daily Star...',
                'language': 'en',
                'source': 'Daily Star'
            },
            {
                'headline': f'Daily Star: News about {keyword} (2)',
                'url': 'https://www.thedailystar.net/news/article-2',
                'snippet': f'In-depth coverage of {keyword} and related developments...',
                'language': 'en',
                'source': 'Daily Star'
            }
        ]

    def _parse_article_content(self, snapshot: str, url: str) -> Dict:
        """
        Parse article content from snapshot

        Args:
            snapshot: Browser snapshot
            url: Article URL

        Returns:
            Article data dict
        """
        # TODO: Implement proper parsing from accessibility tree

        logger.info("Parsing article content from snapshot")

        # Detect language from URL
        language = 'bn' if 'prothomalo' in url else 'en'
        source = 'Prothom Alo' if 'prothomalo' in url else 'Daily Star'

        # Mock article content
        if language == 'bn':
            return {
                'headline': 'নমুনা বাংলা শিরোনাম',
                'content': 'এটি একটি নমুনা বাংলা নিবন্ধ। প্রকৃত বাস্তবায়নে, এটি Playwright স্ন্যাপশট থেকে প্রকৃত বিষয়বস্তু নিষ্কাশন করবে।',
                'author': 'প্রতিবেদক',
                'publish_date': '২০২৫-১১-২৯',
                'url': url,
                'language': language,
                'source': source
            }
        else:
            return {
                'headline': 'Sample English Headline',
                'content': 'This is a sample English article. In actual implementation, this will extract real content from the Playwright snapshot.',
                'author': 'Staff Reporter',
                'publish_date': '2025-11-29',
                'url': url,
                'language': language,
                'source': source
            }

    def _get_mock_results(self, site: str, keyword: str) -> List[Dict]:
        """Generate mock search results for testing"""
        if site == 'prothom_alo':
            return [
                {
                    'headline': f'[Mock] প্রথম আলো: {keyword} সংবাদ',
                    'url': 'https://www.prothomalo.com/mock-article',
                    'snippet': f'{keyword} সম্পর্কিত নমুনা সংবাদ',
                    'language': 'bn',
                    'source': 'Prothom Alo'
                }
            ]
        else:
            return [
                {
                    'headline': f'[Mock] Daily Star: {keyword} news',
                    'url': 'https://www.thedailystar.net/mock-article',
                    'snippet': f'Mock news about {keyword}',
                    'language': 'en',
                    'source': 'Daily Star'
                }
            ]

    def _get_mock_article(self, url: str) -> Dict:
        """Generate mock article for testing"""
        language = 'bn' if 'prothomalo' in url else 'en'

        if language == 'bn':
            return {
                'headline': '[Mock] নমুনা শিরোনাম',
                'content': 'নমুনা বাংলা বিষয়বস্তু। প্রকৃত Playwright সংযোগ সক্রিয় হলে প্রকৃত নিবন্ধ নিষ্কাশন করা হবে।',
                'author': None,
                'publish_date': None,
                'url': url,
                'language': language,
                'source': 'Prothom Alo'
            }
        else:
            return {
                'headline': '[Mock] Sample Headline',
                'content': 'Mock English content. Will extract real article when Playwright connection is active.',
                'author': None,
                'publish_date': None,
                'url': url,
                'language': language,
                'source': 'Daily Star'
            }


# ============================================================================
# TESTING
# ============================================================================

if __name__ == '__main__':
    # Test the searcher
    searcher = KeywordSearcher()

    print("\n=== Testing Keyword Search (Mock Mode) ===\n")

    # Test search without Playwright (will use mock data)
    results = searcher.search_all_sites("tourism", sites=['prothom_alo', 'daily_star'])

    print(f"\nTotal results: {results['total_results']}")

    for site, articles in results.items():
        if site != 'total_results' and articles:
            print(f"\n{site.upper()}:")
            for article in articles:
                print(f"  - {article['headline']}")
                print(f"    {article['url']}")

    # Test extraction
    if results.get('prothom_alo'):
        url = results['prothom_alo'][0]['url']
        print(f"\n\nExtracting article from: {url}")
        article = searcher.extract_article_content(url)
        print(f"Headline: {article['headline']}")
        print(f"Language: {article['language']}")
        print(f"Content: {article['content'][:100]}...")
