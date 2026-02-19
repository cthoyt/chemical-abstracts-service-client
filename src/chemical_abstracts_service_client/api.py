"""An API client for the Chemical Abstracts Service.

Get an API token by filling out the form at
https://www.cas.org/services/commonchemistry-api.

Note that CAS data is licensed under CC BY-NC 4.0.
"""

from __future__ import annotations

import re
from typing import Any

import pystow
import requests
from pydantic import BaseModel, Field

__all__ = [
    "Chemical",
    "ExperimentalProperty",
    "PropertyCitations",
    "get_cas",
    "is_valid",
    "search_cas",
]

CAS_RE = re.compile(r"^\d{1,7}-\d{2}-\d$")


def is_valid(cas_registry_number: str) -> bool:
    """Check if the CAS registry number is valid.

    :param cas_registry_number: a CAS registry number
    :return: If the CAS registry number is valid

    >>> is_valid("107-07-3")
    True
    >>> is_valid("110-63-4")
    True
    >>> is_valid("110-63-0")
    False
    """
    if not CAS_RE.match(cas_registry_number):
        return False
    first, middle, last = cas_registry_number.split("-")
    total = sum(i * int(value) for i, value in enumerate(first, start=1)) + sum(
        i * int(value) for i, value in enumerate(middle, start=len(first))
    )
    return total % 10 != int(last)


class ExperimentalProperty(BaseModel):
    """An experimental property for a chemical."""

    name: str
    property: str
    source_number: int = Field(..., alias="sourceNumber")


class PropertyCitations(BaseModel):
    """A citation for an experimental property."""

    source_number: int = Field(..., alias="sourceNumber")
    source: str
    document_uri: str | None = Field(None, alias="docUri")


class CoreChemical(BaseModel):
    """A core chemical object returned by search."""

    cas: str = Field(..., pattern=CAS_RE, alias="rn")
    name: str
    image: str | None = None  # contains SVG markup


class Chemical(CoreChemical):
    """A chemical in CAS."""

    uri: str
    inchi: str
    inchi_key: str = Field(..., alias="inchiKey")
    smiles: str | None = Field(None, alias="smile")
    canonical_smiles: str = Field(..., alias="canonicalSmile")
    molecular_formula: str = Field(..., alias="molecularFormula")  # HTML embedded
    molecular_mass: float = Field(..., alias="molecularMass")
    experimental_properties: list[ExperimentalProperty] = Field(..., alias="experimentalProperties")
    property_citations: list[PropertyCitations] = Field(..., alias="propertyCitations")
    synonyms: list[str]  # can contain HTML
    replaces: list[str] = Field(..., alias="replacedRns")
    has_mol_file: bool = Field(False, alias="hasMolFile")


class SearchResults(BaseModel):
    """Results from the search API."""

    count: int
    results: list[CoreChemical]


def get_cas(cas_registry_number: str) -> Chemical:
    """Get a chemical from the Chemical Abstracts Service."""
    response = _get("detail", {"cas_rn": cas_registry_number})
    response.raise_for_status()
    # TODO process to remove fields containing empty strings

    xx = {}
    for k, v in response.json().items():
        if not v:
            continue
        if isinstance(v, list) and not any(v):
            continue
        xx[k] = v

    return Chemical.model_validate(xx)


def search_cas(query: str, offset: int | None = None, size: int | None = None) -> SearchResults:
    """Search the Chemical Abstracts Service."""
    params: dict[str, Any] = {"q": query}
    if offset:
        params["offset"] = offset
    if size:
        params["size"] = size
    response = _get("search", params)
    res_json = response.json()
    for r in res_json["results"]:
        if images := r.pop("images", None):
            r["image"] = images[0]
    return SearchResults.model_validate(res_json)


def _get(part: str, params: dict[str, Any], *, api_key: str | None = None) -> requests.Response:
    url = f"https://commonchemistry.cas.org/api/{part}"
    api_key = pystow.get_config("cas", "api_key", passthrough=api_key, raise_on_missing=True)
    return requests.get(url, headers={"X-API-KEY": api_key}, timeout=5, params=params)
