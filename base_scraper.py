# src/scrapers/base_scraper.py
import logging
from abc import ABC, abstractmethod

import requests
from bs4 import BeautifulSoup


class BaseScraper(ABC):
    """Base class for all scrapers in the project."""

    def __init__(self, base_url):
        self.base_url = base_url
        self.logger = logging.getLogger(self.__class__.__name__)

    def parse_html(self, html_content):
        """Parse HTML content using BeautifulSoup."""
        return BeautifulSoup(html_content, "html.parser")

    @abstractmethod
    def extract_data(self, soup):
        """Extract data from BeautifulSoup object."""
        pass

    @abstractmethod
    def process_data(self, raw_data):
        """Process the extracted raw data."""
        pass

    @abstractmethod
    def scrape(self, url):
        """Main method to scrape a URL."""
        pass
