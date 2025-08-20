import os
from typing import List, Dict, Any
import google.generativeai as genai
from app.domain.external.llm import LLM

class GeminiLLM(LLM):
    """
    Concrete implementation of the LLM interface for Google's Gemini API.
    """
    def __init__(self):
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    async def ask(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Sends a prompt to the Gemini API and returns the response.
        """
        try:
            # The Gemini API expects a list of contents, not a direct message list.
            # We'll construct a simple conversation from the messages.
            # This is a simplification; a real implementation would handle roles.
            prompt = "\n".join([msg["content"] for msg in messages if "content" in msg])
            
            response = await self.model.generate_content_async(prompt)
            return {"content": response.text}
        except Exception as e:
            # In a real application, you'd have more robust error handling.
            print(f"Error calling Gemini API: {e}")
            return {"content": f"An error occurred: {e}"}
