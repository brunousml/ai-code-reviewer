from typing import List
from src.ai_code_reviewer.domain.entities.review_comment import ReviewComment


class ReviewParser:
    """Serviço para parsear o review em comentários individuais."""
    
    DEFAULT_SEPARATOR = "---"  # Separador padrão entre seções
    
    @classmethod
    def parse(cls, review_text: str, separator: str = None) -> List[ReviewComment]:
        """
        Divide o texto do review em múltiplos comentários baseados no separador.
        
        Args:
            review_text: O texto completo do review
            separator: O separador usado para dividir (default: "---")
        
        Returns:
            Lista de ReviewComment ordenados
        """
        separator = separator or cls.DEFAULT_SEPARATOR
        
        # Divide pelo separador e remove partes vazias
        parts = review_text.split(separator)
        comments = []
        
        for i, part in enumerate(parts):
            cleaned_part = part.strip()
            if cleaned_part:  # Ignora partes vazias
                comments.append(ReviewComment(content=cleaned_part, order=i))
        
        return comments
