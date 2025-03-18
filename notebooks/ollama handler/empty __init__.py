# src/llm_integration/ollama_handler.py
from ollama import Client

class OllamaHandler:
    def __init__(self, model_name="mistral", api_url="http://localhost:11434"):
        # Fix for test_initialization error
        self.model_name = model_name
        self.api_url = api_url
        self.client = Client(host=api_url)

    def _prepare_prompt(self, content):
        # Fix for test_prepare_prompt error
        """Prepare prompt from content dictionary"""
        if isinstance(content, dict) and 'data' in content:
            return f"Title: {content['data']['title']}\nContent: {content['data']['content']}"
        return str(content)

    def process_content(self, content):
        """Process content using Ollama model"""
        try:
            prompt = self._prepare_prompt(content)
            response = self.client.chat(
                model='tinyllama',
                messages=[{'role': 'user', 'content': prompt}]
            )
            return {
                'success': True,
                'model': 'tinyllama',
                'response': response['message']['content']
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Alexandrea Library - System Architecture

```mermaid
graph TD
    %% Main System
    A[Alexandrea Library] --> B[Data Collection]
    A --> C[Data Processing]
    A --> D[Content Generation]
    A --> E[Content Distribution]

    %% Data Collection Module
    B --> B1[Base Scraper]
    B --> B2[Dynamic Scraper]
    B --> B3[API Integrations]
    B1 --> B1a[History Sources]
    B1 --> B1b[Stock Market Sources]
    B1 --> B1c[Self-Improvement Sources]
    
    %% Data Processing Module
    C --> C1[Orange Data Miner]
    C --> C2[Ollama Integration]
    C --> C3[Database Storage]
    C3 --> C3a[MongoDB]
    C3 --> C3b[SQLite]
    
    %% Content Generation Module
    D --> D1[eBooks]
    D --> D2[Audio Content]
    D --> D3[Video Scripts]
    D --> D4[Blog Posts]
    D --> D5[Email Campaigns]
    
    %% Content Distribution
    E --> E1[Automation]
    E --> E2[Scheduling]
    E --> E3[Analytics]

    %% Data Flow
    B -.-> F1[Raw Data]
    F1 -.-> C
    C -.-> F2[Processed Data]
    F2 -.-> D
    D -.-> F3[Generated Content]
    F3 -.-> E

    %% AI Integration
    G[AI Services] --> G1[Perplexity]
    G --> G2[DeepSeek]
    G --> G3[Claude]
    G --> G4[ChatGPT]
    G -.-> C
    G -.-> D

    %% Styling
    classDef module fill:#f9f,stroke:#333,stroke-width:2px
    classDef data fill:#bbf,stroke:#333,stroke-width:2px
    classDef ai fill:#ffd,stroke:#333,stroke-width:2px
    class B,C,D,E module
    class F1,F2,F3 data
    class G,G1,G2,G3,G4 ai
```

# Current Implementation Status
- ✅ Base Scraper
- ✅ Dynamic Scraper with Playwright
- ✅ Ollama Integration
- 🚧 Content Processing
- 📝 Content Generation
- 📝 Distribution System

# Next Steps
1. Complete the Database Integration
2. Implement Orange Data Miner Pipeline
3. Set up Content Generation Templates
4. Create Automation Scripts