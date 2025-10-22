from unittest import TestCase

from NEMO_publications.utils import sanitize_doi


class TestCleanDOI(TestCase):
    def test_clean_doi(self):
        test_cases = [
            ("https://doi.org/10.1000/j.journal.2023.01.001", "10.1000/j.journal.2023.01.001"),
            ("http://doi.org/10.1000/j.journal.2020.05.003", "10.1000/j.journal.2020.05.003"),
            ("https://dx.doi.org/10.1234/example.test.2021", "10.1234/example.test.2021"),
            ("http://dx.doi.org/10.5678/example.test.2022", "10.5678/example.test.2022"),
            ("10.9987/standalone.doi.example", "10.9987/standalone.doi.example"),
        ]

        for doi, expected in test_cases:
            with self.subTest(doi=doi):
                self.assertEqual(sanitize_doi(doi), expected)
