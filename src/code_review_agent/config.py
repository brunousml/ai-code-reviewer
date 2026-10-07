import logging
import os

GEMINI_PROMPT = """Please review the following code changes based on the provided context and rules. Offering constructive suggestions and identifying potential issues.

Here are the rules:
{rules}

Here are the code changes:

{changes}

"""

def configure_logging():
    """Configures the root logger for the application."""
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
