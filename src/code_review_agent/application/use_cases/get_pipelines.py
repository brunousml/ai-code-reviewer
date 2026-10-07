import logging
from typing import List, Optional

from src.code_review_agent.domain.ports.vcs_service import VCSService
from src.code_review_agent.domain.entities.pipeline import Pipeline

logger = logging.getLogger(__name__)

class GetPipelinesUseCase:
    """Use case for getting recent pipelines."""

    def __init__(self, vcs_service: VCSService):
        self.vcs_service = vcs_service

    def execute(self, project_id: str, days: Optional[int] = None) -> List[Pipeline]:
        """Executes the get recent pipelines process."""
        logger.info(f"Executing get recent pipelines for project '{project_id}'.")
        return self.vcs_service.get_pipelines(project_id, days)
