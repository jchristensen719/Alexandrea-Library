import unittest

from src.llm_integration.ollama_handler import OllamaHandler


class TestOllamaHandler(unittest.TestCase):
    def setUp(self):
        self.handler = OllamaHandler()
        
    def test_initialization(self):
        self.assertEqual(self.handler.model_name, "mistral")
        self.assertEqual(self.handler.api_url, "http://localhost:11434")
        
    def test_prepare_prompt(self):
        content = {"data": {"title": "Test", "content": "Sample content"}}
        prompt = self.handler._prepare_prompt(content)
        self.assertIsInstance(prompt, str)
        self.assertIn("content", prompt.lower())

    def test_memory_config(self):
        result = self.handler.process_content("Hello, world!")
        self.assertTrue(result['success'])
        self.assertEqual(result['model'], "tinyllama")

if __name__ == '__main__':
    unittest.main()
