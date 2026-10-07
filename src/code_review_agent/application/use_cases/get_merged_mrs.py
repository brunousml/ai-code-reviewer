import logging
from datetime import datetime, timedelta
from typing import Optional
from src.code_review_agent.domain.ports.vcs_service import VCSService

logger = logging.getLogger(__name__)

class GetMergedMRsUseCase:
    def __init__(self, vcs_service: VCSService):
        self.vcs_service = vcs_service

    def execute(self, project_path: str, days: int, label: Optional[str] = None) -> list[dict]:
        logger.info(f"Executing GetMergedMRsUseCase for project: {project_path}, days: {days}, label: {label}")
        
        after_date = datetime.now() - timedelta(days=days)
        
        mrs = self.vcs_service.get_merged_mrs(
            project_path=project_path,
            merged_after=after_date,
            label=label
        )
        
        return [
            {
                "iid": mr.iid,
                "title": mr.title,
                "author": mr.author['name'],
                "merged_at": mr.merged_at,
                "url": mr.web_url
            }
            for mr in mrs
        ]
