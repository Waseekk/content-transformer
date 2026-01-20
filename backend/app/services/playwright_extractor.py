"""
Playwright Content Extraction Service
Extract article content from URLs using headless browser for JS-rendered sites
"""

import asyncio
import re
from typing import Dict, Optional
from datetime import datetime

from app.utils.logger import LoggerManager

logger = LoggerManager.get_logger('playwright_extractor')


class PlaywrightExtractionError(Exception):
    """Raised when Playwright extraction fails"""
    pass


class PlaywrightExtractor:
    """
    Content extraction using Playwright headless browser.
    Handles JavaScript-rendered content that Trafilatura/Newspaper3k can't extract.
    """

    # CSS selectors for article content (in priority order)
    CONTENT_SELECTORS = [
        'article',
        '[role="article"]',
        '.article-content',
        '.article-body',
        '.article__body',
        '.story-body',
        '.post-content',
        '.entry-content',
        '.content-body',
        '.main-content',
        'main article',
        'main',
        '#article-body',
        '#story-body',
        '#content',
    ]

    # Selectors for elements to remove (noise)
    NOISE_SELECTORS = [
        'nav',
        'header',
        'footer',
        'aside',
        '.sidebar',
        '.navigation',
        '.nav',
        '.menu',
        '.advertisement',
        '.ad',
        '.ads',
        '.social-share',
        '.share-buttons',
        '.comments',
        '.comment-section',
        '.related-articles',
        '.recommended',
        '.newsletter',
        '.subscribe',
        '.popup',
        '.modal',
        'script',
        'style',
        'noscript',
        'iframe',
        '[aria-hidden="true"]',
    ]

    def __init__(self, timeout: int = 30):
        """
        Initialize Playwright extractor.

        Args:
            timeout: Page load timeout in seconds (default: 30)
        """
        self.timeout = timeout * 1000  # Convert to milliseconds
        self._browser = None
        self._playwright = None

    async def _ensure_browser(self):
        """Ensure browser is started."""
        if self._browser is None:
            try:
                from playwright.async_api import async_playwright
                self._playwright = await async_playwright().start()
                self._browser = await self._playwright.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-gpu',
                        '--disable-dev-shm-usage',
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                    ]
                )
                logger.info("Playwright browser started successfully")
            except Exception as e:
                logger.error(f"Failed to start Playwright browser: {e}")
                raise PlaywrightExtractionError(
                    f"Browser initialization failed: {str(e)}. "
                    "Make sure Playwright is installed: pip install playwright && playwright install chromium"
                )

    async def _cleanup_browser(self):
        """Clean up browser resources."""
        try:
            if self._browser:
                await self._browser.close()
                self._browser = None
            if self._playwright:
                await self._playwright.stop()
                self._playwright = None
        except Exception as e:
            logger.warning(f"Error during browser cleanup: {e}")

    async def extract(self, url: str) -> Dict[str, str]:
        """
        Extract content from URL using Playwright.

        Args:
            url: Target URL to extract content from

        Returns:
            Dictionary with:
                - title: Article title
                - text: Main article content (cleaned)
                - author: Author name (if available)
                - date: Publication date (if available)
                - method: 'playwright'
                - url: Original URL
                - extracted_at: Extraction timestamp

        Raises:
            PlaywrightExtractionError: If extraction fails
        """
        logger.info(f"Extracting content from {url} using Playwright")

        page = None
        try:
            await self._ensure_browser()

            # Create new page with context
            context = await self._browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()

            # Navigate to URL
            try:
                await page.goto(url, wait_until='domcontentloaded', timeout=self.timeout)
                # Wait a bit for JS to render
                await page.wait_for_timeout(2000)
            except Exception as e:
                logger.error(f"Navigation failed: {e}")
                raise PlaywrightExtractionError(f"Failed to load page: {str(e)}")

            # Extract title
            title = await self._extract_title(page)

            # Remove noise elements
            await self._remove_noise(page)

            # Extract main content
            text = await self._extract_content(page)

            if not text or len(text) < 100:
                raise PlaywrightExtractionError("Insufficient content extracted from page")

            # Extract metadata
            author = await self._extract_author(page)
            date = await self._extract_date(page)

            logger.info(f"Successfully extracted {len(text)} characters using Playwright")

            return {
                'title': title,
                'text': text,
                'author': author,
                'date': date,
                'method': 'playwright',
                'url': url,
                'extracted_at': datetime.utcnow().isoformat()
            }

        except PlaywrightExtractionError:
            raise
        except Exception as e:
            logger.error(f"Playwright extraction error: {e}")
            raise PlaywrightExtractionError(f"Extraction failed: {str(e)}")
        finally:
            if page:
                try:
                    await page.close()
                except:
                    pass

    async def _extract_title(self, page) -> str:
        """Extract article title from page."""
        # Try various title selectors
        title_selectors = [
            'h1.article-title',
            'h1.headline',
            'h1.entry-title',
            'h1.post-title',
            'article h1',
            'main h1',
            'h1',
            'title',
        ]

        for selector in title_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    title = await element.text_content()
                    if title and len(title.strip()) > 5:
                        return title.strip()
            except:
                continue

        # Fallback to page title
        return await page.title() or ''

    async def _extract_author(self, page) -> str:
        """Extract author name from page."""
        author_selectors = [
            '[rel="author"]',
            '.author-name',
            '.byline',
            '.author',
            '[itemprop="author"]',
            'meta[name="author"]',
        ]

        for selector in author_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    if selector.startswith('meta'):
                        author = await element.get_attribute('content')
                    else:
                        author = await element.text_content()
                    if author and len(author.strip()) > 1:
                        return author.strip()
            except:
                continue

        return ''

    async def _extract_date(self, page) -> str:
        """Extract publication date from page."""
        date_selectors = [
            'time[datetime]',
            '[itemprop="datePublished"]',
            '.publish-date',
            '.date',
            'meta[property="article:published_time"]',
        ]

        for selector in date_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    if 'time' in selector:
                        date = await element.get_attribute('datetime')
                    elif selector.startswith('meta'):
                        date = await element.get_attribute('content')
                    else:
                        date = await element.text_content()
                    if date:
                        return date.strip()
            except:
                continue

        return ''

    async def _remove_noise(self, page):
        """Remove noise elements from page."""
        for selector in self.NOISE_SELECTORS:
            try:
                await page.evaluate(f'''
                    document.querySelectorAll("{selector}").forEach(el => el.remove());
                ''')
            except:
                continue

    async def _extract_content(self, page) -> str:
        """Extract main article content from page."""
        # Try each content selector
        for selector in self.CONTENT_SELECTORS:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text:
                        cleaned = self._clean_text(text)
                        if len(cleaned) > 200:
                            return cleaned
            except:
                continue

        # Fallback: get all text from body
        try:
            body = await page.query_selector('body')
            if body:
                text = await body.text_content()
                return self._clean_text(text)
        except:
            pass

        return ''

    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        if not text:
            return ''

        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove common noise patterns
        noise_patterns = [
            r'Share this article',
            r'Follow us on',
            r'Subscribe to',
            r'Sign up for',
            r'Newsletter',
            r'Cookie Policy',
            r'Privacy Policy',
            r'Terms of Service',
            r'Advertisement',
            r'ADVERTISEMENT',
            r'Sponsored',
            r'Read more:',
            r'Related:',
            r'See also:',
        ]

        for pattern in noise_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)

        # Clean up resulting whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

        return text

    async def close(self):
        """Close browser and release resources."""
        await self._cleanup_browser()


# Convenience function for direct usage
async def extract_with_playwright(url: str) -> Dict[str, str]:
    """
    Extract content from URL using Playwright.

    Args:
        url: URL to extract content from

    Returns:
        Extracted content dictionary

    Example:
        >>> content = await extract_with_playwright('https://example.com/article')
        >>> print(content['title'])
        >>> print(content['text'][:200])
    """
    extractor = PlaywrightExtractor()
    try:
        return await extractor.extract(url)
    finally:
        await extractor.close()
