import logging
from src.code_review_agent.domain.ports.vcs_service import VCSService

logger = logging.getLogger(__name__)

class GetProjectLabelsUseCase:
    def __init__(self, vcs_service: VCSService):
        self.vcs_service = vcs_service

    def execute(self, project_path: str) -> list[str]:
        logger.info(f"Executing GetProjectLabelsUseCase for project: {project_path}")
        labels = self.vcs_service.get_project_labels(project_path=project_path)
        return [label.name for label in labels]
