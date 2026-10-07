from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.code_review_agent.domain.entities.pipeline import Pipeline
from src.code_review_agent.domain.entities.job import Job

class VCSService(ABC):
    """Abstract interface for a Version Control System service."""

    @abstractmethod
    def get_merge_request_changes(self, project_path: str, merge_request_iid: int) -> Dict[str, Any]:
        """Fetches the changes for a given merge request."""
        pass

    @abstractmethod
    def post_comment_on_merge_request(self, project_path: str, merge_request_iid: int, note: str) -> None:
        """Posts a comment on a given merge request."""
        pass

    @abstractmethod
    def post_comments_on_merge_request(self, project_path: str, merge_request_iid: int, comments: List[str]) -> None:
        """Posts multiple comments on a given merge request with retry support."""
        pass

    @abstractmethod
    def get_merge_request_comments(self, project_path: str, merge_request_iid: int) -> List[str]:
        """Fetches all comments (notes) for a given merge request."""
        pass

    @abstractmethod
    def get_merge_request_labels(self, project_path: str, merge_request_iid: int) -> List[str]:
        """Fetches the labels for a given merge request."""
        pass

    @abstractmethod
    def remove_merge_request_label(self, project_path: str, merge_request_iid: int, label: str) -> None:
        """Removes a specific label from a merge request."""
        pass

    @abstractmethod
    def get_pipelines(self, project_path: str, days: Optional[int] = None) -> List[Pipeline]:
        """Fetches recent pipelines for a given project, optionally filtered by the number of days."""
        pass

    @abstractmethod
    def list_pipelines_in_range(self, project_path: str, start_date: str, end_date: str) -> List[Pipeline]:
        """Lists pipelines for a given project within a specific date range."""
        pass

    @abstractmethod
    def list_pipeline_jobs(self, project_path: str, pipeline_id: int) -> List[Job]:
        """Lists jobs for a given pipeline."""
        pass

    @abstractmethod
    def get_merged_mrs(self, project_path: str, merged_after: datetime, label: Optional[str] = None) -> List[Any]:
        """Fetches merged MRs for a given project."""
        pass

    @abstractmethod
    def get_project_labels(self, project_path: str) -> List[Any]:
        """Fetches all labels for a given project."""
        pass
