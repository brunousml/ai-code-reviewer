import gitlab
import os
import logging
import time
import random
from urllib.parse import unquote
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from src.code_review_agent.domain.ports.vcs_service import VCSService
from src.code_review_agent.domain.entities.pipeline import Pipeline
from src.code_review_agent.domain.entities.job import Job

logger = logging.getLogger(__name__)

class GitLabService(VCSService):
    """Concrete implementation of VCSService for GitLab."""

    def __init__(self):
        logger.info("Initializing GitLabService.")
        gitlab_url = os.getenv("GITLAB_URL")
        private_token = os.getenv("GITLAB_PRIVATE_TOKEN")

        if not gitlab_url or not private_token:
            logger.error("GITLAB_URL or GITLAB_PRIVATE_TOKEN environment variables not set.")
            raise ValueError("GITLAB_URL and GITLAB_PRIVATE_TOKEN must be set.")

        self.gl = gitlab.Gitlab(gitlab_url, private_token=private_token)
        try:
            self.gl.auth()
            logger.info("GitLab authentication successful.")
        except gitlab.exceptions.GitlabAuthenticationError:
            logger.error("GitLab authentication failed.", exc_info=True)
            raise
        
        # Configuração de retry via ambiente (com defaults)
        self.DEFAULT_RETRY_CONFIG = {
            'max_retries': int(os.getenv("GITLAB_RETRY_MAX_ATTEMPTS", "5")),
            'base_delay': float(os.getenv("GITLAB_RETRY_BASE_DELAY", "1.0")),
            'max_delay': float(os.getenv("GITLAB_RETRY_MAX_DELAY", "60.0")),
            'exponential_base': 2.0,
            'jitter': True
        }
        self.THROTTLE_DELAY = float(os.getenv("GITLAB_THROTTLE_DELAY", "0.5"))

    def get_merge_request_changes(self, project_path: str, merge_request_iid: int) -> Dict[str, Any]:
        logger.info(f"Fetching changes for MR !{merge_request_iid} in project '{project_path}'.")
        try:
            project = self.gl.projects.get(unquote(project_path))
            mr = project.mergerequests.get(merge_request_iid)
            return mr.changes()
        except gitlab.exceptions.GitlabError as e:
            logger.error(f"Failed to get merge request changes for project {project_path}, MR {merge_request_iid}.", exc_info=True)
            raise

    def post_comment_on_merge_request(self, project_path: str, merge_request_iid: int, note: str) -> None:
        logger.info(f"Posting comment to MR !{merge_request_iid} in project '{project_path}'.")
        try:
            project = self.gl.projects.get(unquote(project_path))
            mr = project.mergerequests.get(merge_request_iid)
            mr.notes.create({"body": note})
        except gitlab.exceptions.GitlabError as e:
            logger.error(f"Failed to post comment on merge request for project {project_path}, MR {merge_request_iid}.", exc_info=True)
            raise

    def _is_rate_limit_error(self, error: Exception) -> bool:
        """Verifica se o erro é relacionado a rate limiting."""
        error_str = str(error).lower()
        rate_limit_indicators = ['rate limit', 'too many requests', '429', 'throttl']
        return any(indicator in error_str for indicator in rate_limit_indicators)

    def _extract_retry_after(self, error: Exception) -> Optional[float]:
        """Extrai o tempo de retry sugerido pelo servidor, se disponível."""
        # GitLab pode retornar header Retry-After
        if hasattr(error, 'response_headers'):
            retry_after = error.response_headers.get('Retry-After')
            if retry_after:
                try:
                    return float(retry_after)
                except ValueError:
                    pass
        return None

    def _calculate_backoff_delay(self, attempt: int, retry_after: Optional[float] = None) -> float:
        """Calcula o delay para a próxima tentativa usando Exponential Backoff."""
        config = self.DEFAULT_RETRY_CONFIG
        
        # Se o servidor informou quanto tempo esperar, respeitar
        if retry_after is not None:
            return retry_after
        
        # Exponential backoff: base_delay * (2 ^ attempt)
        exponential_delay = config['base_delay'] * (config['exponential_base'] ** attempt)
        
        # Limitar ao max_delay
        delay = min(exponential_delay, config['max_delay'])
        
        # Adicionar jitter (variação aleatória de 0-25%) para evitar thundering herd
        if config['jitter']:
            jitter_range = delay * 0.25
            delay += random.uniform(0, jitter_range)
        
        return delay

    def post_comments_on_merge_request(
        self, 
        project_path: str, 
        merge_request_iid: int, 
        comments: List[str]
    ) -> None:
        """
        Posts multiple comments on a given merge request with retry and throttling.
        
        Implements:
        - Exponential Backoff: Aumenta o delay exponencialmente entre retries
        - Jitter: Adiciona variação aleatória para evitar thundering herd
        - Throttling: Delay fixo entre chamadas bem-sucedidas
        - Rate Limit Detection: Detecta erros 429 e respeita Retry-After header
        
        Args:
            project_path: Caminho do projeto no GitLab
            merge_request_iid: IID do Merge Request
            comments: Lista de comentários a serem postados
        """
        logger.info(
            f"Posting {len(comments)} comments to MR !{merge_request_iid} "
            f"in project '{project_path}' with retry support."
        )
        
        try:
            project = self.gl.projects.get(unquote(project_path))
            mr = project.mergerequests.get(merge_request_iid)
        except gitlab.exceptions.GitlabError as e:
            logger.error(f"Failed to get MR {merge_request_iid}", exc_info=True)
            raise
        
        posted_count = 0
        failed_comments = []
        config = self.DEFAULT_RETRY_CONFIG
        
        for i, comment in enumerate(comments, 1):
            attempt = 0
            success = False
            
            while attempt <= config['max_retries'] and not success:
                try:
                    logger.debug(f"Posting comment {i}/{len(comments)} (attempt {attempt + 1})")
                    mr.notes.create({"body": comment})
                    posted_count += 1
                    success = True
                    
                    # Throttling: aguardar entre chamadas bem-sucedidas (exceto na última)
                    if i < len(comments):
                        logger.debug(f"Throttling: waiting {self.THROTTLE_DELAY}s")
                        time.sleep(self.THROTTLE_DELAY)
                        
                except gitlab.exceptions.GitlabError as e:
                    attempt += 1
                    
                    # Verificar se é rate limit
                    is_rate_limit = self._is_rate_limit_error(e)
                    retry_after = self._extract_retry_after(e) if is_rate_limit else None
                    
                    if attempt > config['max_retries']:
                        logger.error(
                            f"Failed to post comment {i}/{len(comments)} after "
                            f"{config['max_retries']} retries: {e}"
                        )
                        failed_comments.append((i, comment[:100], str(e)))
                        break
                    
                    # Calcular delay com exponential backoff
                    delay = self._calculate_backoff_delay(attempt - 1, retry_after)
                    
                    if retry_after:
                        logger.warning(f"Rate limited. Server requested wait of {delay}s")
                    else:
                        logger.warning(
                            f"Attempt {attempt}/{config['max_retries'] + 1} "
                            f"failed for comment {i}. Retrying in {delay:.2f}s. Error: {e}"
                        )
                    
                    time.sleep(delay)
        
        # Log resultado final
        if failed_comments:
            logger.error(
                f"Completed with errors: {posted_count}/{len(comments)} comments posted. "
                f"Failed comments: {[f[0] for f in failed_comments]}"
            )
            raise gitlab.exceptions.GitlabError(
                f"Failed to post {len(failed_comments)} comments after retries"
            )
        else:
            logger.info(f"Successfully posted all {posted_count} comments to MR !{merge_request_iid}")

    def get_merge_request_comments(self, project_path: str, merge_request_iid: int) -> List[str]:
        """Fetches all comments (notes) for a given merge request."""
        logger.info(f"Fetching comments for MR !{merge_request_iid} in project '{project_path}'.")
        try:
            project = self.gl.projects.get(unquote(project_path))
            mr = project.mergerequests.get(merge_request_iid)
            notes = mr.notes.list(all=True)
            return [note.body for note in notes]
        except gitlab.exceptions.GitlabError as e:
            logger.error(f"Failed to get comments for MR {merge_request_iid} in project {project_path}.", exc_info=True)
            raise

    def get_merge_request_labels(self, project_path: str, merge_request_iid: int) -> List[str]:
        """Fetches the labels for a given merge request."""
        logger.info(f"Fetching labels for MR !{merge_request_iid} in project '{project_path}'.")
        try:
            project = self.gl.projects.get(unquote(project_path))
            mr = project.mergerequests.get(merge_request_iid)
            return mr.labels
        except gitlab.exceptions.GitlabError as e:
            logger.error(f"Failed to get labels for MR {merge_request_iid} in project {project_path}.", exc_info=True)
            raise

    def remove_merge_request_label(self, project_path: str, merge_request_iid: int, label: str) -> None:
        """Removes a specific label from a merge request."""
        logger.info(f"Removing label '{label}' from MR !{merge_request_iid} in project '{project_path}'.")
        try:
            project = self.gl.projects.get(unquote(project_path))
            mr = project.mergerequests.get(merge_request_iid)
            if label in mr.labels:
                mr.labels.remove(label)
                mr.save()
                logger.info(f"Label '{label}' removed successfully.")
            else:
                logger.info(f"Label '{label}' not found in MR labels.")
        except gitlab.exceptions.GitlabError as e:
            logger.error(f"Failed to remove label '{label}' from MR {merge_request_iid}.", exc_info=True)
            # We log but might not want to raise, as it's a cleanup step? 
            # Reviewing requirements: "Label removida automaticamente". Ideally should succeed.
            raise

    def get_pipelines(self, project_path: str, days: Optional[int] = None) -> List[Pipeline]:
        logger.info(f"Fetching recent pipelines for project '{project_path}'.")
        try:
            project = self.gl.projects.get(unquote(project_path))
            params = {'all': True, 'per_page': 100, 'order_by': 'updated_at', 'sort': 'desc'}
            if days is not None:
                updated_after = datetime.utcnow() - timedelta(days=days)
                params['updated_after'] = updated_after.isoformat()

            pipelines = project.pipelines.list(**params)
            return [Pipeline(id=p.id, status=p.status, source=p.source, ref=p.ref, created_at=p.created_at, web_url=p.web_url) for p in pipelines]
        except gitlab.exceptions.GitlabError as e:
            logger.error(f"Failed to get pipelines for project {project_path}.", exc_info=True)
            raise

    def list_pipelines_in_range(self, project_path: str, start_date: str, end_date: str) -> List[Pipeline]:
        logger.info(f"Fetching pipelines for project '{project_path}' from {start_date} to {end_date}.")
        try:
            project = self.gl.projects.get(unquote(project_path))
            pipelines = project.pipelines.list(
                all=True,
                updated_after=start_date + "T00:00:00Z",
                updated_before=end_date + "T23:59:59Z",
                order_by="updated_at",
                sort="asc"
            )
            return [Pipeline(id=p.id, status=p.status, source=p.source, ref=p.ref, created_at=p.created_at, web_url=p.web_url) for p in pipelines]
        except gitlab.exceptions.GitlabError as e:
            logger.error(f"Failed to get pipelines for project {project_path}.", exc_info=True)
            raise

    def list_pipeline_jobs(self, project_path: str, pipeline_id: int) -> List[Job]:
        logger.info(f"Fetching jobs for pipeline '{pipeline_id}' in project '{project_path}'.")
        try:
            project = self.gl.projects.get(unquote(project_path))
            pipeline = project.pipelines.get(pipeline_id)
            jobs = pipeline.jobs.list(all=True)
            return [Job(id=j.id, name=j.name, status=j.status) for j in jobs]
        except gitlab.exceptions.GitlabError as e:
            logger.error(f"Failed to list jobs for pipeline {pipeline_id} in project {project_path}.", exc_info=True)
            raise

    def get_merged_mrs(self, project_path: str, merged_after: datetime, label: Optional[str] = None) -> List[Any]:
        logger.info(f"Fetching merged MRs for project '{project_path}' after {merged_after}.")
        try:
            project = self.gl.projects.get(unquote(project_path))
            params = {
                'state': 'merged',
                'merged_after': merged_after.isoformat(),
                'all': True,
                'order_by': 'updated_at',
                'sort': 'desc'
            }
            if label:
                params['labels'] = [label]
            
            mrs = project.mergerequests.list(**params)
            return mrs
        except gitlab.exceptions.GitlabError as e:
            logger.error(f"Failed to get merged MRs for project {project_path}.", exc_info=True)
            raise

    def get_project_labels(self, project_path: str) -> List[Any]:
        logger.info(f"Fetching labels for project '{project_path}'.")
        try:
            project = self.gl.projects.get(unquote(project_path))
            return project.labels.list(all=True)
        except gitlab.exceptions.GitlabError as e:
            logger.error(f"Failed to get labels for project {project_path}.", exc_info=True)
            raise
