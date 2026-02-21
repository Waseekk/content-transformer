"""
Google News Search Service
Uses requests + BeautifulSoup to fetch Google News RSS feed
"""

import time
import hashlib
import requests
import re
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from urllib.parse import quote_plus, urlparse, parse_qs
from bs4 import BeautifulSoup


class GoogleNewsSearcher:
    """
    Google News search service using Google News RSS feed.

    Features:
    - Searches Google News by keyword via RSS
    - Filters by time (1h, 24h, 7d, 30d) - applied post-fetch
    - Caches results to prevent rate limiting
    """

    # Time filter mappings (hours)
    TIME_FILTERS = {
        "1h": 1,
        "24h": 24,
        "7d": 168,    # 7 * 24
        "30d": 720,   # 30 * 24
    }

    # In-memory cache (upgrade to Redis for production)
    _cache: Dict[str, Dict[str, Any]] = {}
    _cache_duration = timedelta(minutes=5)

    # Request headers to mimic a browser
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/rss+xml, application/xml, text/xml, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
    }

    def __init__(self):
        pass

    def _is_bengali(self, text: str) -> bool:
        """Check if text contains Bengali Unicode characters (U+0980–U+09FF)"""
        return bool(re.search(r'[\u0980-\u09FF]', text))

    def _translate_keyword_to_english(self, keyword: str) -> str:
        """Translate a Bengali keyword to English using OpenAI."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a translator. Translate the given Bengali word or phrase to English. Reply with ONLY the English translation, nothing else."
                    },
                    {
                        "role": "user",
                        "content": keyword
                    }
                ],
                max_tokens=50,
                temperature=0
            )
            translated = response.choices[0].message.content.strip()
            return translated
        except Exception as e:
            # If translation fails, return original keyword so search still runs
            return keyword

    def _get_cache_key(self, keyword: str, time_filter: str, user_id: Optional[int] = None) -> str:
        """Generate cache key from search parameters"""
        raw_key = f"{user_id or 'anon'}:{keyword.lower().strip()}:{time_filter}"
        return hashlib.md5(raw_key.encode()).hexdigest()

    def _get_cached_results(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached results if still valid"""
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            if datetime.now() - cached['timestamp'] < self._cache_duration:
                return cached['data']
            else:
                # Cache expired, remove it
                del self._cache[cache_key]
        return None

    def _set_cache(self, cache_key: str, data: Dict[str, Any]):
        """Store results in cache"""
        self._cache[cache_key] = {
            'timestamp': datetime.now(),
            'data': data
        }

    def _build_rss_url(self, keyword: str, language: str = 'en') -> str:
        """Build Google News RSS URL, using Bengali locale for Bengali keywords."""
        encoded_keyword = quote_plus(keyword)
        if language == 'bn':
            return f"https://news.google.com/rss/search?q={encoded_keyword}&hl=bn-BD&gl=BD&ceid=BD:bn"
        return f"https://news.google.com/rss/search?q={encoded_keyword}&hl=en-US&gl=US&ceid=US:en"

    def _extract_real_url(self, google_url: str) -> str:
        """Extract the real article URL from Google's redirect URL"""
        # Google News RSS links look like: https://news.google.com/rss/articles/...
        # or contain a redirect parameter
        if 'news.google.com' in google_url:
            # Try to follow the redirect or parse the URL
            try:
                # Make a HEAD request to get the real URL
                resp = requests.head(google_url, allow_redirects=True, timeout=5, headers=self.HEADERS)
                if resp.url and 'news.google.com' not in resp.url:
                    return resp.url
            except:
                pass
        return google_url

    def _parse_pub_date(self, pub_date_str: str) -> Optional[datetime]:
        """Parse RSS pubDate to datetime"""
        if not pub_date_str:
            return None
        try:
            # RSS date format: "Sat, 18 Jan 2025 10:30:00 GMT"
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(pub_date_str)
        except:
            return None

    def _is_within_time_filter(self, pub_date: Optional[datetime], hours: int) -> bool:
        """Check if publication date is within the time filter"""
        if not pub_date:
            return True  # Include if we can't determine the date
        cutoff = datetime.now(pub_date.tzinfo) - timedelta(hours=hours)
        return pub_date >= cutoff

    def _extract_source_from_title(self, title: str) -> tuple:
        """Extract source name from title (Google News format: 'Title - Source')"""
        if ' - ' in title:
            parts = title.rsplit(' - ', 1)
            if len(parts) == 2:
                return parts[0].strip(), parts[1].strip()
        return title, None

    def _format_time_ago(self, pub_date: Optional[datetime]) -> Optional[str]:
        """Format publication date as relative time"""
        if not pub_date:
            return None
        try:
            now = datetime.now(pub_date.tzinfo)
            diff = now - pub_date

            if diff.days > 0:
                return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
            hours = diff.seconds // 3600
            if hours > 0:
                return f"{hours} hour{'s' if hours > 1 else ''} ago"
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        except:
            return None

    def _extract_results_from_rss(self, soup: BeautifulSoup, max_results: int, time_hours: int) -> List[Dict[str, Any]]:
        """Extract news results from RSS feed"""
        results = []

        items = soup.find_all('item')

        for item in items:
            if len(results) >= max_results:
                break

            try:
                # Get title (includes source)
                title_elem = item.find('title')
                full_title = title_elem.get_text(strip=True) if title_elem else None
                if not full_title:
                    continue

                # Extract actual title and source
                title, source = self._extract_source_from_title(full_title)

                # Get link
                link_elem = item.find('link')
                url = link_elem.get_text(strip=True) if link_elem else None
                if not url:
                    continue

                # Get publication date
                pub_date_elem = item.find('pubdate')
                pub_date_str = pub_date_elem.get_text(strip=True) if pub_date_elem else None
                pub_date = self._parse_pub_date(pub_date_str)

                # Filter by time
                if not self._is_within_time_filter(pub_date, time_hours):
                    continue

                # Get description/snippet
                desc_elem = item.find('description')
                snippet = None
                if desc_elem:
                    desc_html = desc_elem.get_text(strip=True)
                    # Parse HTML in description to get clean text
                    desc_soup = BeautifulSoup(desc_html, 'html.parser')
                    snippet = desc_soup.get_text(strip=True)[:200]

                # Format time
                published_time = self._format_time_ago(pub_date)

                results.append({
                    'title': title,
                    'url': url,
                    'source': source,
                    'published_time': published_time,
                    'snippet': snippet
                })

            except Exception as e:
                continue

        return results

    async def search(
        self,
        keyword: str,
        time_filter: str = "24h",
        max_results: int = 50,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Search Google News for the given keyword using RSS feed.
        """
        start_time = time.time()

        # Validate time filter
        if time_filter not in self.TIME_FILTERS:
            time_filter = "24h"
        time_hours = self.TIME_FILTERS[time_filter]

        # Detect language — search in that language directly (no translation)
        language = 'bn' if self._is_bengali(keyword) else 'en'
        search_keyword = keyword

        # Check cache first
        cache_key = self._get_cache_key(search_keyword, time_filter, user_id)
        cached = self._get_cached_results(cache_key)
        if cached:
            cached['cached'] = True
            cached['search_time_ms'] = int((time.time() - start_time) * 1000)
            return cached

        # Build RSS URL with appropriate locale
        rss_url = self._build_rss_url(search_keyword, language)

        try:
            # Make HTTP request
            response = requests.get(
                rss_url,
                headers=self.HEADERS,
                timeout=15,
                allow_redirects=True
            )
            response.raise_for_status()

            # Parse XML/RSS
            soup = BeautifulSoup(response.content, 'xml')

            # If xml parser fails, try html.parser
            if not soup.find('item'):
                soup = BeautifulSoup(response.content, 'html.parser')

            # Extract results
            results = self._extract_results_from_rss(soup, max_results, time_hours)

            result_data = {
                'success': True,
                'keyword': keyword,  # original (Bengali) keyword for display
                'total_results': len(results),
                'results': results,
                'search_time_ms': int((time.time() - start_time) * 1000),
                'cached': False,
                'error_message': None
            }

            # Cache successful results
            if results:
                self._set_cache(cache_key, result_data)

            return result_data

        except requests.exceptions.Timeout:
            return {
                'success': False,
                'keyword': keyword,
                'total_results': 0,
                'results': [],
                'search_time_ms': int((time.time() - start_time) * 1000),
                'cached': False,
                'error_message': "Request timed out. Please try again."
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'keyword': keyword,
                'total_results': 0,
                'results': [],
                'search_time_ms': int((time.time() - start_time) * 1000),
                'cached': False,
                'error_message': f"Network error: {str(e)}"
            }
        except Exception as e:
            import traceback
            error_detail = str(e) or type(e).__name__
            print(f"[GoogleNewsSearcher] Error: {error_detail}")
            traceback.print_exc()
            return {
                'success': False,
                'keyword': keyword,
                'total_results': 0,
                'results': [],
                'search_time_ms': int((time.time() - start_time) * 1000),
                'cached': False,
                'error_message': f"Search failed: {error_detail}"
            }

    def get_paginated_results(
        self,
        keyword: str,
        time_filter: str,
        page: int = 1,
        limit: int = 10,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get paginated results from cache."""
        cache_key = self._get_cache_key(keyword, time_filter, user_id)
        cached = self._get_cached_results(cache_key)

        if not cached:
            return {
                'success': False,
                'results': [],
                'total': 0,
                'page': page,
                'limit': limit,
                'total_pages': 0,
                'keyword': keyword,
                'time_filter': time_filter,
                'cached': False,
                'error_message': 'No cached results. Please perform a search first.'
            }

        all_results = cached.get('results', [])
        total = len(all_results)
        total_pages = (total + limit - 1) // limit

        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        page_results = all_results[start_idx:end_idx]

        return {
            'success': True,
            'results': page_results,
            'total': total,
            'page': page,
            'limit': limit,
            'total_pages': total_pages,
            'keyword': keyword,
            'time_filter': time_filter,
            'cached': True,
            'error_message': None
        }

    def clear_cache(self):
        """Clear all cached search results"""
        self._cache.clear()


# Global instance for reuse
_searcher_instance: Optional[GoogleNewsSearcher] = None


def get_google_news_searcher() -> GoogleNewsSearcher:
    """Get or create a GoogleNewsSearcher instance"""
    global _searcher_instance
    if _searcher_instance is None:
        _searcher_instance = GoogleNewsSearcher()
    return _searcher_instance
