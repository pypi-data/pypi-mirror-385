"""
Useless Facts - A Python package that returns random useless facts
"""

from .facts import get_random_fact, get_all_facts, get_fact_by_category, get_categories, get_fact_count

__version__ = "1.0.0"
__author__ = "useless-facts"


__all__ = ["get_random_fact", "get_all_facts", "get_fact_by_category", "get_categories", "get_fact_count"]
