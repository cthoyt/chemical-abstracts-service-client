"""An API client to the Chemical Abstracts Service (CAS)."""

from .api import Chemical, ExperimentalProperty, PropertyCitations, get_chemical, is_valid, search

__all__ = [
    "Chemical",
    "ExperimentalProperty",
    "PropertyCitations",
    "get_chemical",
    "is_valid",
    "search",
]
