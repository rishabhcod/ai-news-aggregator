import logging
import json
from typing import Dict, Any, Optional
from google import genai
from google.genai import types
from app.config import settings
from app.llm.prompts import SUMMARIZE_NEWS_SYSTEM_PROMPT, SUMMARIZE_NEWS_USER_PROMPT

logger = logging.getLogger(__name__)


class SummarizationAgent:
    """Agent that handles LLM-powered summarization using Google Gemini."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model or settings.GEMINI_MODEL
        self._client = None

        if self.api_key:
            try:
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Gemini Client: {e}")

    def summarize(self, title: str, source_name: str, source_type: str, raw_content: str) -> Dict[str, Any]:
        """Generates a structured summary and category for a news item."""
        if not self._client:
            logger.warning("Gemini API Key missing or client not initialized. Using fallback summary.")
            return self._fallback_summary(raw_content)

        user_content = SUMMARIZE_NEWS_USER_PROMPT.format(
            title=title,
            source_name=source_name,
            source_type=source_type,
            content=raw_content[:3000] if raw_content else "No detailed text available."
        )

        try:
            config = types.GenerateContentConfig(
                system_instruction=SUMMARIZE_NEWS_SYSTEM_PROMPT,
                temperature=0.2,
                response_mime_type="application/json"
            )

            response = self._client.models.generate_content(
                model=self.model_name,
                contents=user_content,
                config=config,
            )

            if response.text:
                result = json.loads(response.text)
                return {
                    "summary": result.get("summary", self._fallback_summary(raw_content)["summary"]),
                    "category": result.get("category", "General AI")
                }
        except Exception as e:
            logger.error(f"Gemini API summarization failed for '{title}': {e}")

        return self._fallback_summary(raw_content)

    def _fallback_summary(self, content: str) -> Dict[str, Any]:
        """Provides a simple fallback summary when LLM is unavailable."""
        clean_content = content[:300] if content else "Summary unavailable."
        return {
            "summary": f"- {clean_content}...\n\n**Bottom Line**: Check original source for full details.",
            "category": "General AI"
        }
