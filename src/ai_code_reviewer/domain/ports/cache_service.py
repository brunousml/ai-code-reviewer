from abc import ABC, abstractmethod
from typing import Optional

class CacheService(ABC):
    """Abstract interface for a caching service."""

    @abstractmethod
    def get(self, key: str) -> Optional[str]:
        """Retrieves an item from the cache by key."""
        pass

    @abstractmethod
    def set(self, key: str, value: str) -> None:
        """Stores an item in the cache."""
        pass
