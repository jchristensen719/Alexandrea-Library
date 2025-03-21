import logging
import requests
from datetime import datetime
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

from .base_scraper import BaseScraper


class HistoryScraper(BaseScraper):
    """Scraper for historical content."""
    def __init__(self, base_url: str, era: Optional[str] = None, region: Optional[str] = None):
        super().__init__(base_url)
        self.era = era  # e.g., "ancient", "medieval", "modern"
        self.region = region  # e.g., "egypt", "greece", "rome"
        self.logger = logging.getLogger(__name__)

        # Common historical source websites
        self.trusted_sources = [
            "worldhistory.org",
            "britannica.com",
            "ancient.eu",
            "archive.org",
        ]

    def extract_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract historical data from BeautifulSoup object.

        Args:
            soup: BeautifulSoup object containing parsed HTML

        Returns:
            Dict containing extracted data including title, content, and primary sources
        """
        # Find all links that might be primary sources
        primary_sources = []
        for link in soup.find_all("a", href=True):
            if any(source in link["href"].lower() for source in self.trusted_sources):
                primary_sources.append(link["href"])

        return {
            "title": soup.title.string if soup.title else None,
            "content": soup.get_text(),
            "primary_sources": primary_sources,
        }

    def process_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the extracted historical data."""
        return raw_data
    def scrape(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape historical content from URL."""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            soup = self.parse_html(response.text)
            raw_data = self.extract_data(soup)
            return self.process_data(raw_data)
        except Exception as e:
            self.logger.error(f"Error scraping {url}: {str(e)}")
            return None
    def validate_source(self, url: str) -> bool:
        """Check if the source is from a trusted historical website."""
        return any(source in url.lower() for source in self.trusted_sources)

    def scrape_by_era(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Scrape multiple URLs filtering by historical era."""
        results = []
        for url in urls:
            if self.validate_source(url):
                try:
                    data = self.scrape(url)
                    if data:
                        results.append(data)
                except Exception as e:
                    self.logger.error(f"Error scraping {url}: {e}")
        return results
