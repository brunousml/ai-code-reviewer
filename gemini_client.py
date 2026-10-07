import logging
import os
import google.generativeai as genai

logger = logging.getLogger(__name__)


class GeminiClient:
    def __init__(self):
        logger.info("Initializing GeminiClient.")
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY environment variable not set.")
            raise ValueError("GEMINI_API_KEY environment variable not set.")

        genai.configure(api_key=api_key)

        self.model_name = os.getenv("GEMINI_MODEL", 'gemini-2.5-flash-lite')
        if not self.model_name:
            logger.error("GEMINI_MODEL environment variable not set.")
            raise ValueError("GEMINI_MODEL environment variable not set.")

        self.model = genai.GenerativeModel(self.model_name)
        logger.debug(f"Using Gemini model: {self.model_name}")

    def analyze_code_changes(self, prompt_template):
        logger.info("Analyzing code changes via Gemini API.")
        logger.debug("Prompt being sent to Gemini: %s", prompt_template)

        try:
            response = self.model.generate_content(prompt_template)
            logger.info("Successfully received response from Gemini API.")
            logger.debug("Gemini API response: %s", response.text)
            return response.text
        except Exception as e:
            logger.error("An error occurred while calling the Gemini API: %s", e)
            raise
