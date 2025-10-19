import os
import google.generativeai as genai

_FALLBACK_GEMINI_KEY = "AIzaSyADvzIVXdxT8DOBKU5oByXGgQ5SsOXW6Sw"

class GeminiClient:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", _FALLBACK_GEMINI_KEY)

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def generate_content(self, prompt: str) -> str:
        """Generate text content using Gemini model."""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"[Gemini Error] {e}")
            raise
