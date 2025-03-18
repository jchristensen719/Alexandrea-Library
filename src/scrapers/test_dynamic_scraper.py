# tests/test_dynamic_scraper.py
import unittest
from src.scrapers.dynamic_scraper import DynamicScraper

class TestDynamicScraper(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.scraper = DynamicScraper("https://example.com")

    def test_initialization(self):
        """Test scraper initialization"""
        self.assertEqual(self.scraper.base_url, "https://example.com")
        self.assertEqual(self.scraper.user_agent, "AlexandreaLibrary/1.0")
        self.assertTrue(self.scraper.headless)

    def test_extract_data(self):
        """Test data extraction from sample HTML"""
        html = "<html><title>Test Page</title></html>"
        soup = self.scraper.parse_html(html)
        data = self.scraper.extract_data(soup)
        self.assertEqual(data["title"], "Test Page")

if __name__ == '__main__':
    unittest.main()