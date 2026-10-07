import os
import hashlib
import logging
from typing import Optional

from src.ai_code_reviewer.domain.ports.cache_service import CacheService

logger = logging.getLogger(__name__)

class FileCacheService(CacheService):
    """Concrete implementation of CacheService using the local filesystem."""

    def __init__(self, cache_dir: str = ".cache/reviews"):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
        logger.info(f"FileCacheService initialized with directory: {self.cache_dir}")

    def _get_cache_filepath(self, key: str) -> str:
        """Hashes the key to create a stable filepath."""
        hashed_key = hashlib.sha256(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{hashed_key}.txt")

    def get(self, key: str) -> Optional[str]:
        """Retrieves an item from the file cache."""
        filepath = self._get_cache_filepath(key)
        if not os.path.exists(filepath):
            logger.debug(f"Cache miss for key: {key[:50]}...")
            return None

        try:
            with open(filepath, "r") as f:
                content = f.read()
            logger.info(f"Cache hit for key: {key[:50]}...")
            return content
        except IOError as e:
            logger.error(f"Failed to read from cache file {filepath}: {e}")
            return None

    def set(self, key: str, value: str) -> None:
        """Stores an item in the file cache."""
        filepath = self._get_cache_filepath(key)
        try:
            with open(filepath, "w") as f:
                f.write(value)
            logger.info(f"Saved to cache for key: {key[:50]}...")
        except IOError as e:
            logger.error(f"Failed to write to cache file {filepath}: {e}")
