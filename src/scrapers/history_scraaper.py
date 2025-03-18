from .base_scraper import BaseScraper
import re
import json
import os
from datetime import datetime
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Union

class AncientHistoryScraper(BaseScraper):
	"""Scraper specialized for ancient history websites."""
	
	def __init__(self, base_url: str):
		super().__init__(base_url)
		self.categories = ["mesopotamia", "egypt", "greece", "rome", "china", "india"]
	
	def extract_data(self, soup: BeautifulSoup) -> Dict[str, Union[str, List]]:
		"""Extract history-related content from the page."""
		# Extract title
		title = soup.find('h1')
		title_text = title.text.strip() if title else "No Title"
		
		# Extract main content
		content_div = soup.find('div', class_=re.compile(r'(content|article|main)'))
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
			"references": references,
			"timestamp": datetime.now().timestamp()
		}
	
	def process_data(self, data: Optional[Dict]) -> Optional[Dict]:
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
	
	def save_data(self, data: Optional[Dict], filename: Optional[str] = None) -> bool:
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
