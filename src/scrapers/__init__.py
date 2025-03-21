"""
Scrapers package for Alexandrea Library.
"""

from .base_scraper import BaseScraper
from .history_scraper import HistoryScraper
from .stock_market_scraper import StockMarketScraper

__all__ = ["BaseScraper", "HistoryScraper", "StockMarketScraper"]
