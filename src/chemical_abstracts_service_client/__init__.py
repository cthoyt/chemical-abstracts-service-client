"""An API client to the Chemical Abstracts Service (CAS)."""

from .api import Chemical, ExperimentalProperty, PropertyCitations, get_cas, is_valid, search_cas

__all__ = [
    "Chemical",
    "ExperimentalProperty",
    "PropertyCitations",
    "get_cas",
    "is_valid",
    "search_cas",
]
