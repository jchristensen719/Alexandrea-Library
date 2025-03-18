# Module 2: Web Crawlers & Scrapers Development

This module will guide you through creating modular, efficient web crawlers and scrapers that respect website policies while effectively gathering data for your three focus niches.

## Understanding Web Scraping Fundamentals

### Types of Web Scraping
1. **Static HTML Scraping**: Using libraries like BeautifulSoup to parse static HTML
2. **Dynamic Content Scraping**: Using Selenium or Playwright to interact with JavaScript-rendered content
3. **API-based Data Retrieval**: Using REST APIs when available (often the most reliable method)

### Ethical and Legal Considerations
1. **Always respect robots.txt**: Check if scraping is allowed before proceeding
2. **Rate limiting**: Implement delays between requests to avoid overloading servers
3. **Terms of Service**: Be aware that some websites explicitly prohibit scraping
4. **Personal data**: Be cautious about scraping and storing personal information (GDPR concerns)

## Building Your Basic Scraper Framework

### Step 1: Create a Base Scraper Class

```python
import requests
import time
import random
from urllib.robotparser import RobotFileParser
import logging
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
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
```

### Step 2: Create Specialized Scrapers for Each Niche

#### Ancient History Scraper
Create a file `src/scrapers/history_scraper.py`:

```python
from .base_scraper import BaseScraper
import re
import json
import os

class AncientHistoryScraper(BaseScraper):
    """Scraper specialized for ancient history websites."""
    
    def __init__(self, base_url):
        super().__init__(base_url)
        self.categories = ["mesopotamia", "egypt", "greece", "rome", "china", "india"]
    
    def extract_data(self, soup):
        """Extract history-related content from the page."""
        # Extract title
        title = soup.find('h1')
        title_text = title.text.strip() if title else "No Title"
        
        # Extract main content
        content_div = soup.find('div', class_=re.compile('(content|article|main)'))
        paragraphs = content_div.find_all('p') if content_div else []
        content = "\n\n".join([p.text.strip() for p in paragraphs])
        
        # Extract time period or dates
        date_pattern = r'\b\d{1,4}(?:\s*(?:BC|BCE|AD|CE))?\b'
        dates = re.findall(date_pattern, content)
        
        # Extract images with captions
        images = []
        for img in soup.find_all('img'):
            if img.get('alt'):
                images.append({
                    'url': img.get('src', ''),
                    'caption': img.get('alt', '')
                })
        
        # Extract references
        references = []
        refs = soup.find_all(['cite', 'blockquote']) 
        for ref in refs:
            references.append(ref.text.strip())
        
        return {
            "title": title_text,
            "content": content,
            "dates": dates,
            "images": images,
            "references": references
        }
    
    def process_data(self, data):
        """Process and categorize the extracted history data."""
        if not data or not data.get("content"):
            return None
            
        # Categorize content
        categories = []
        content_lower = data["content"].lower()
        
        for category in self.categories:
            if category in content_lower:
                categories.append(category)
        
        # Add time period classification
        if any("BC" in date or "BCE" in date for date in data["dates"]):
            if any(int(re.sub(r'[^\d]', '', date)) > 500 for date in data["dates"] if re.sub(r'[^\d]', '', date)):
                categories.append("classical_antiquity")
            else:
                categories.append("ancient_world")
        
        # Extract wisdom/philosophical content
        if re.search(r'\b(philosoph|wisdom|ethics|virtue|knowledge)\b', content_lower):
            categories.append("ancient_wisdom")
            
        # Add processed data
        data["categories"] = categories
        data["word_count"] = len(data["content"].split())
        
        return data
    
    def save_data(self, data, filename=None):
        """Save the scraped data to a JSON file."""
        if not data:
            return False
            
        os.makedirs("data/raw/history", exist_ok=True)
        
        if not filename:
            filename = f"history_{int(data['timestamp'])}.json"
            
        with open(f"data/raw/history/{filename}", 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        self.logger.info(f"Saved data to data/raw/history/{filename}")
        return True
```

#### Stock Market Scraper
Create a file `src/scrapers/stock_market_scraper.py`:

