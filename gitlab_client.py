from urllib.parse import unquote, urlparse
import gitlab
import os
import logging

logger = logging.getLogger(__name__)


def get_project_path_and_mr_iid_from_url(url):
    """
    Extracts project path and merge request IID from a GitLab MR URL.
    """
    logger.info(f"Attempting to parse GitLab URL: {url}")
    try:
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip('/').split('/')

        # Find the index of '-/merge_requests'
        mr_keyword_index = path_parts.index('merge_requests')
        
        project_path_parts = path_parts[:mr_keyword_index-1]
        project_path = "/".join(project_path_parts)

        mr_iid = path_parts[mr_keyword_index + 1]

        if not project_path or not mr_iid.isdigit():
            raise ValueError("Project path or MR IID is invalid.")

        logger.info(f"Successfully parsed URL. Project path: {project_path}, MR IID: {mr_iid}")
        return project_path, int(mr_iid)
    except (ValueError, IndexError):
        logger.error(f"Could not parse project path and MR IID from URL: {url}", exc_info=True)
        raise ValueError(f"Could not parse project path and MR IID from URL: {url}")


class GitLabClient:
    def __init__(self):
        logger.info("Initializing GitLabClient.")
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

    def get_merge_request_changes(self, project_id, merge_request_iid):
        logger.info(f"Fetching changes for MR !{merge_request_iid} in project '{project_id}'.")
        try:
            project = self.gl.projects.get(unquote(project_id))
            logger.debug(f"Successfully fetched project: {project.name_with_namespace}")
            mr = project.mergerequests.get(merge_request_iid)
            logger.debug(f"Successfully fetched MR: {mr.title}")
            changes = mr.changes()
            logger.info(f"Successfully fetched {len(changes.get('changes', []))} changes for MR !{merge_request_iid}.")
            logger.debug("Changes data: %s", changes)
            return changes
        except gitlab.exceptions.GitlabError as e:
            logger.error(f"Failed to get merge request changes for project {project_id}, MR {merge_request_iid}.", exc_info=True)
            raise

    def post_comment_on_merge_request(self, project_id, merge_request_iid, note):
        logger.info(f"Posting comment to MR !{merge_request_iid} in project '{project_id}'.")
        logger.debug(f"Project ID: {project_id}, MR IID: {merge_request_iid}")
        logger.debug(f"Note to be posted: {note[:100]}...") # Log first 100 chars
        try:
            project = self.gl.projects.get(project_id)
            mr = project.mergerequests.get(merge_request_iid)
            mr.notes.create({"body": note})
            logger.info(f"Successfully posted comment to MR !{merge_request_iid}.")
        except gitlab.exceptions.GitlabError:
            logger.error(f"Failed to post comment on merge request for project {project_id}, MR {merge_request_iid}.", exc_info=True)
            raise
