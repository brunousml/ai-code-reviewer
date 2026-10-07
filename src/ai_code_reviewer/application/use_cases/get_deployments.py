import logging
from typing import List

from src.ai_code_reviewer.domain.ports.vcs_service import VCSService
from src.ai_code_reviewer.domain.entities.deployment import Deployment

logger = logging.getLogger(__name__)

class GetDeploymentsUseCase:
    """Use case for getting deployments."""

    def __init__(self, vcs_service: VCSService):
        self.vcs_service = vcs_service

    def execute(self, project_id: str, environment: str) -> List[Deployment]:
        """Executes the get deployments process."""
        logger.info(f"Executing get deployments for project '{project_id}' and environment '{environment}'.")
        return self.vcs_service.get_deployments(project_id, environment)
