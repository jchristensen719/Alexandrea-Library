"""
Base scraper class for Alexandrea Library.

This module provides the foundation for all scrapers in the system.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup


class BaseScraper(ABC):
    """
    Base class for all scrapers.

    All scraper implementations should inherit from this class and
    implement the required methods.
    """

    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None):
        """
        Initialize the scraper with a base URL and optional headers.

        Args:
            base_url: Base URL for the scraping target
            headers: Optional HTTP headers for requests
        """
        self.base_url = base_url
        self.headers = headers or {}
        self.logger = logging.getLogger(self.__class__.__name__)

    def parse_html(self, html_content):
        """Parse HTML content using BeautifulSoup."""
        return BeautifulSoup(html_content, "html.parser")

    @abstractmethod
    def fetch(self, endpoint: str) -> Any:
        """
        Fetch data from the specified endpoint.

        Args:
            endpoint: API endpoint or URL path to fetch

        Returns:
            The fetched data in an appropriate format
        """
        pass

    @abstractmethod
    def parse(self, data: Any) -> List[Dict[str, Any]]:
        """
        Parse the fetched data into a structured format.

        Args:
            data: Raw data fetched from the source

        Returns:
            Parsed data as a list of dictionaries
        """
        pass

    def run(self, endpoint: str) -> List[Dict[str, Any]]:
        """
        Run the complete scrape process: fetch and parse.

        Args:
            endpoint: API endpoint or URL path to fetch

        Returns:
            Processed data as a list of dictionaries
        """
        data = self.fetch(endpoint)
        return self.parse(data)
