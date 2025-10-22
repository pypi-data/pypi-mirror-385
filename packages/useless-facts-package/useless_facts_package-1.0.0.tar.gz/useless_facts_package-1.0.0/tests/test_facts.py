"""
Tests for the useless_facts package
"""

import pytest
from useless_facts import get_random_fact, get_all_facts, get_fact_by_category, get_categories, get_fact_count


def test_get_random_fact():
    """Test that get_random_fact returns a string"""
    fact = get_random_fact()
    assert isinstance(fact, str)
    assert len(fact) > 0


def test_get_random_fact_with_category():
    """Test that get_random_fact with category returns a fact from that category"""
    fact = get_random_fact("animals")
    assert isinstance(fact, str)
    assert len(fact) > 0


def test_get_random_fact_invalid_category():
    """Test that get_random_fact raises ValueError for invalid category"""
    with pytest.raises(ValueError):
        get_random_fact("invalid_category")


def test_get_all_facts():
    """Test that get_all_facts returns a dictionary with all categories"""
    facts = get_all_facts()
    assert isinstance(facts, dict)
    assert "animals" in facts
    assert "science" in facts
    assert "history" in facts
    assert "food" in facts
    assert "random" in facts


def test_get_fact_by_category():
    """Test that get_fact_by_category returns a list of facts"""
    animal_facts = get_fact_by_category("animals")
    assert isinstance(animal_facts, list)
    assert len(animal_facts) > 0
    assert all(isinstance(fact, str) for fact in animal_facts)


def test_get_fact_by_category_invalid():
    """Test that get_fact_by_category raises ValueError for invalid category"""
    with pytest.raises(ValueError):
        get_fact_by_category("invalid_category")


def test_get_categories():
    """Test that get_categories returns a list of all categories"""
    categories = get_categories()
    assert isinstance(categories, list)
    assert "animals" in categories
    assert "science" in categories
    assert "history" in categories
    assert "food" in categories
    assert "random" in categories


def test_get_fact_count():
    """Test that get_fact_count returns a positive integer"""
    count = get_fact_count()
    assert isinstance(count, int)
    assert count > 0


def test_facts_are_unique():
    """Test that facts within each category are unique"""
    all_facts = get_all_facts()
    for category, facts in all_facts.items():
        assert len(facts) == len(set(facts)), f"Duplicate facts found in category: {category}"
