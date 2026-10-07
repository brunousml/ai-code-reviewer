import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def get_project_path_and_mr_iid_from_url(url: str):
    """
    Extracts project path and merge request IID from a GitLab MR URL.
    """
    logger.info(f"Attempting to parse GitLab URL: {url}")
    try:
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip('/').split('/')

        # Find the index of '-/merge_requests' or 'merge_requests'
        try:
            mr_keyword_index = path_parts.index('merge_requests')
            project_path_parts = path_parts[:mr_keyword_index - 1] # Accomodate for /-/ part
        except ValueError:
            # Fallback for URLs without the /-/ part
            mr_keyword_index = path_parts.index('merge_requests')
            project_path_parts = path_parts[:mr_keyword_index]

        project_path = "/".join(project_path_parts)
        mr_iid = path_parts[mr_keyword_index + 1]

        if not project_path or not mr_iid.isdigit():
            raise ValueError("Project path or MR IID is invalid.")

        logger.info(f"Successfully parsed URL. Project path: {project_path}, MR IID: {mr_iid}")
        return project_path, int(mr_iid)
    except (ValueError, IndexError):
        logger.error(f"Could not parse project path and MR IID from URL: {url}", exc_info=True)
        raise ValueError(f"Could not parse project path and MR IID from URL: {url}")
