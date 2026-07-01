import os
import requests
import json
import re

class GeminiService:
    def __init__(self):
        # Auto-detect if we should use Google Gemini API or local Ollama
        self.api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("gemini_api_key")
        
        if self.api_key:
            print("Gemini Service: GEMINI_API_KEY detected. Using Google Gemini API cloud service.")
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model_name = os.environ.get("GEMINI_MODEL") or "gemini-2.5-flash"
            self.model = genai.GenerativeModel(self.model_name)
            self.use_cloud = True
        else:
            from app.config import settings
            self.base_url = settings.OLLAMA_URL.rstrip('/')
            self.model_name = settings.OLLAMA_MODEL
            print(f"Gemini Service: No GEMINI_API_KEY found. Falling back to local Ollama '{self.model_name}' at '{self.base_url}'.")
            self.use_cloud = False

    def generate_response(self, prompt: str) -> str:
        if self.use_cloud:
            try:
                response = self.model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                print(f"Error calling Google Gemini API: {e}")
                return f"Error processing request on cloud: {str(e)}"
        else:
            try:
                url = f"{self.base_url}/api/generate"
                payload = {
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3
                    }
                }
                response = requests.post(url, json=payload, timeout=60)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("response", "").strip()
                else:
                    return f"Error calling local Ollama: Status Code {response.status_code}"
            except Exception as e:
                print(f"Error calling local Ollama: {e}")
                return f"Error processing request locally: {str(e)}"

    def generate_json(self, prompt: str) -> dict:
        if self.use_cloud:
            try:
                full_prompt = f"{prompt}\n\nReturn ONLY a valid JSON object. No markdown formatting, no backticks."
                response = self.model.generate_content(full_prompt)
                text = response.text.strip()
                
                # Clean markdown JSON formatting if model outputs it anyway
                match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
                if match:
                    text = match.group(1)
                else:
                    text = text.strip("` \n")
                    if text.startswith("json"):
                        text = text[4:].strip()
                
                return json.loads(text)
            except Exception as e:
                print(f"Failed to decode JSON from Gemini cloud. Error: {e}")
                return {"intent": "unknown", "entities": {}}
        else:
            try:
                url = f"{self.base_url}/api/generate"
                payload = {
                    "model": self.model_name,
                    "prompt": prompt,
                    "format": "json",
                    "stream": False,
                    "options": {
                        "temperature": 0.0
                    }
                }
                response = requests.post(url, json=payload, timeout=60)
                if response.status_code == 200:
                    data = response.json()
                    text = data.get("response", "").strip()
                    return json.loads(text)
                else:
                    print(f"Error calling local Ollama JSON API: {response.status_code}")
                    return {"intent": "unknown", "entities": {}}
            except Exception as e:
                print(f"Failed to retrieve/decode JSON from local Ollama. Error: {e}")
                return {"intent": "unknown", "entities": {}}

# Singleton instance
gemini_service = GeminiService()
