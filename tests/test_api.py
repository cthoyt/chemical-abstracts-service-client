"""Trivial version test."""

import unittest

import requests.exceptions

from chemical_abstracts_service_client import get_cas, search_cas
from chemical_abstracts_service_client.version import get_version


class TestGetter(unittest.TestCase):
    """Test the get_version function."""

    def test_missing(self) -> None:
        """Test getting an invalid CAS."""
        with self.assertRaises(requests.exceptions.HTTPError) as ctx:
            get_cas("1234")
            self.assertEqual(404, ctx.exception.response.status_code)

    def test_get(self) -> None:
        """Test getting a valid CAS."""
        chemical = get_cas("110-63-4")
        self.assertEqual("110-63-4", chemical.cas)
        self.assertEqual("1,4-Butanediol", chemical.name)
        self.assertEqual(90.12, chemical.molecular_mass)
        self.assertEqual("InChI=1S/C4H10O2/c5-3-1-2-4-6/h5-6H,1-4H2", chemical.inchi)
        self.assertEqual("InChIKey=WERYXYBDKMZEQL-UHFFFAOYSA-N", chemical.inchi_key)
        self.assertEqual("OCCCCO", chemical.canonical_smiles)
        self.assertIsNone(chemical.smiles)
        self.assertIn("Diol 14B", chemical.synonyms)
        self.assertEqual(
            {"732189-03-6", "1204746-06-4", "1400594-63-9"},
            set(chemical.replaces),
        )

    def test_search_single(self) -> None:
        """Test search."""
        search_results = search_cas("butane")
        self.assertEqual(1, search_results.count)
        self.assertEqual("106-97-8", search_results.results[0].cas)
        self.assertEqual("Butane", search_results.results[0].name)

    def test_search_wildcard(self) -> None:
        """Test search with a wildcard."""
        search_results = search_cas("sodium*")
        self.assertLessEqual(2_000, search_results.count)
        self.assertEqual(50, len(search_results.results))

        search_results = search_cas("sodium*", size=100)
        self.assertLessEqual(2_000, search_results.count)
        self.assertEqual(100, len(search_results.results))


class TestVersion(unittest.TestCase):
    """Trivially test a version."""

    def test_version_type(self) -> None:
        """Test the version is a string.

        This is only meant to be an example test.
        """
        version = get_version()
        self.assertIsInstance(version, str)
