from .base_scraper import BaseScraper
import re
import json
import os
import pandas as pd
from datetime import datetime
import logging
from typing import Dict, List, Optional, Union
from bs4 import BeautifulSoup

class StockMarketScraper(BaseScraper):
    """Scraper specialized for stock market news and data."""
    
    def __init__(self, base_url: str):
        """Initialize the stock market scraper with base URL and market terms.
        
        Args:
            base_url (str): The base URL for scraping
        """
        super().__init__(base_url)
        self.market_terms = [
            "stock", "market", "index", "nasdaq", "dow", "s&p", "nyse", 
            "bull", "bear", "trading", "investor", "etf", "fund", "dividend"
        ]
        self.logger = logging.getLogger(__name__)
        
    def extract_data(self, soup: BeautifulSoup) -> Dict[str, Union[str, List]]:
        """Extract stock market content from the page.
        
        Args:
            soup (BeautifulSoup): Parsed HTML content
            
        Returns:
            Dict containing extracted data
        """
        try:
            # Extract title
            title = soup.find('h1')
            title_text = title.text.strip() if title else "No Title"
            
            # Extract publish date
            date_element = soup.find(['time', 'span'], class_=re.compile(r'(date|time|publish)', re.I))
            publish_date = date_element.text.strip() if date_element else datetime.now().strftime("%Y-%m-%d")
            
            # Extract main content
            content_div = soup.find('div', class_=re.compile(r'(content|article|main)', re.I))
            paragraphs = content_div.find_all('p') if content_div else []
            content = "\n\n".join([p.text.strip() for p in paragraphs])
            
            # Extract stock tickers/symbols
            ticker_pattern = r'\b[A-Z]{1,5}\b'
            potential_tickers = re.findall(ticker_pattern, content)
            
            # Filter out common words
            common_words = {"A", "I", "AN", "THE", "AND", "OR", "BUT", "FOR", "IF", "CEO", "CFO", "USA"}
            tickers = list(set([ticker for ticker in potential_tickers if ticker not in common_words]))
            
            # Extract numeric data
            numeric_data = re.findall(r'\$\d+(?:\.\d+)?|\d+(?:\.\d+)?\%', content)
            
            # Extract tables
            tables = []
            for table in soup.find_all('table'):
                try:
                    df = pd.read_html(str(table))[0]
                    tables.append(df.to_dict(orient='records'))
                except Exception as e:
                    self.logger.warning(f"Failed to parse table: {str(e)}")
            
            return {
                "title": title_text,
                "publish_date": publish_date,
                "content": content,
                "tickers": tickers,
                "numeric_data": numeric_data,
                "tables": tables,
                "timestamp": datetime.now().timestamp()
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting data: {str(e)}")
            return None

    def process_data(self, data: Optional[Dict]) -> Optional[Dict]:
        """Process and categorize the extracted stock market data.
        
        Args:
            data (Dict): Raw extracted data
            
        Returns:
            Dict containing processed data, or None if invalid
        """
        if not data or not data.get("content"):
            self.logger.warning("Invalid or empty data received")
            return None
            
        try:
            content_lower = data["content"].lower()
            
            # Categorize content
            categories = []
            category_terms = {
                "market_forecast": ["forecast", "predict", "outlook", "future"],
                "technical_analysis": ["technical analysis", "chart", "pattern", "support", "resistance"],
                "fundamental_analysis": ["fundamental", "earnings", "revenue", "profit", "growth"],
                "dividend_investing": ["dividend", "yield", "payout"],
                "cryptocurrency": ["crypto", "bitcoin", "blockchain"],
                "etf": ["etf", "exchange traded fund"]
            }
            
            for category, terms in category_terms.items():
                if any(term in content_lower for term in terms):
                    categories.append(category)
            
            # Sentiment analysis
            sentiment_words = {
                "positive": ["growth", "gain", "profit", "increase", "bullish", "opportunity", "recovery"],
                "negative": ["loss", "decline", "bearish", "risk", "crash", "bubble", "recession"]
            }
            
            sentiment_scores = {
                sentiment: sum(content_lower.count(word) for word in words)
                for sentiment, words in sentiment_words.items()
            }
            
            sentiment = max(sentiment_scores.items(), key=lambda x: x[1])[0] if any(sentiment_scores.values()) else "neutral"
            
            # Update data dictionary
            data.update({
                "categories": categories,
                "sentiment": sentiment,
                "word_count": len(data["content"].split()),
                "processed_timestamp": datetime.now().timestamp()
            })
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error processing data: {str(e)}")
            return None

    def save_data(self, data: Optional[Dict], filename: Optional[str] = None) -> bool:
        """Save the scraped data to a JSON file.
        
        Args:
            data (Dict): Processed data to save
            filename (str, optional): Custom filename
            
        Returns:
            bool: True if save successful, False otherwise
        """
        if not data:
            self.logger.warning("No data to save")
            return False
            
        try:
            save_dir = "data/raw/stock_market"
            os.makedirs(save_dir, exist_ok=True)
            
            if not filename:
                filename = f"stock_{int(data['timestamp'])}.json"
                
            filepath = os.path.join(save_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"Successfully saved data to {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving data: {str(e)}")
            return False