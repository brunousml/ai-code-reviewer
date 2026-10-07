import logging
import os
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

from src.ai_code_reviewer.domain.ports.llm_service import LLMService

logger = logging.getLogger(__name__)

class GeminiService(LLMService):
    """
    Concrete implementation of LLMService using the google-generativeai library.
    It authenticates using Application Default Credentials (ADC).
    """

    def __init__(self):
        logger.info("Initializing GeminiService.")
        # No API key is passed; the library will automatically use Application
        # Default Credentials (ADC) if they are configured.
        # Run `gcloud auth application-default login` to configure ADC.
        try:
            # The library doesn't have an explicit auth check, so we just configure it.
            # An error will be raised on the first API call if auth is missing.
            pass
        except Exception as e:
            logger.error(
                "Failed to configure Gemini. Ensure Application Default Credentials are set.",
                exc_info=True
            )
            raise ValueError(
                "Gemini configuration failed. Have you run 'gcloud auth application-default login'?"
            ) from e

        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
        if not self.model_name:
            logger.error("GEMINI_MODEL environment variable not set.")
            raise ValueError("GEMINI_MODEL environment variable not set.")

        self.model = genai.GenerativeModel(self.model_name)
        logger.debug(f"Using Gemini model: {self.model_name}")

    def analyze_code_changes(self, prompt: str) -> str:
        logger.info("Analyzing code changes via Gemini API.")
        logger.debug("Prompt being sent to Gemini: %s", prompt[:200]) # Log snippet

        try:
            response = self.model.generate_content(prompt)
            logger.info("Successfully received response from Gemini API.")
            logger.debug("Gemini response: %s", response.text[:200]) # Log snippet
            return response.text
        except google_exceptions.PermissionDenied as e:
            logger.error(
                "Gemini API permission denied. Check your ADC and project permissions.",
                exc_info=True
            )
            raise
        except Exception as e:
            logger.error("Gemini API call failed.", exc_info=True)
            raise
