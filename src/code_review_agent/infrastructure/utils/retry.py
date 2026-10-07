import time
import random
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class RetryConfig:
    """Configuração para estratégia de retry."""
    
    def __init__(
        self,
        max_retries: int = 5,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        """
        Args:
            max_retries: Número máximo de tentativas (default: 5)
            base_delay: Delay base em segundos (default: 1.0)
            max_delay: Delay máximo em segundos (default: 60.0)
            exponential_base: Base para cálculo exponencial (default: 2.0)
            jitter: Adicionar variação aleatória para evitar thundering herd (default: True)
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter


class RateLimitError(Exception):
    """Exceção para erros de rate limit."""
    
    def __init__(self, message: str, retry_after: Optional[float] = None):
        super().__init__(message)
        self.retry_after = retry_after  # Tempo sugerido pelo servidor para retry


def calculate_backoff_delay(
    attempt: int,
    config: RetryConfig,
    retry_after: Optional[float] = None
) -> float:
    """
    Calcula o delay para a próxima tentativa usando Exponential Backoff.
    
    Formula: min(max_delay, base_delay * (exponential_base ^ attempt)) + jitter
    
    Args:
        attempt: Número da tentativa atual (0-indexed)
        config: Configuração de retry
        retry_after: Tempo sugerido pelo servidor (tem prioridade se fornecido)
    
    Returns:
        Delay em segundos
    """
    # Se o servidor informou quanto tempo esperar, respeitar
    if retry_after is not None:
        return retry_after
    
    # Exponential backoff: base_delay * (2 ^ attempt)
    exponential_delay = config.base_delay * (config.exponential_base ** attempt)
    
    # Limitar ao max_delay
    delay = min(exponential_delay, config.max_delay)
    
    # Adicionar jitter (variação aleatória de 0-25%) para evitar thundering herd
    if config.jitter:
        jitter_range = delay * 0.25
        delay += random.uniform(0, jitter_range)
    
    return delay
