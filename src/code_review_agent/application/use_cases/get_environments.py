import logging
from typing import List

from src.code_review_agent.domain.ports.vcs_service import VCSService
from src.code_review_agent.domain.entities.environment import Environment

logger = logging.getLogger(__name__)

class GetEnvironmentsUseCase:
    """Use case for getting environments."""

    def __init__(self, vcs_service: VCSService):
        self.vcs_service = vcs_service

    def execute(self, project_id: str) -> List[Environment]:
        """Executes the get environments process."""
        logger.info(f"Executing get environments for project '{project_id}'.")
        return self.vcs_service.get_environments(project_id)
