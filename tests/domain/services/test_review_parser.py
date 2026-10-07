from src.code_review_agent.domain.services.review_parser import ReviewParser


class TestReviewParser:
    """Testes para o ReviewParser."""

    def test_parse_single_comment(self):
        """Review sem separador deve retornar 1 comentário."""
        review = "Este é um comentário único"
        result = ReviewParser.parse(review)
        assert len(result) == 1
        assert result[0].content == "Este é um comentário único"
        assert result[0].order == 0

    def test_parse_multiple_comments(self):
        """Review com separadores deve retornar múltiplos comentários."""
        review = """Primeiro comentário
---
Segundo comentário
---
Terceiro comentário"""
        result = ReviewParser.parse(review)
        assert len(result) == 3
        assert result[0].content == "Primeiro comentário"
        assert result[1].content == "Segundo comentário"
        assert result[2].content == "Terceiro comentário"
        assert result[0].order == 0
        assert result[1].order == 1
        assert result[2].order == 2

    def test_parse_ignores_empty_sections(self):
        """Seções vazias devem ser ignoradas."""
        review = """Primeiro comentário
---
---
Segundo comentário"""
        result = ReviewParser.parse(review)
        assert len(result) == 2
        assert result[0].content == "Primeiro comentário"
        assert result[1].content == "Segundo comentário"

    def test_parse_with_custom_separator(self):
        """Deve funcionar com separador customizado."""
        review = "A|||B|||C"
        result = ReviewParser.parse(review, separator="|||")
        assert len(result) == 3
        assert result[0].content == "A"
        assert result[1].content == "B"
        assert result[2].content == "C"

    def test_parse_preserves_order(self):
        """A ordem dos comentários deve ser preservada."""
        review = "A\n---\nB\n---\nC"
        result = ReviewParser.parse(review)
        assert result[0].order == 0
        assert result[1].order == 1
        assert result[2].order == 2

    def test_parse_strips_whitespace(self):
        """Espaços em branco devem ser removidos das bordas."""
        review = """   Comentário com espaços   
---
   Outro comentário   """
        result = ReviewParser.parse(review)
        assert result[0].content == "Comentário com espaços"
        assert result[1].content == "Outro comentário"

    def test_parse_empty_review(self):
        """Review vazio deve retornar lista vazia."""
        result = ReviewParser.parse("")
        assert len(result) == 0

    def test_parse_only_separators(self):
        """Review com apenas separadores deve retornar lista vazia."""
        result = ReviewParser.parse("---\n---\n---")
        assert len(result) == 0

    def test_parse_only_whitespace(self):
        """Review com apenas espaços em branco deve retornar lista vazia."""
        result = ReviewParser.parse("   \n   \n   ")
        assert len(result) == 0

    def test_parse_comments_with_newlines(self):
        """Comentários com múltiplas linhas devem ser preservados."""
        review = """Primeiro comentário
com múltiplas linhas
---
Segundo comentário
também com linhas"""
        result = ReviewParser.parse(review)
        assert len(result) == 2
        assert "múltiplas linhas" in result[0].content
        assert "também com linhas" in result[1].content
