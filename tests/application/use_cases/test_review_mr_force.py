from unittest.mock import Mock, patch
import os
import pytest
from src.code_review_agent.application.use_cases.review_mr import ReviewMRUseCase

@patch.dict(os.environ, {"AGENT_REVIEW_FORCE": "true"})
def test_review_mr_proceeds_when_env_var_force_is_true():
    # Setup
    mock_vcs_service = Mock()
    mock_storage_service = Mock()
    mock_cache_service = Mock()
    mock_llm_service = Mock()
    
    # Existing comments present
    mock_vcs_service.get_merge_request_comments.return_value = [
        "<!-- agent-review-bot -->\n\nExisting review..."
    ]
    mock_vcs_service.get_merge_request_labels.return_value = []
    mock_vcs_service.get_merge_request_changes.return_value = {"changes": []}
    mock_llm_service.analyze_code_changes.return_value = "Review content"
    
    use_case = ReviewMRUseCase(
        vcs_service=mock_vcs_service,
        storage_service=mock_storage_service,
        cache_service=mock_cache_service,
        base_prompt="prompt"
    )
    use_case._load_prompt_context = Mock(return_value="")

    # Execute
    result = use_case.execute("group/project", 1, mock_llm_service)
    
    # Verify
    mock_vcs_service.get_merge_request_changes.assert_called_once()
    assert result.get("skipped", False) is False

def test_review_mr_proceeds_when_label_present_and_removes_label():
    # Setup
    mock_vcs_service = Mock()
    mock_storage_service = Mock()
    mock_cache_service = Mock()
    mock_llm_service = Mock()
    
    # Existing comments present and FORCE LABEL present
    mock_vcs_service.get_merge_request_comments.return_value = [
        "<!-- agent-review-bot -->\n\nExisting review..."
    ]
    mock_vcs_service.get_merge_request_labels.return_value = ["agent-review-requested", "bug"]
    mock_vcs_service.get_merge_request_changes.return_value = {"changes": []}
    mock_llm_service.analyze_code_changes.return_value = "Review content"
    
    use_case = ReviewMRUseCase(
        vcs_service=mock_vcs_service,
        storage_service=mock_storage_service,
        cache_service=mock_cache_service,
        base_prompt="prompt"
    )
    use_case._load_prompt_context = Mock(return_value="")

    # Execute
    result = use_case.execute("group/project", 1, mock_llm_service)
    
    # Verify
    mock_vcs_service.get_merge_request_changes.assert_called_once()
    assert result.get("skipped", False) is False
    # Verify label removal
    mock_vcs_service.remove_merge_request_label.assert_called_once_with("group/project", 1, "agent-review-requested")

@patch.dict(os.environ, {"AGENT_REVIEW_FORCE": "false"})
def test_review_mr_skips_when_no_force_conditions():
    # Setup
    mock_vcs_service = Mock()
    mock_storage_service = Mock()
    mock_cache_service = Mock()
    mock_llm_service = Mock()
    
    # Existing comments present, NO force label, NO force env
    mock_vcs_service.get_merge_request_comments.return_value = [
        "<!-- agent-review-bot -->\n\nExisting review..."
    ]
    mock_vcs_service.get_merge_request_labels.return_value = ["bug"] # no agent-review-requested
    
    use_case = ReviewMRUseCase(
        vcs_service=mock_vcs_service,
        storage_service=mock_storage_service,
        cache_service=mock_cache_service,
        base_prompt="prompt"
    )
    
    # Execute
    result = use_case.execute("group/project", 1, mock_llm_service)
    
    # Verify
    assert result.get("skipped") is True
    mock_vcs_service.get_merge_request_changes.assert_not_called()
