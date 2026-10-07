import logging
import os

import openai

from src.code_review_agent.domain.ports.llm_service import LLMService

logger = logging.getLogger(__name__)

class OpenAIService(LLMService):
    """Concrete implementation of LLMService for OpenAI."""

    def __init__(self, api_key: str, model: str = os.getenv("OPENAI_MODEL", "gpt-5" )):
        logger.info(f"Initializing OpenAIService with model: {model}.")
        if not api_key:
            raise ValueError("OpenAI API key must be provided.")
        self.api_key = api_key
        self.model = model
        openai.api_key = self.api_key

    def analyze_code_changes(self, prompt: str) -> str:
        logger.info("Analyzing code changes using OpenA I.")
        try:
            response = openai.responses.create(
                model=self.model,
                instructions="You are a senior software engineer performing a code review.",
                input=prompt
            )
            review = response.output_text
            if not review:
                raise ValueError("Received an empty review from OpenAI.")
            logger.info("Successfully received review from OpenAI.")
            return review
        except Exception as e:
            logger.error(f"Failed to get review from OpenAI: {e}", exc_info=True)
            raise
