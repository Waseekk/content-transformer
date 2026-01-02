"""
Content Extraction Service
Extract article content from URLs using Trafilatura and Newspaper3k
"""

import requests
import trafilatura
from newspaper import Article
from typing import Dict, Optional
from datetime import datetime

from shared.utils.logger import LoggerManager

logger = LoggerManager.get_logger('content_extraction')


class ExtractionError(Exception):
    """Raised when content extraction fails"""
    pass


class ContentExtractor:
    """
    Lightweight content extraction from URLs
    Uses cascading approach: Trafilatura → Newspaper3k
    """

    def __init__(self):
        self.timeout = 15  # Request timeout in seconds
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

    async def extract(
        self,
        url: str,
        method: str = 'auto'
    ) -> Dict[str, str]:
        """
        Extract content from URL using cascading methods

        Args:
            url: Target URL to extract content from
            method: Extraction method - 'auto', 'trafilatura', 'newspaper'

        Returns:
            Dictionary with:
                - title: Article title
                - text: Main article content
                - author: Author name (if available)
                - date: Publication date (if available)
                - method: Which extraction method succeeded
                - url: Original URL
                - extracted_at: Extraction timestamp

        Raises:
            ExtractionError: If all extraction methods fail
        """
        logger.info(f"Extracting content from: {url}")

        if method == 'auto':
            # Try Trafilatura first (fastest, most accurate)
            try:
                result = await self._extract_with_trafilatura(url)
                if result and len(result['text']) > 200:
                    logger.info(f"Successfully extracted with Trafilatura: {len(result['text'])} chars")
                    return result
            except Exception as e:
                logger.warning(f"Trafilatura extraction failed: {str(e)}")

            # Fallback to Newspaper3k
            try:
                result = await self._extract_with_newspaper(url)
                if result and len(result['text']) > 200:
                    logger.info(f"Successfully extracted with Newspaper3k: {len(result['text'])} chars")
                    return result
            except Exception as e:
                logger.warning(f"Newspaper3k extraction failed: {str(e)}")

            raise ExtractionError("All extraction methods failed. URL may be inaccessible or content may be behind a paywall.")

        elif method == 'trafilatura':
            return await self._extract_with_trafilatura(url)

        elif method == 'newspaper':
            return await self._extract_with_newspaper(url)

        else:
            raise ValueError(f"Invalid extraction method: {method}")

    async def _extract_with_trafilatura(self, url: str) -> Dict[str, str]:
        """
        Extract content using Trafilatura

        Trafilatura is optimized for news articles and blogs.
        Fast, accurate, and handles most common HTML structures.
        """
        try:
            # Download content
            downloaded = trafilatura.fetch_url(url)

            if not downloaded:
                raise ExtractionError("Failed to download content from URL")

            # Extract main text
            text = trafilatura.extract(
                downloaded,
                include_comments=False,
                include_tables=True,
                no_fallback=False
            )

            if not text:
                raise ExtractionError("No content extracted")

            # Extract metadata
            metadata = trafilatura.extract_metadata(downloaded)

            return {
                'title': metadata.title if metadata and metadata.title else '',
                'text': text,
                'author': metadata.author if metadata and metadata.author else '',
                'date': metadata.date if metadata and metadata.date else '',
                'method': 'trafilatura',
                'url': url,
                'extracted_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Trafilatura extraction error: {str(e)}")
            raise ExtractionError(f"Trafilatura extraction failed: {str(e)}")

    async def _extract_with_newspaper(self, url: str) -> Dict[str, str]:
        """
        Extract content using Newspaper3k

        Newspaper3k is optimized specifically for news articles.
        Good fallback when Trafilatura fails.
        """
        try:
            # Create article object
            article = Article(url)

            # Download and parse
            article.download()
            article.parse()

            if not article.text:
                raise ExtractionError("No content extracted")

            # Get publication date
            pub_date = ''
            if article.publish_date:
                pub_date = article.publish_date.isoformat()

            return {
                'title': article.title or '',
                'text': article.text,
                'author': ', '.join(article.authors) if article.authors else '',
                'date': pub_date,
                'method': 'newspaper3k',
                'url': url,
                'extracted_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Newspaper3k extraction error: {str(e)}")
            raise ExtractionError(f"Newspaper3k extraction failed: {str(e)}")

    async def extract_multiple(
        self,
        urls: list[str],
        method: str = 'auto'
    ) -> Dict[str, Dict]:
        """
        Extract content from multiple URLs

        Args:
            urls: List of URLs to extract
            method: Extraction method to use

        Returns:
            Dictionary mapping URLs to extraction results
            Failed extractions will have 'error' key in result
        """
        results = {}

        for url in urls:
            try:
                result = await self.extract(url, method)
                results[url] = result
            except Exception as e:
                logger.error(f"Failed to extract {url}: {str(e)}")
                results[url] = {
                    'error': str(e),
                    'url': url,
                    'extracted_at': datetime.utcnow().isoformat()
                }

        return results

    def validate_url(self, url: str) -> bool:
        """
        Validate if URL is accessible and returns HTML

        Args:
            url: URL to validate

        Returns:
            True if URL is valid and accessible
        """
        try:
            response = requests.head(url, timeout=5, allow_redirects=True)
            return response.status_code == 200
        except Exception:
            return False


# Convenience function for direct usage
async def extract_content_from_url(url: str, method: str = 'auto') -> Dict[str, str]:
    """
    Extract content from a single URL

    Args:
        url: URL to extract content from
        method: Extraction method ('auto', 'trafilatura', 'newspaper')

    Returns:
        Extracted content dictionary

    Example:
        >>> content = await extract_content_from_url('https://example.com/article')
        >>> print(content['title'])
        >>> print(content['text'][:200])
    """
    extractor = ContentExtractor()
    return await extractor.extract(url, method)


# Example usage
if __name__ == "__main__":
    import asyncio

    async def test_extraction():
        """Test content extraction"""
        test_urls = [
            "https://www.bbc.com/travel",
            "https://www.cnn.com/travel",
        ]

        extractor = ContentExtractor()

        for url in test_urls:
            try:
                print(f"\nTesting: {url}")
                result = await extractor.extract(url)
                print(f"✓ Method: {result['method']}")
                print(f"✓ Title: {result['title'][:80]}...")
                print(f"✓ Content: {len(result['text'])} characters")
                print(f"✓ Author: {result['author']}")
                print(f"✓ Date: {result['date']}")
            except ExtractionError as e:
                print(f"✗ Failed: {e}")

    asyncio.run(test_extraction())
