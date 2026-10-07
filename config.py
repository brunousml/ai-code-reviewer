import logging
import os

"""
Configuration for the AI Code Reviewer.

This file contains the base prompt template for the Gemini API.
Context files from the 'prompt-contexts' directory will be prepended to this prompt.
"""

GEMINI_PROMPT = """Please review the following code changes based on the provided context and rules. Offering constructive suggestions and identifying potential issues.

Here are the rules:
{rules}

Here are the code changes:

{changes}

"""

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
