from abc import ABC, abstractmethod

class LLMService(ABC):
    """Abstract interface for a Large Language Model service."""

    @abstractmethod
    def analyze_code_changes(self, prompt: str) -> str:
        """Analyzes code changes using the language model."""
        pass
