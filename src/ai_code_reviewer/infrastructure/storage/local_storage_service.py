import os
import datetime
import logging

from src.ai_code_reviewer.domain.ports.storage_service import StorageService

logger = logging.getLogger(__name__)

class LocalStorageService(StorageService):
    """Concrete implementation of StorageService that saves files locally."""

    def __init__(self, reviews_dir: str = "reviews"):
        self.reviews_dir = reviews_dir
        logger.info(f"LocalStorageService initialized with directory: {self.reviews_dir}")

    def save_review(self, merge_request_iid: int, review_content: str) -> str:
        current_date = datetime.date.today().strftime("%Y-%m-%d")
        review_dir = os.path.join(self.reviews_dir, current_date, str(merge_request_iid))

        os.makedirs(review_dir, exist_ok=True)
        logger.info(f"Created review directory: {review_dir}")

        review_file_path = os.path.join(review_dir, "review.md")
        with open(review_file_path, "w") as f:
            f.write(review_content)

        logger.info(f"Review saved to file: {review_file_path}")
        return review_file_path