```python
from .base_scraper import BaseScraper
import re
import json
import os
import pandas as pd
from datetime import datetime

class StockMarketScraper(BaseScraper):
    """Scraper specialized for stock market news and data."""
    
    def __init__(self, base_url):
        super().__init__(base_url)
        self.market_terms = [
            "stock", "market", "index", "nasdaq", "dow", "s&p", "nyse", 
            "bull", "bear", "trading", "investor", "etf", "fund", "dividend"
        ]
    
    def extract_data(self, soup):
        """Extract stock market content from the page."""
        # Extract title
        title = soup.find('h1')
        title_text = title.text.strip() if title else "No Title"
        
        # Extract publish date
        date_element = soup.find(['time', 'span'], class_=re.compile('(date|time|publish)'))
        publish_date = date_element.text.strip() if date_element else datetime.now().strftime("%Y-%m-%d")
        
        # Extract main content
        content_div = soup.find('div', class_=re.compile('(content|article|main)'))
        paragraphs = content_div.find_all('p') if content_div else []
        content = "\n\n".join([p.text.strip() for p in paragraphs])
        
        # Extract stock tickers/symbols (usually in uppercase letters)
        ticker_pattern = r'\b[A-Z]{1,5}\b'
        potential_tickers = re.findall(ticker_pattern, content)
        
        # Filter out common words that might be all caps
        common_words = {"A", "I", "AN", "THE", "AND", "OR", "BUT", "FOR", "IF", "CEO", "CFO", "USA"}
        tickers = [ticker for ticker in potential_tickers if ticker not in common_words]
        
        # Extract any numeric data/figures mentioned
        numeric_data = re.findall(r'\$\d+(?:\.\d+)?|\d+(?:\.\d+)?\%', content)
        
        # Look for tables with stock data
        tables = []
        for table in soup.find_all('table'):
            try:
                df = pd.read_html(str(table))[0]
                tables.append(df.to_dict(orient='records'))
            except:
                pass
        
        return {
            "title": title_text,
            "publish_date": publish_date,
            "content": content,
            "tickers": tickers,
            "numeric_data": numeric_data,
            "tables": tables
        }
    
    def process_data(self, data):
        """Process and categorize the extracted stock market data."""
        if not data or not data.get("content"):
            return None
            
        # Categorize content
        categories = []
        content_lower = data["content"].lower()
        
        # Check for market news vs. analysis
        if any(term in content_lower for term in ["forecast", "predict", "outlook", "future"]):
            categories.append("market_forecast")
            
        if any(term in content_lower for term in ["technical analysis", "chart", "pattern", "support", "resistance"]):
            categories.append("technical_analysis")
            
        if any(term in content_lower for term in ["fundamental", "earnings", "revenue", "profit", "growth"]):
            categories.append("fundamental_analysis")
            
        if any(term in content_lower for term in ["dividend", "yield", "payout"]):
            categories.append("dividend_investing")
            
        # Check for specific market segments
        if "crypto" in content_lower or "bitcoin" in content_lower:
            categories.append("cryptocurrency")
            
        if "etf" in content_lower:
            categories.append("etf")
            
        # Add sentiment analysis (very basic)
        positive_words = ["growth", "gain", "profit", "increase", "bullish", "opportunity", "recovery"]
        negative_words = ["loss", "decline", "bearish", "risk", "crash", "bubble", "recession"]
        
        positive_count = sum(content_lower.count(word) for word in positive_words)
        negative_count = sum(content_lower.count(word) for word in negative_words)
        
        if positive_count > negative_count:
            sentiment = "positive"
        elif negative_count > positive_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"
            
        # Add processed data
        data["categories"] = categories
        data["sentiment"] = sentiment
        data["word_count"] = len(data["content"].split())
        
        return data
    
    def save_data(self, data, filename=None):
        """Save the scraped data to a JSON file."""
        if not data:
            return False
            
        os.makedirs("data/raw/stock_market", exist_ok=True)
        
        if not filename:
            filename = f"stock_{int(data['timestamp'])}.json"
            
        with open(f"data/raw/stock_market/{filename}", 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        self.logger.info(f"Saved data to data/raw/stock_market/{filename}")
        return True
```

#### Self-Improvement Scraper
Create a file `src/scrapers/self_improvement_scraper.py`:

```python
from .base_scraper import BaseScraper
import re
import json
import os

class SelfImprovementScraper(BaseScraper):
    """Scraper specialized for self-improvement content."""
    
    def __init__(self, base_url):
        super().__init__(base_url)
        self.improvement_categories = [
            "productivity", "motivation", "mindfulness", "health", "fitness",
            "nutrition", "relationships", "career", "learning", "habits", "goals"
        ]
    
    def extract_data(self, soup):
        """Extract self-improvement content from the page."""
        # Extract title
        title = soup.find('h1')
        title_text = title.text.strip() if title else "No Title"
        
        # Extract main content
        content_div = soup.find('div', class_=re.compile('(content|article|main)'))
        paragraphs = content_div.find_all('p') if content_div else []
        content = "\n\n".join([p.text.strip() for p in paragraphs])
        
        # Extract any lists (often used for tips/steps)
        lists = []
        for list_element in soup.find_all(['ul', 'ol']):
            list_items = [li.text.strip() for li in list_element.find_all('li')]
            if list_items:
                lists.append(list_items)
        
        # Extract any highlighted quotes or tips
        quotes = []
        for quote in soup.find_all(['blockquote', 'div'], class_=re.compile('(quote|highlight|callout|tip)')):
            quotes.append(quote.text.strip())
        
        # Extract headings for structure
        headings = []
        for heading in soup.find_all(['h2', 'h3']):
            headings.append(heading.text.strip())
        
        return {
            "title": title_text,
            "content": content,
            "lists": lists,
            "quotes": quotes,
            "headings": headings
        }
    
    def process_data(self, data):
        """Process and categorize the extracted self-improvement data."""
        if not data or not data.get("content"):
            return None
            
        # Categorize content
        categories = []
        content_lower = data["content"].lower()
        
        for category in self.improvement_categories:
            if category in content_lower:
                categories.append(category)
        
        # Identify content types and formats
        content_type = []
        
        if len(data["lists"]) > 0:
            content_type.append("list_based")
            
        if any(re.search(r'step \d+|day \d+', item) for sublist in data["lists"] for item in sublist):
            content_type.append("step_by_step")
            
        if len(data["quotes"]) > 3:
            content_type.append("quote_heavy")
            
        if re.search(r'scientific|research|study|evidence', content_lower):
            content_type.append("research_based")
            
        if re.search(r'my (story|journey|experience)', content_lower):
            content_type.append("personal_story")
            
        # Check for actionability
        action_phrases = [
            "try this", "do this", "practice", "start", "begin with",
            "implement", "create a", "build a", "develop", "establish"
        ]
        
        if any(phrase in content_lower for phrase in action_phrases):
            content_type.append("actionable")
            
        # Add processed data
        data["categories"] = categories
        data["content_type"] = content_type
        data["word_count"] = len(data["content"].split())
        
        return data
    
    def save_data(self, data, filename=None):
        """Save the scraped data to a JSON file."""
        if not data:
            return False
            
        os.makedirs("data/raw/self_improvement", exist_ok=True)
        
        if not filename:
            filename = f"improvement_{int(data['timestamp'])}.json"
            
        with open(f"data/raw/self_improvement/{filename}", 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        self.logger.info(f"Saved data to data/raw/self_improvement/{filename}")
        return True
```

