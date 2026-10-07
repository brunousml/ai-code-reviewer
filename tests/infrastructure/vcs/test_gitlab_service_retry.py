import pytest
from unittest.mock import Mock, patch
import gitlab.exceptions
import os

from src.code_review_agent.infrastructure.vcs.gitlab_service import GitLabService


class TestGitLabServiceRetry:
    """Testes para retry e throttling no GitLabService."""

    @patch('code_review_agent.infrastructure.vcs.gitlab_service.Gitlab')
    @patch.dict(os.environ, {
        'GITLAB_URL': 'https://gitlab.com',
        'GITLAB_PRIVATE_TOKEN': 'test-token'
    })
    def test_post_comments_with_rate_limit_retry(self, mock_gitlab_class):
        """Testa retry quando há rate limit."""
        # Setup
        mock_mr = Mock()
        mock_project = Mock()
        mock_project.mergerequests.get.return_value = mock_mr

        mock_gl_instance = Mock()
        mock_gl_instance.projects.get.return_value = mock_project
        mock_gl_instance.auth.return_value = None
        mock_gitlab_class.return_value = mock_gl_instance

        # Simula rate limit nas primeiras 2 tentativas, sucesso na terceira
        mock_mr.notes.create.side_effect = [
            gitlab.exceptions.GitlabError("Rate limit exceeded"),
            gitlab.exceptions.GitlabError("Rate limit exceeded"),
            None  # Sucesso
        ]

        service = GitLabService()
        service.DEFAULT_RETRY_CONFIG = {
            'max_retries': 3,
            'base_delay': 0.1,
            'max_delay': 1.0,
            'exponential_base': 2.0,
            'jitter': False
        }
        service.THROTTLE_DELAY = 0.1

        comments = ["Comment 1", "Comment 2"]

        with patch('time.sleep'):  # Mock sleep para testes rápidos
            service.post_comments_on_merge_request("project/path", 123, comments)

        # Verifica que tentou 3 vezes para o primeiro comentário
        assert mock_mr.notes.create.call_count == 3

    @patch('code_review_agent.infrastructure.vcs.gitlab_service.Gitlab')
    @patch.dict(os.environ, {
        'GITLAB_URL': 'https://gitlab.com',
        'GITLAB_PRIVATE_TOKEN': 'test-token'
    })
    def test_post_comments_with_throttling(self, mock_gitlab_class):
        """Testa que throttling é aplicado entre comentários."""
        # Setup
        mock_mr = Mock()
        mock_project = Mock()
        mock_project.mergerequests.get.return_value = mock_mr
        mock_mr.notes.create.return_value = None

        mock_gl_instance = Mock()
        mock_gl_instance.projects.get.return_value = mock_project
        mock_gl_instance.auth.return_value = None
        mock_gitlab_class.return_value = mock_gl_instance

        service = GitLabService()
        service.THROTTLE_DELAY = 0.1

        comments = ["Comment 1", "Comment 2", "Comment 3"]

        with patch('time.sleep') as mock_sleep:
            service.post_comments_on_merge_request("project/path", 123, comments)

            # Deve ter chamado sleep pelo menos 2 vezes (entre os 3 comentários)
            assert mock_sleep.call_count >= 2

    @patch('code_review_agent.infrastructure.vcs.gitlab_service.Gitlab')
    @patch.dict(os.environ, {
        'GITLAB_URL': 'https://gitlab.com',
        'GITLAB_PRIVATE_TOKEN': 'test-token'
    })
    def test_is_rate_limit_error(self, mock_gitlab_class):
        """Testa detecção de erros de rate limit."""
        mock_gl_instance = Mock()
        mock_gl_instance.auth.return_value = None
        mock_gitlab_class.return_value = mock_gl_instance

        service = GitLabService()

        assert service._is_rate_limit_error(Exception("Rate limit exceeded")) == True
        assert service._is_rate_limit_error(Exception("429 Too Many Requests")) == True
        assert service._is_rate_limit_error(Exception("Throttling error")) == True
        assert service._is_rate_limit_error(Exception("Normal error")) == False

    @patch('code_review_agent.infrastructure.vcs.gitlab_service.Gitlab')
    @patch.dict(os.environ, {
        'GITLAB_URL': 'https://gitlab.com',
        'GITLAB_PRIVATE_TOKEN': 'test-token'
    })
    def test_calculate_backoff_delay(self, mock_gitlab_class):
        """Testa cálculo de delay com exponential backoff."""
        mock_gl_instance = Mock()
        mock_gl_instance.auth.return_value = None
        mock_gitlab_class.return_value = mock_gl_instance

        service = GitLabService()
        service.DEFAULT_RETRY_CONFIG = {
            'base_delay': 1.0,
            'max_delay': 60.0,
            'exponential_base': 2.0,
            'jitter': False
        }

        # Tentativa 0: 1.0 * 2^0 = 1.0
        delay = service._calculate_backoff_delay(0)
        assert delay == 1.0

        # Tentativa 1: 1.0 * 2^1 = 2.0
        delay = service._calculate_backoff_delay(1)
        assert delay == 2.0

        # Tentativa 2: 1.0 * 2^2 = 4.0
        delay = service._calculate_backoff_delay(2)
        assert delay == 4.0

        # Com retry_after, deve respeitar
        delay = service._calculate_backoff_delay(0, retry_after=30.0)
        assert delay == 30.0

    @patch('code_review_agent.infrastructure.vcs.gitlab_service.Gitlab')
    @patch.dict(os.environ, {
        'GITLAB_URL': 'https://gitlab.com',
        'GITLAB_PRIVATE_TOKEN': 'test-token'
    })
    def test_post_comments_max_retries_exceeded(self, mock_gitlab_class):
        """Testa que erro é lançado após max_retries."""
        # Setup
        mock_mr = Mock()
        mock_project = Mock()
        mock_project.mergerequests.get.return_value = mock_mr

        mock_gl_instance = Mock()
        mock_gl_instance.projects.get.return_value = mock_project
        mock_gl_instance.auth.return_value = None
        mock_gitlab_class.return_value = mock_gl_instance

        # Sempre falha
        mock_mr.notes.create.side_effect = gitlab.exceptions.GitlabError("Always fails")

        service = GitLabService()
        service.DEFAULT_RETRY_CONFIG = {
            'max_retries': 2,
            'base_delay': 0.1,
            'max_delay': 1.0,
            'exponential_base': 2.0,
            'jitter': False
        }
        service.THROTTLE_DELAY = 0.1

        comments = ["Comment 1"]

        with patch('time.sleep'):
            with pytest.raises(gitlab.exceptions.GitlabError):
                service.post_comments_on_merge_request("project/path", 123, comments)

        # Deve ter tentado max_retries + 1 vezes (1 inicial + 2 retries)
        assert mock_mr.notes.create.call_count == 3

    @patch('code_review_agent.infrastructure.vcs.gitlab_service.Gitlab')
    @patch.dict(os.environ, {
        'GITLAB_URL': 'https://gitlab.com',
        'GITLAB_PRIVATE_TOKEN': 'test-token'
    })
    def test_post_comments_success(self, mock_gitlab_class):
        """Testa postagem bem-sucedida de múltiplos comentários."""
        # Setup
        mock_mr = Mock()
        mock_project = Mock()
        mock_project.mergerequests.get.return_value = mock_mr
        mock_mr.notes.create.return_value = None

        mock_gl_instance = Mock()
        mock_gl_instance.projects.get.return_value = mock_project
        mock_gl_instance.auth.return_value = None
        mock_gitlab_class.return_value = mock_gl_instance

        service = GitLabService()
        service.THROTTLE_DELAY = 0.1

        comments = ["Comment 1", "Comment 2"]

        with patch('time.sleep'):
            service.post_comments_on_merge_request("project/path", 123, comments)

        # Deve ter chamado create 2 vezes (um para cada comentário)
        assert mock_mr.notes.create.call_count == 2
