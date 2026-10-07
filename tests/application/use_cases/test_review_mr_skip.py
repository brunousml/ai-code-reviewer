from unittest.mock import Mock, MagicMock
from src.ai_code_reviewer.application.use_cases.review_mr import ReviewMRUseCase

def test_review_mr_skips_when_already_reviewed():
    # Setup
    mock_vcs_service = Mock()
    mock_storage_service = Mock()
    mock_cache_service = Mock()
    mock_llm_service = Mock()
    
    # Configure mock to return a comment with the flag
    mock_vcs_service.get_merge_request_comments.return_value = [
        "Some user comment",
        "<!-- agent-review-bot -->\n\nExisting review..."
    ]
    
    use_case = ReviewMRUseCase(
        vcs_service=mock_vcs_service,
        storage_service=mock_storage_service,
        cache_service=mock_cache_service,
        base_prompt="prompt"
    )
    
    # Execute
    result = use_case.execute("group/project", 1, mock_llm_service)
    
    # Verify
    assert result["skipped"] is True
    mock_vcs_service.get_merge_request_changes.assert_not_called()
    mock_llm_service.analyze_code_changes.assert_not_called()

def test_review_mr_proceeds_when_not_reviewed():
    # Setup
    mock_vcs_service = Mock()
    mock_storage_service = Mock()
    mock_cache_service = Mock()
    mock_llm_service = Mock()
    
    # Configure mock to return comments WITHOUT the flag
    mock_vcs_service.get_merge_request_comments.return_value = [
        "Some user comment"
    ]
    mock_vcs_service.get_merge_request_changes.return_value = {"changes": []}
    mock_llm_service.analyze_code_changes.return_value = "Review content"
    mock_cache_service.get.return_value = None
    
    # Mock _load_prompt_context to unnecessary file operations
    use_case = ReviewMRUseCase(
        vcs_service=mock_vcs_service,
        storage_service=mock_storage_service,
        cache_service=mock_cache_service,
        base_prompt="prompt"
    )
    # Patch _load_prompt_context to return empty string
    use_case._load_prompt_context = Mock(return_value="")

    # Execute
    result = use_case.execute("group/project", 1, mock_llm_service)
    
    # Verify
    # We might not get "skipped" key or it might be False depending on implementation, 
    # but the key check is avoiding the skip logic.
    # The important part is that it proceeded to call get_changes and analyze.
    mock_vcs_service.get_merge_request_changes.assert_called_once()
    mock_llm_service.analyze_code_changes.assert_called_once()
