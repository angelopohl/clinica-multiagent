import google.generativeai as genai
from app.config import settings
import json
import re

class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if not self.api_key:
            print("WARNING: GEMINI_API_KEY is not set.")
        else:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
    def generate_response(self, prompt: str) -> str:
        if not self.api_key:
            return "Error: Gemini API Key is missing. Please configure it in .env"
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error calling Gemini: {e}")
            return f"Error processing the request: {str(e)}"

    def generate_json(self, prompt: str) -> dict:
        """
        Forces the model to output JSON and parses it.
        """
        if not self.api_key:
            return {"error": "API Key missing"}
        
        try:
            full_prompt = f"{prompt}\n\nReturn ONLY a valid JSON object. No markdown formatting, no backticks."
            response = self.model.generate_content(full_prompt)
            
            text = response.text.strip()
            
            # Clean markdown JSON formatting
            match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
            if match:
                text = match.group(1)
            else:
                text = text.strip("` \n")
                if text.startswith("json"):
                    text = text[4:].strip()
            
            return json.loads(text)
        except Exception as e:
            print(f"Failed to decode JSON from Gemini. Error: {e}")
            return {"intent": "unknown", "entities": {}}

# Singleton instance
gemini_service = GeminiService()
