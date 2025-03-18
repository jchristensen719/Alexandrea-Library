import unittest
from src.scrapers.base_scraper import BaseScraper
from src.scrapers.history_scraper import AncientHistoryScraper

class TestAncientHistoryScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = AncientHistoryScraper("https://www.worldhistory.org")
    
    def test_scraper_initialization(self):
        self.assertIsNotNone(self.scraper)
        self.assertEqual(self.scraper.base_url, "https://www.worldhistory.org")
    
    def test_extract_data(self):
        # Add specific test cases for ancient history data extraction
        pass

if __name__ == '__main__':
    unittest.main()