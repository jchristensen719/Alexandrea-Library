from datetime import datetime

import pandas as pd
import yfinance as yf
from bs4 import BeautifulSoup

from .base_scraper import BaseScraper


class StockMarketScraper(BaseScraper):
    """Specialized scraper for financial market data."""

    def __init__(self, base_url, symbols=None):
        super().__init__(base_url)
        self.symbols = symbols or []

    def extract_data(self, soup):
        """Extract data from financial pages."""
        data = {
            "title": soup.title.string if soup.title else None,
            "market_data": {},
            "news": [],
        }

        # Extract financial news headlines
        news_items = soup.find_all("div", class_="news-item")
        for item in news_items:
            data["news"].append(
                {"headline": item.get_text(), "timestamp": datetime.now().isoformat()}
            )

        return data

    def process_data(self, raw_data):
        """Process the extracted market data."""
        return {
            "processed_at": datetime.now().isoformat(),
            "market_data": raw_data.get("market_data", {}),
            "news": raw_data.get("news", []),
        }

    def get_stock_data(self, symbol, period="1d"):
        """Fetch stock data using yfinance."""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            return {
                "symbol": symbol,
                "data": hist.to_dict("records"),
                "info": ticker.info,
            }
        except Exception as e:
            self.logger.error(f"Error fetching data for {symbol}: {e}")
            return None

    def batch_fetch_stocks(self, symbols=None, period="1d"):
        """Fetch data for multiple stock symbols."""
        symbols = symbols or self.symbols
        results = {}

        for symbol in symbols:
            results[symbol] = self.get_stock_data(symbol, period)

        return results
