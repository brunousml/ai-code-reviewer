import logging
import os
import subprocess

from src.ai_code_reviewer.domain.ports.llm_service import LLMService

logger = logging.getLogger(__name__)

class GeminiCliService(LLMService):
    """Concrete implementation of LLMService using the Gemini CLI."""

    def __init__(self):
        logger.info("Initializing GeminiCliService.")
        self.model = os.getenv("GEMINI_MODEL")
        if not self.model:
            logger.error("GEMINI_MODEL environment variable not set.")
            raise ValueError("GEMINI_MODEL environment variable not set.")
        logger.debug(f"Using Gemini model: {self.model}")

    def analyze_code_changes(self, prompt: str) -> str:
        logger.info("Analyzing code changes via Gemini CLI.")
        logger.debug("Prompt being sent to Gemini: %s", prompt)

        command = [
            "gemini",
            "-m",
            self.model,
            "-p",
            prompt,
        ]

        try:
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
            )
            logger.info("Successfully received response from Gemini CLI.")
            logger.debug("Gemini CLI stdout: %s", process.stdout)
            if process.stderr:
                logger.warning("Gemini CLI stderr: %s", process.stderr)
            return process.stdout
        except FileNotFoundError:
            logger.error(
                "The 'gemini' command is not found. Please ensure it is installed and in your system's PATH."
            )
            raise
        except subprocess.CalledProcessError as e:
            logger.error(
                "Gemini CLI command failed with exit code %d.", e.returncode
            )
            logger.error("Stderr: %s", e.stderr)
            raise
