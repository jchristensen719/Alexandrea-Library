"""
Stock market scraper for Alexandrea Library.

This module provides functionality for scraping financial and stock market information.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

from .base_scraper import BaseScraper


class StockMarketScraper(BaseScraper):
    """
    Scraper for stock market and financial information.

    This scraper specializes in retrieving financial data, stock prices,
    market trends, and business publications.
    """

    def __init__(
        self, base_url: str, api_key: str, headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize the stock market scraper.

        Args:
            base_url: Base URL for the financial data API
            api_key: API key for authentication
            headers: Optional HTTP headers for requests
        """
        super().__init__(base_url, headers)
        self.api_key = api_key

    def fetch(self, endpoint: str) -> Any:
        """
        Fetch financial data from the API endpoint.

        Args:
            endpoint: API endpoint or URL path to fetch

        Returns:
            JSON response data

        Raises:
            requests.RequestException: If an error occurs during the request
        """
        url = f"{self.base_url}/{endpoint}"
        params = {"apikey": self.api_key}
        response = requests.get(url, params=params, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def parse(self, data: Any) -> List[Dict[str, Any]]:
        """
        Parse financial data into a structured format.

        Args:
            data: Raw JSON data from the API

        Returns:
            List of financial item dictionaries with normalized attributes
        """
        if not data or not isinstance(data, dict):
            return []

        if "stocks" in data:
            return self._parse_stocks(data["stocks"])
        elif "reports" in data:
            return self._parse_reports(data["reports"])
        else:
            return []

    def _parse_stocks(self, stocks_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse stock information."""
        return [
            {
                "symbol": stock.get("symbol", ""),
                "name": stock.get("name", ""),
                "price": float(stock.get("price", 0)),
                "change": float(stock.get("change", 0)),
                "change_percent": float(stock.get("changePercent", 0)),
                "market_cap": stock.get("marketCap"),
                "volume": stock.get("volume"),
                "timestamp": datetime.fromisoformat(
                    stock.get("timestamp", datetime.now().isoformat())
                ),
            }
            for stock in stocks_data
        ]

    def _parse_reports(
        self, reports_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Parse financial reports."""
        return [
            {
                "id": report.get("id", ""),
                "title": report.get("title", ""),
                "author": report.get("author", ""),
                "publication": report.get("publication", ""),
                "date": report.get("date"),
                "summary": report.get("summary", ""),
                "keywords": report.get("keywords", []),
                "url": report.get("url", ""),
            }
            for report in reports_data
        ]

    def get_stock_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get the current price for a specific stock.

        Args:
            symbol: Stock symbol (e.g., "AAPL")

        Returns:
            Stock information
        """
        result = self.run(f"quote/{symbol}")
        return result[0] if result else {}

    def get_market_news(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the latest market news and reports.

        Args:
            limit: Maximum number of news items to retrieve

        Returns:
            List of market news items
        """
        return self.run(f"news?limit={limit}")
