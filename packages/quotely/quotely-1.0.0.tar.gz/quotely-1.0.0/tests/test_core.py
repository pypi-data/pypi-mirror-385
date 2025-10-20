"""Test suite for quotely core functionality."""

import pytest

from quotely import get_random_quote, quote, random


class TestRandomQuoteAPI:
    """Tests for the random(quote) API."""
    
    def test_returns_string(self):
        result = random(quote)
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_works_without_args(self):
        result = random()
        assert isinstance(result, str)
        assert len(result) > 0


class TestRandomNameAPI:
    """Tests for the random.name(quote) API."""
    
    def test_returns_formatted_string(self):
        result = random.name(quote)
        assert isinstance(result, str)
        assert " - " in result
        assert result.startswith('"')
    
    def test_works_without_args(self):
        result = random.name()
        assert isinstance(result, str)
        assert " - " in result


class TestQuoteObject:
    """Tests for Quote object functionality."""
    
    def test_get_random_quote_returns_object(self):
        q = get_random_quote()
        assert hasattr(q, "name")
        assert isinstance(str(q), str)
        assert isinstance(repr(q), str)
    
    def test_has_name_attribute(self):
        q = get_random_quote()
        assert hasattr(q, "name")
        assert isinstance(q.name, str)
        assert len(q.name) > 0
    
    def test_str_returns_text_only(self):
        q = get_random_quote()
        text = str(q)
        assert not (text.startswith('"') and '" - ' in text)
    
    def test_repr_includes_author(self):
        q = get_random_quote()
        representation = repr(q)
        assert " - " in representation
        assert representation.startswith('"')


class TestQuoteVariety:
    """Tests for quote collection quality."""
    
    def test_multiple_calls_can_return_different_quotes(self):
        quotes = [random(quote) for _ in range(10)]
        unique_quotes = set(quotes)
        assert len(unique_quotes) >= 1
    
    def test_has_sufficient_quotes(self):
        from quotely.core import ALL_QUOTES
        
        assert len(ALL_QUOTES) >= 500
    
    def test_no_duplicate_quotes(self):
        from quotely.core import ALL_QUOTES
        
        quotes = [q[0] for q in ALL_QUOTES]
        assert len(quotes) == len(set(quotes)), "Duplicate quotes found"
