from abc import ABC, abstractmethod

class StorageService(ABC):
    """Abstract interface for a storage service."""

    @abstractmethod
    def save_review(self, merge_request_iid: int, review_content: str) -> str:
        """Saves the review content and returns the path to the saved file."""
        pass
