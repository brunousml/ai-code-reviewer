from dataclasses import dataclass

@dataclass
class ReviewComment:
    """Representa um comentário individual do review."""
    content: str
    order: int  # ordem do comentário no review original
