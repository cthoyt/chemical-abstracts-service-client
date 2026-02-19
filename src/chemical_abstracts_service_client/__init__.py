"""An API client to the Chemical Abstracts Service (CAS)."""

from .api import hello, square

# being explicit about exports is important!
__all__ = [
    "hello",
    "square",
]
