"""
History scraper for Alexandrea Library.

This module provides functionality for scraping historical book information.
"""

from typing import Any, Dict, List

import requests

from .base_scraper import BaseScraper


class HistoryScraper(BaseScraper):
    """
    Scraper for historical book information from various sources.

    This scraper specializes in retrieving information about historical books,
    including classic literature, historical documents, and manuscripts.
    """

    def fetch(self, endpoint: str) -> Any:
        """
        Fetch historical book data from the API endpoint.

        Args:
            endpoint: API endpoint or URL path to fetch

        Returns:
            JSON response data

        Raises:
            requests.RequestException: If an error occurs during the request
        """
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def parse(self, data: Any) -> List[Dict[str, Any]]:
        """
        Parse historical book data into a structured format.

        Args:
            data: Raw JSON data from the API

        Returns:
            List of book dictionaries with normalized attributes
        """
        if not data or "items" not in data:
            return []

        books = []
        for item in data["items"]:
            # Extract and normalize book data
            book = {
                "title": item.get("title", "Unknown Title"),
                "author": item.get("author", "Unknown Author"),
                "year": item.get("year") or item.get("publicationDate", "Unknown"),
                "publisher": item.get("publisher", "Unknown Publisher"),
                "isbn": item.get("isbn", ""),
                "language": item.get("language", "Unknown"),
                "categories": item.get("categories", []),
                "historical_period": item.get("period", "Unknown"),
                "historical_significance": item.get("significance", ""),
            }
            books.append(book)

        return books

    def search_by_period(self, period: str) -> List[Dict[str, Any]]:
        """
        Search for books by historical period.

        Args:
            period: Historical period (e.g., "Renaissance", "Ancient Greece")

        Returns:
            List of books from the specified period
        """
        return self.run(f"search?period={period}")

    def search_by_author(self, author: str) -> List[Dict[str, Any]]:
        """
        Search for historical books by author.

        Args:
            author: Author name to search for

        Returns:
            List of books by the specified author
        """
        return self.run(f"search?author={author}")