### Step 3: Create a Dynamic Content Scraper Using Playwright

Create a file `src/scrapers/dynamic_scraper.py`:

```python
from playwright.sync_api import sync_playwright
import time
import random
import logging
import json
import os
from urllib.robotparser import RobotFileParser

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

class DynamicScraper:
    """Scraper for JavaScript-heavy websites using Playwright."""
    
    def __init__(self, base_url, user_agent="AlexandreaLibrary/1.0", headless=True):
        self.base_url = base_url
        self.user_agent = user_agent
        self.headless = headless
        self.logger = logging.getLogger("scraper.DynamicScraper")
        
        # Set up robot parser
        self.robot_parser = RobotFileParser()
        self.robot_parser.set_url(f"{self.base_url}/robots.txt")
        
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
    
    def scrape(self, url, selector_to_wait_for=None, extract_function=None, scroll=False, wait_time=5):
        """
        Scrape a dynamic website using Playwright.
        
        Args:
            url: The URL to scrape
            selector_to_wait_for: CSS selector to wait for before extraction
            extract_function: Custom function to extract data from the page
            scroll: Whether to scroll down the page to load lazy content
            wait_time: How long to wait for the page to load
            
        Returns:
            Extracted data or None if failed
        """
        if not self.can_fetch(url):
            return None
            
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                user_agent=self.user_agent
            )
            
            page = context.new_page()
            
            try:
                # Navigate to the page
                self.logger.info(f"Navigating to {url}")
                page.goto(url, wait_until="domcontentloaded")
                
                # Wait for specific content to load if specified
                if selector_to_wait_for:
                    self.logger.info(f"Waiting for selector: {selector_to_wait_for}")
                    page.wait_for_selector(selector_to_wait_for, timeout=wait_time * 1000)
                else:
                    time.sleep(wait_time)  # Default wait
                
                # Scroll if needed (for lazy-loaded content)
                if scroll:
                    self.logger.info("Scrolling down to load lazy content")
                    for _ in range(3):  # Scroll down 3 times
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        time.sleep(random.uniform(1, 2))  # Random wait between scrolls
                
                # Extract data using a custom function or just return HTML
                if extract_function:
                    data = extract_function(page)
                else:
                    data = {
                        "url": url,
                        "html": page.content(),
                        "timestamp": time.time()
                    }
                
                browser.close()
                return data
                
            except Exception as e:
                self.logger.error(f"Error scraping {url}: {e}")
                browser.close()
                return None
    
    def save_data(self, data, folder="dynamic", filename=None):
        """Save the scraped data to a file."""
        if not data:
            return False
            
        os.makedirs(f"data/raw/{folder}", exist_ok=True)
        
        if not filename:
            filename = f"dynamic_{int(time.time())}.json"
            
        try:
            # If data contains HTML, save it separately
            if "html" in data:
                html_filename = f"{filename.split('.')[0]}.html"
                with open(f"data/raw/{folder}/{html_filename}", 'w', encoding='utf-8') as f:
                    f.write(data["html"])
                
                # Remove HTML from JSON data to avoid duplication
                data_copy = data.copy()
                data_copy["html"] = f"Saved to {html_filename}"
                
                with open(f"data/raw/{folder}/{filename}", 'w', encoding='utf-8') as f:
                    json.dump(data_copy, f, ensure_ascii=False, indent=2)
            else:
                with open(f"data/raw/{folder}/{filename}", 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                    
            self.logger.info(f"Saved data to data/raw/{folder}/{filename}")
            return True
        except Exception as e:
            self.logger.error(