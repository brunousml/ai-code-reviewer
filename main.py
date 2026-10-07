from dotenv import load_dotenv

# Load environment variables before other imports
load_dotenv()

import os

from src.code_review_agent.config import configure_logging, GEMINI_PROMPT
from src.code_review_agent.infrastructure.vcs.gitlab_service import GitLabService
from src.code_review_agent.infrastructure.llm.gemini_service import GeminiService
from src.code_review_agent.infrastructure.llm.openai_service import OpenAIService
from src.code_review_agent.infrastructure.storage.local_storage_service import LocalStorageService
from src.code_review_agent.infrastructure.cache.file_cache_service import FileCacheService
from src.code_review_agent.application.use_cases.review_mr import ReviewMRUseCase
from src.code_review_agent.application.use_cases.get_pipelines import GetPipelinesUseCase
from src.code_review_agent.application.use_cases.get_dora_metrics import GetDoraMetricsUseCase
from src.code_review_agent.application.use_cases.get_merged_mrs import GetMergedMRsUseCase
from src.code_review_agent.application.use_cases.get_project_labels import GetProjectLabelsUseCase
from src.code_review_agent.presentation.cli import CLI

def main():
    """Composition Root: Initializes and wires up the application components."""
    # 1. Configure logging
    configure_logging()

    # 2. Initialize services (Infrastructure Layer)
    vcs_service = GitLabService()
    storage_service = LocalStorageService(reviews_dir="reviews")
    cache_service = FileCacheService()

    # Initialize LLM services
    gemini_service = GeminiService()
    openai_service = None
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        openai_service = OpenAIService(api_key=openai_api_key)

    # 3. Initialize use cases (Application Layer)
    review_mr_use_case = ReviewMRUseCase(
        vcs_service=vcs_service,
        storage_service=storage_service,
        cache_service=cache_service,
        base_prompt=GEMINI_PROMPT,
    )
    get_pipelines_use_case = GetPipelinesUseCase(vcs_service=vcs_service)
    get_dora_metrics_use_case = GetDoraMetricsUseCase(vcs_service=vcs_service)
    get_merged_mrs_use_case = GetMergedMRsUseCase(vcs_service=vcs_service)
    get_project_labels_use_case = GetProjectLabelsUseCase(vcs_service=vcs_service)

    # 4. Initialize and run the presentation layer
    cli = CLI(
        review_mr_use_case=review_mr_use_case,
        get_pipelines_use_case=get_pipelines_use_case,
        get_dora_metrics_use_case=get_dora_metrics_use_case,
        get_merged_mrs_use_case=get_merged_mrs_use_case,
        get_project_labels_use_case=get_project_labels_use_case,
        gemini_service=gemini_service,
        openai_service=openai_service
    )
    cli.run()

if __name__ == "__main__":
    main()
