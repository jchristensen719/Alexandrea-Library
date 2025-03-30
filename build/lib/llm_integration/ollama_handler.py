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