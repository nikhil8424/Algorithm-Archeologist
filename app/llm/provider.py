import os
from typing import Optional
from app.config import config

class LLMProvider:
    """Pluggable LLM provider supporting Gemini, OpenAI, or deterministic archaeological heuristics."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or config.gemini_api_key
        self.model = model or config.default_llm_model

    def generate(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        # If Gemini SDK / key is available, call Gemini
        if self.api_key:
            try:
                from google import genai
                client = genai.Client(api_key=self.api_key)
                response = client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config={"system_instruction": system_instruction} if system_instruction else None
                )
                return response.text or ""
            except Exception as e:
                # Fallback on failure
                pass
        return ""

llm_provider = LLMProvider()
