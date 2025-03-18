import requests
import time
import random
from urllib.robotparser import RobotFileParser
import logging
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from playwright.sync_api import sync_playwright

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/scraper.log"),
        logging.StreamHandler()
    ]
)

class BaseScraper(ABC):
    """Base class for all scrapers in the Alexandrea Library system."""
    
    def __init__(self, base_url, user_agent="AlexandreaLibrary/1.0"):
        self.base_url = base_url
        self.user_agent = user_agent
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
        self.robot_parser = RobotFileParser()
        self.robot_parser.set_url(f"{self.base_url}/robots.txt")
        self.logger = logging.getLogger(f"scraper.{self.__class__.__name__}")
        
        try:
            self.robot_parser.read()
            self.logger.info(f"Robot.txt parsed for {base_url}")
        except Exception as e:
            self.logger.warning(f"Could not parse robots.txt for {base_url}: {e}")
    
    def can_fetch(self, url):
        """Check if scraping is allowed for this URL according to robots.txt."""
        can_fetch = self.robot_parser.can_fetch(self.user_agent, url)
        if not can_fetch:
            self.logger.warning(f"Robots.txt disallows scraping: {url}")
        return can_fetch
    
    def get_page(self, url, params=None):
        """Fetch a page with rate limiting and robots.txt check."""
        if not self.can_fetch(url):
            return None
        
        # Random delay between 1-3 seconds to be respectful
        time.sleep(random.uniform(1, 3))
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return None
    
    def parse_html(self, html_content):
        """Parse HTML content using BeautifulSoup."""
        return BeautifulSoup(html_content, 'html.parser')
    
    @abstractmethod
    def extract_data(self, soup):
        """Extract relevant data from the parsed HTML.
        This method should be implemented by each specific scraper.
        """
        pass
    
    @abstractmethod
    def process_data(self, data):
        """Process and clean the extracted data.
        This method should be implemented by each specific scraper.
        """
        pass
    
    def scrape(self, url, params=None):
        """Main method to scrape a URL and extract data."""
        response = self.get_page(url, params)
        if not response:
            return None
        
        soup = self.parse_html(response.text)
        raw_data = self.extract_data(soup)
        processed_data = self.process_data(raw_data)
        
        return {
            "url": url,
            "timestamp": time.time(),
            "data": processed_data
        }

class DynamicScraper(BaseScraper):
    """Scraper for JavaScript-heavy websites using Playwright."""
    
    def __init__(self, base_url, user_agent="AlexandreaLibrary/1.0", headless=True):
        super().__init__(base_url, user_agent)
        self.headless = headless
    
    def extract_data(self, soup):
        """Extract data from BeautifulSoup object."""
        # Implement specific extraction logic
        return {"title": soup.title.string if soup.title else None}
    
    def process_data(self, raw_data):
        """Process the extracted raw data."""
        # Implement specific processing logic
        return raw_data
    
    def scrape(self, url, selector_to_wait_for=None, wait_time=5):
        """Scrape a dynamic website using Playwright."""
        if not self.can_fetch(url):
            return None
            
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(user_agent=self.user_agent)
            page = context.new_page()
            
            try:
                self.logger.info(f"Navigating to {url}")
                page.goto(url, wait_until="domcontentloaded")
                
                if selector_to_wait_for:
                    page.wait_for_selector(selector_to_wait_for, timeout=wait_time * 1000)
                else:
                    time.sleep(wait_time)
                
                soup = self.parse_html(page.content())
                raw_data = self.extract_data(soup)
                processed_data = self.process_data(raw_data)
                
                browser.close()
                return {
                    "url": url,
                    "timestamp": time.time(),
                    "data": processed_data
                }
                
            except Exception as e:
                self.logger.error(f"Error scraping {url}: {e}")
                browser.close()
                return None

# test_imports.py
import requests
import beautifulsoup4
from playwright.sync_api import sync_playwright

print("All modules imported successfully!")