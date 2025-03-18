# Ollama Integration for Alexandrea Library

## Overview
Ollama allows you to run various open-source AI models locally on your machine, which can significantly reduce costs and latency while providing more privacy for your data processing. This guide will show you how to integrate Ollama into your Alexandrea Library system for content generation, summarization, and data processing.

## Step 1: Install Ollama

### For macOS and Linux
1. Open Terminal and run:
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

### For Windows
1. Download the installer from [Ollama's website](https://ollama.com/download)
2. Run the installer and follow the on-screen instructions

### Verify Installation
After installation, verify Ollama is working:
```bash
ollama --version
```

## Step 2: Download Required Models
Download models relevant to your use cases:

```bash
# General-purpose model for content generation
ollama pull llama3

# Specialized model for code generation
ollama pull codellama

# Smaller, faster model for quick processing
ollama pull mistral
```

## Step 3: Create Ollama Integration Module

Create a file `src/content_generation/ollama_client.py`:

```python
import requests
import json
import time
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/ollama.log"),
        logging.StreamHandler()
    ]
)

class OllamaClient:
    """Client for interacting with locally running Ollama models."""
    
    def __init__(self, base_url="http://localhost:11434", default_model="llama3"):
        self.base_url = base_url
        self.default_model = default_model
        self.logger = logging.getLogger("ollama.client")
        self.api_endpoint = f"{self.base_url}/api/generate"
        
        # Verify connection
        try:
            response = requests.get(f"{self.base_url}/api/version")
            if response.status_code == 200:
                version_info = response.json()
                self.logger.info(f"Connected to Ollama {version_info.get('version', 'unknown version')}")
            else:
                self.logger.warning(f"Connected to Ollama but couldn't get version info. Status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            self.logger.error(f"Could not connect to Ollama at {self.base_url}. Is Ollama running?")
            raise ConnectionError(f"Could not connect to Ollama at {self.base_url}. Is Ollama running?")
    
    def list_models(self):
        """List all available models in the local Ollama instance."""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                return response.json().get('models', [])
            else:
                self.logger.error(f"Failed to list models. Status: {response.status_code}")
                return []
        except Exception as e:
            self.logger.error(f"Error listing models: {e}")
            return []
    
    def generate(self, prompt, model=None, max_tokens=2048, temperature=0.7, stream=False):
        """
        Generate text using the specified Ollama model.
        
        Args:
            prompt: The input text prompt
            model: Model name (defaults to self.default_model)
            max_tokens: Maximum number of tokens to generate
            temperature: Randomness of the generation (0.0 to 1.0)
            stream: Whether to stream the response
            
        Returns:
            Generated text or generator if streaming
        """
        model = model or self.default_model
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature
            }
        }
        
        headers = {"Content-Type": "application/json"}
        
        try:
            if stream:
                return self._stream_response(payload, headers)
            else:
                start_time = time.time()
                response = requests.post(self.api_endpoint, headers=headers, json=payload)
                end_time = time.time()
                
                if response.status_code == 200:
                    result = response.json()
                    self.logger.info(f"Generated {len(result.get('response', ''))} chars in {end_time - start_time:.2f}s")
                    return result.get('response', '')
                else:
                    self.logger.error(f"Generation failed. Status: {response.status_code}")
                    return f"Error: {response.text}"
        
        except Exception as e:
            self.logger.error(f"Error in generate: {e}")
            return f"Error: {str(e)}"
    
    def _stream_response(self, payload, headers):
        """Generator function for streaming responses."""
        with requests.post(self.api_endpoint, headers=headers, json=payload, stream=True) as response:
            if response.status_code != 200:
                self.logger.error(f"Streaming failed. Status: {response.status_code}")
                yield f"Error: {response.text}"
                return
                
            response_text = ""
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line)
                        chunk_text = chunk.get('response', '')
                        response_text += chunk_text
                        yield chunk_text
                    except json.JSONDecodeError:
                        self.logger.warning(f"Could not decode JSON: {line}")
                        
            self.logger.info(f"Streamed {len(response_text)} chars")
    
    def summarize(self, text, model=None, max_length=150):
        """
        Summarize a text using Ollama.
        
        Args:
            text: Text to summarize
            model: Model to use (defaults to self.default_model)
            max_length: Target summary length
            
        Returns:
            Summarized text
        """
        prompt = f"""Please summarize the following text in around {max_length} words or less:

{text}

Summary:"""
        
        return self.generate(prompt, model=model, max_tokens=max_length*2)
    
    def categorize(self, text, categories, model=None):
        """
        Categorize text into one or more of the provided categories.
        
        Args:
            text: Text to categorize
            categories: List of possible categories
            model: Model to use
            
        Returns:
            List of matching categories
        """
        categories_str = ", ".join(categories)
        prompt = f"""Categorize the following text into one or more of these categories: {categories_str}

Text:
{text}

Return ONLY a comma-separated list of matching categories with no explanation."""
        
        result = self.generate(prompt, model=model, temperature=0.1)
        return [cat.strip() for cat in result.split(',')]
    
    def extract_key_information(self, text, model=None):
        """
        Extract key information from a text.
        
        Args:
            text: Text to analyze
            model: Model to use
            
        Returns:
            Dictionary with extracted information
        """
        prompt = f"""Extract key information from the following text. 
Return the result as a JSON object with these keys: 
- main_topic
- key_points (list of 3-5 items)
- entities (list of people, places, organizations)
- sentiment (positive, negative, or neutral)

Text:
{text}

JSON:"""
        
        result = self.generate(prompt, model=model, temperature=0.1)
        
        try:
            # Try to find JSON in the response
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = result[json_start:json_end]
                return json.loads(json_str)
            else:
                self.logger.warning("Could not find JSON in the response")
                return {
                    "error": "Failed to parse JSON",
                    "raw_response": result
                }
        except json.JSONDecodeError:
            self.logger.warning(f"Invalid JSON in response")
            return {
                "error": "Invalid JSON",
                "raw_response": result
            }
```

## Step 4: Create Content Generation Modules Using Ollama

Create a file `src/content_generation/ollama_generator.py`:

```python
from .ollama_client import OllamaClient
import json
import os
import logging
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/content_generator.log"),
        logging.StreamHandler()
    ]
)

class ContentGenerator:
    """Generate various content types using Ollama models."""
    
    def __init__(self, model_map=None):
        self.client = OllamaClient()
        self.logger = logging.getLogger("content.generator")
        
        # Default model mapping for different content types
        self.model_map = model_map or {
            "article": "llama3",
            "blog": "llama3",
            "summary": "mistral",
            "social": "mistral",
            "ebook": "llama3",
            "script": "llama3",
            "analysis": "llama3:latest"
        }
        
        # Verify available models
        available_models = [model['name'] for model in self.client.list_models()]
        self.logger.info(f"Available models: {', '.join(available_models)}")
        
        # Check if our mapped models are available
        for content_type, model in self.model_map.items():
            model_base = model.split(':')[0]  # Handle model:tag format
            if model_base not in [m.split(':')[0] for m in available_models]:
                self.logger.warning(f"Model {model} for {content_type} not found locally. Using default model instead.")
                self.model_map[content_type] = "llama3"  # Fallback to default
    
    def _get_model_for_content_type(self, content_type):
        """Get the appropriate model for a content type."""
        return self.model_map.get(content_type, self.model_map.get("article"))
    
    def generate_blog_post(self, topic, data_sources=None, word_count=800):
        """
        Generate a blog post on the given topic.
        
        Args:
            topic: The blog post topic
            data_sources: Optional list of data sources to reference
            word_count: Target word count
            
        Returns:
            Generated blog post text
        """
        model = self._get_model_for_content_type("blog")
        
        # Create data sources section if provided
        data_section = ""
        if data_sources:
            data_section = "Reference these data points in your article:\n"
            for source in data_sources:
                data_section += f"- {source}\n"
        
        prompt = f"""Write an engaging, informative blog post about {topic}.

{data_section}
The blog post should be approximately {word_count} words.
Include a catchy title, introduction, several subheadings, and a conclusion.
Write in a conversational yet authoritative tone.
Include actionable advice where appropriate.

Blog Post:"""
        
        self.logger.info(f"Generating blog post about: {topic}")
        result = self.client.generate(prompt, model=model, max_tokens=word_count*2)
        
        return result
    
    def generate_social_media_post(self, topic, platform="all", data_source=None):
        """
        Generate a social media post on the given topic.
        
        Args:
            topic: The post topic
            platform: Target platform (twitter, linkedin, facebook, instagram, or all)
            data_source: Optional data source to reference
            
        Returns:
            Generated social media post(s)
        """
        model = self._get_model_for_content_type("social")
        
        # Adjust prompt based on platform
        if platform.lower() == "twitter":
            max_length = "280 characters"
        elif platform.lower() == "linkedin":
            max_length = "approximately 200 words"
        elif platform.lower() == "facebook":
            max_length = "approximately 100 words"
        elif platform.lower() == "instagram":
            max_length = "approximately 100 words and include 5 relevant hashtags"
        else:  # all platforms
            return {
                "twitter": self.generate_social_media_post(topic, "twitter", data_source),
                "linkedin": self.generate_social_media_post(topic, "linkedin", data_source),
                "facebook": self.generate_social_media_post(topic, "facebook", data_source),
                "instagram": self.generate_social_media_post(topic, "instagram", data_source)
            }
        
        # Create data source reference if provided
        data_reference = f"\nReference this information: {data_source}" if data_source else ""
        
        prompt = f"""Write an engaging social media post for {platform} about {topic}.
The post should be {max_length}.
Use an appropriate tone for the platform.{data_reference}

{platform.capitalize()} Post:"""
        
        self.logger.info(f"Generating {platform} post about: {topic}")
        result = self.client.generate(prompt, model=model, max_tokens=500)
        
        return result
    
    def generate_ebook_outline(self, topic, chapters=7):
        """
        Generate an eBook outline on the given topic.
        
        Args:
            topic: The eBook topic
            chapters: Number of chapters to include
            
        Returns:
            Generated eBook outline
        """
        model = self._get_model_for_content_type("ebook")
        
        prompt = f"""Create a detailed outline for an eBook about {topic}.

The outline should include:
1. A compelling title
2. An introduction section explaining the eBook's purpose
3. {chapters} chapter titles
4. For each chapter, include 3-5 subsections
5. A conclusion section

Make the outline detailed enough to serve as a writing guide.

eBook Outline:"""
        
        self.logger.info(f"Generating eBook outline about: {topic}")
        result = self.client.generate(prompt, model=model, max_tokens=2000)
        
        return result
    
    def generate_ebook_chapter(self, title, outline, word_count=2000):
        """
        Generate a complete eBook chapter.
        
        Args:
            title: Chapter title
            outline: Bullet points or description of what to include
            word_count: Target word count
            
        Returns:
            Generated chapter text
        """
        model = self._get_model_for_content_type("ebook")
        
        prompt = f"""Write a complete, engaging chapter for an eBook with the title: "{title}"

Chapter outline:
{outline}

Write approximately {word_count} words.
Include relevant subheadings.
Use an informative, educational tone.
Make sure content is well-structured and flows naturally.
Include examples or anecdotes where appropriate.

Chapter:"""
        
        self.logger.info(f"Generating eBook chapter: {title}")
        result = self.client.generate(prompt, model=model, max_tokens=word_count*2)
        
        return result
    
    def generate_market_analysis(self, ticker_or_topic, data_points=None):
        """
        Generate a market analysis for a stock or market topic.
        
        Args:
            ticker_or_topic: Stock ticker or market topic
            data_points: Optional list of data points to include
            
        Returns:
            Generated market analysis
        """
        model = self._get_model_for_content_type("analysis")
        
        # Create data points section if provided
        data_section = ""
        if data_points:
            data_section = "Reference these data points in your analysis:\n"
            for point in data_points:
                data_section += f"- {point}\n"
        
        prompt = f"""Write a detailed market analysis about {ticker_or_topic}.

{data_section}
Include:
1. An overview of the current situation
2. Key factors affecting performance
3. Potential future scenarios
4. Considerations for investors

Write in a balanced, analytical tone. Present different perspectives.
Be careful not to make definitive predictions.

Market Analysis:"""
        
        self.logger.info(f"Generating market analysis for: {ticker_or_topic}")
        result = self.client.generate(prompt, model=model, max_tokens=1500)
        
        return result
    
    def generate_historical_narrative(self, topic, time_period, word_count=1500):
        """
        Generate a historical narrative about a specific topic.
        
        Args:
            topic: Historical topic
            time_period: Time period to cover
            word_count: Target word count
            
        Returns:
            Generated historical narrative
        """
        model = self._get_model_for_content_type("article")
        
        prompt = f"""Write an engaging historical narrative about {topic} during the {time_period} period.

The narrative should be approximately {word_count} words.
Include:
1. Important events and their context
2. Key historical figures
3. The social, political, or cultural significance
4. Interesting details that might not be widely known

Write in an engaging, educational style that brings history to life.
Maintain historical accuracy while being engaging.

Historical Narrative:"""
        
        self.logger.info(f"Generating historical narrative about: {topic} in {time_period}")
        result = self.client.generate(prompt, model=model, max_tokens=word_count*2)
        
        return result
    
    def save_content(self, content, category, title, format="txt"):
        """
        Save generated content to a file.
        
        Args:
            content: The content to save
            category: Content category
            title: Content title
            format: File format (txt, md, json)
            
        Returns:
            Path to the saved file
        """
        # Clean the title for use as filename
        clean_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in title)
        clean_title = clean_title.replace(" ", "_")[:50]  # Truncate long titles
        
        timestamp = int(time.time())
        filename = f"{clean_title}_{timestamp}.{format}"
        
        # Create directory if it doesn't exist
        directory = f"data/processed/{category}"
        os.makedirs(directory, exist_ok=True)
        
        filepath = os.path.join(directory, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            if format == "json":
                json.dump(content, f, ensure_ascii=False, indent=2)
            else:
                f.write(content)
        
        self.logger.info(f"Saved content to {filepath}")
        return filepath
```

## Step 5: Create an Orange Data Miner Integration with Ollama

Since Orange Data Miner doesn't have a direct Python API, we'll create a preprocessing script that can be used before Orange:

Create a file `src/data_processing/ollama_preprocessor.py`:

```python
import os
import json
import glob
import pandas as pd
import logging
from ..content_generation.ollama_client import OllamaClient

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/preprocessor.log"),
        logging.StreamHandler()
    ]
)

class OllamaPreprocessor:
    """Preprocess data using Ollama for easier import into Orange Data Miner."""
    
    def __init__(self, model="mistral"):
        self.client = OllamaClient(default_model=model)
        self.logger = logging.getLogger("ollama.preprocessor")
    
    def preprocess_directory(self, directory, output_csv=None):
        """
        Preprocess all JSON files in a directory and create a CSV for Orange.
        
        Args:
            directory: Directory containing JSON data files
            output_csv: Path to save the output CSV
            
        Returns:
            Path to the output CSV
        """
        if not os.path.exists(directory):
            self.logger.error(f"Directory not found: {directory}")
            return None
            
        # Get all JSON files in the directory
        json_files = glob.glob(os.path.join(directory, "*.json"))
        if not json_files:
            self.logger.warning(f"No JSON files found in {directory}")
            return None
            
        self.logger.info(f"Found {len(json_files)} JSON files in {directory}")
        
        # Process each file
        processed_data = []
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract the main content text
                content = ""
                if "content" in data:
                    content = data["content"]
                elif "data" in data and "content" in data["data"]:
                    content = data["data"]["content"]
                
                if not content:
                    self.logger.warning(f"No content found in {json_file}")
                    continue
                
                # Generate summaries and extract info using Ollama
                summary = self.client.summarize(content[:10000], max_length=100)  # Truncate long content
                
                # Extract entities and topics
                info = self.client.extract_key_information(content[:10000])
                
                # Create processed record
                processed_record = {
                    "file": os.path.basename(json_file),
                    "title": data.get("title", data.get("data", {}).get("title", "")),
                    "summary": summary,
                    "word_count": len(content.split()),
                    "main_topic": info.get("main_topic", ""),
                    "sentiment": info.get("sentiment", ""),
                    "entities": ", ".join(info.get("entities", [])) if isinstance(info.get("entities", []), list) else "",
                    "key_points": ", ".join(info.get("key_points", [])) if isinstance(info.get("key_points", []), list) else ""
                }
                
                # Add any categories from the original data
                if "categories" in data:
                    processed_record["categories"] = ", ".join(data["categories"]) if isinstance(data["categories"], list) else data["categories"]
                
                processed_data.append(processed_record)
                self.logger.info(f"Processed {os.path.basename(json_file)}")
                
            except Exception as e:
                self.logger.error(f"Error processing {json_file}: {e}")
        
        if not processed_data:
            self.logger.warning("No data was successfully processed")
            return None
        
        # Create a DataFrame
        df = pd.DataFrame(processed_data)
        
        # Save to CSV
        if not output_csv:
            dir_name = os.path.basename(os.path.normpath(directory))
            output_csv = f"data/processed/{dir_name}_processed.csv"
        
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        df.to_csv(output_csv, index=False)
        self.logger.info(f"Saved processed data to {output_csv}")
        
        return output_csv
    
    def preprocess_for_orange(self, data_dirs, output_dir="data/processed/orange"):
        """
        Preprocess multiple data directories for Orange Data Miner.
        
        Args:
            data_dirs: List of directories to process
            output_dir: Directory to save output files
            
        Returns:
            List of output CSV paths
        """
        os.makedirs(output_dir, exist_ok=True)
        
        output_files = []
        for data_dir in data_dirs:
            if not os.path.exists(data_dir):
                self.logger.warning(f"Directory not found: {data_dir}")
                continue
                
            dir_name = os.path.basename(os.path.normpath(data_dir))
            output_csv = os.path.join(output_dir, f"{dir_name}_orange.csv")
            
            result = self.preprocess_directory(data_dir, output_csv)
            if result:
                output_files.append(result)
        
        # Create a combined dataset for all data
        if len(output_files) > 1:
            try:
                dfs = [pd.read_csv(file) for file in output_files]
                combined_df = pd.concat(dfs, ignore_index=True)
                
                combined_csv = os.path.join(output_dir, "combined_orange.csv")
                combined_df.to_csv(combined_csv, index=False)
                output_files.append(combined_csv)
                self.logger.info(f"Created combined dataset at {combined_csv}")
                
            except Exception as e:
                self.logger.error(f"Error creating combined dataset: {e}")
        
        return output_files
```

## Step 6: Create an Orchestration Script

Create a file `src/orchestration/ollama_pipeline.py`:

```python
import sys
import os
import time
import schedule
import logging
import json
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.scrapers.history_scraper import AncientHistoryScraper
from src.scrapers.stock_market_scraper import StockMarketScraper
from src.scrapers.self_improvement_scraper import SelfImprovementScraper
from src.scrapers.dynamic_scraper import DynamicScraper
from src.data_processing.ollama_preprocessor import OllamaPreprocessor
from src.content_generation.ollama_generator import ContentGenerator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/pipeline.log"),
        logging.StreamHandler()
    ]
)

class AlexandreaOllamaPipeline:
    """Orchestration pipeline for the Alexandrea Library system with Ollama integration."""
    
    def __init__(self, config_file="config/pipeline_config.json"):
        self.logger = logging.getLogger("pipeline")
        
        # Load configuration
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    self.config = json.load(f)
                self.logger.info(f"Loaded configuration from {config_file}")
            else:
                self.logger.warning(f"Config file {config_file} not found, using defaults")
                self.config = self._default_config()
                
                # Create config directory and save default config
                os.makedirs(os.path.dirname(config_file), exist_ok=True)
                with open(config_file, 'w') as f:
                    json.dump(self.config, f, indent=2)
                    
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            self.config = self._default_config()
        
        # Initialize components
        self._init_components()
    
    def _default_config(self):
        """Create default configuration."""
        return {
            "scraping": {
                "history_sources": [
                    "https://www.ancient.eu/",
                    "https://www.worldhistory.org/"
                ],
                "stock_market_sources": [
                    "https://finance.yahoo.com/",
                    "https://www.marketwatch.com/"
                ],
                "self_improvement_sources": [
                    "https://www.lifehack.org/",
                    "https://zenhabits.net/"
                ],
                "max_pages_per_source": 5,
                "scraping_interval_hours": 24
            },
            "processing": {
                "ollama_model": "mistral",
                "preprocessing_batch_size": 50
            },
            "content_generation": {
                "model_map": {
                    "article": "llama3",
                    "blog": "llama3",
                    "summary": "mistral",
                    "social": "mistral",
                    "ebook": "llama3",
                    "script": "llama3",
                    "analysis": "llama3"
                },
                "weekly_content_plan": {
                    "blog_posts": 2,
                    "social_media_posts": 5,
                    "market_analyses": 1
                }
            },
            "scheduling": {
                "scrape_time": "01:00",  # 1 AM
                "process_time": "03:00",  # 3 AM
                "generate_time": "05:00"  # 5 AM
            }
        }
    
    def _init_components(self):
        """Initialize all pipeline components."""
        # Initialize scrapers
        self.history_scraper = None
        self.stock_scraper = None
        self.improvement_scraper = None
        self.dynamic_scraper = None
        
        # Initialize processor
        self.preprocessor = OllamaPreprocessor(model=self.config["processing"]["ollama_model"])
        
        # Initialize content generator
        self.content_generator = ContentGenerator(model_map=self.config["content_generation"]["model_map"])
        
        self.logger.info("Pipeline components initialized")
    
    def _init_scraper(self, scraper_type, base_url):
        """Initialize a specific scraper on demand."""
        if scraper_type == "history":
            return AncientHistoryScraper(base_url)
        elif scraper_type == "stock":
            return StockMarketScraper(base_url)
        elif scraper_type == "improvement":
            return SelfImprovementScraper(base_url)
        elif scraper_type == "dynamic":
            return DynamicScraper(base_url)
        else:
            self.logger.error(f"Unknown scraper type: {scraper_type}")
            return None
    
    def run_scraping_job(self):
        """Run the data scraping job."""
        self.logger.info("Starting scraping job")
        
        # Scrape Ancient History sources
        for source in self.config["scraping"]["history_sources"]:
            try:
                scraper = self._init_scraper("history", source)
                if not scraper:
                    continue
                    
                # Here you would add logic to traverse the site and find pages to scrape
                # This is a simplified example
                for i in range(self.config["scraping"]["max_pages_per_source"]):
                    url = f"{source}article{i+1}"  # This is a placeholder
                    data = scraper.scrape(url)
                    if data:
                        scraper.save_data(data)
                    
            except Exception as e:
                self.logger.error(f"Error scraping {source}: {e}")
        
        # Similarly for other sources...
        # (Implement similarly for stock market and self-improvement)
        
        self.logger.info("Scraping job completed")
    
    def run_processing_job