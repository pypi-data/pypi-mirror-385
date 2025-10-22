import json
from argparse import Namespace
from typing import Optional
from urllib.parse import urlparse

import requests
from bibtexparser import bparser
from dateutil import parser
from django.conf import settings
from requests import Timeout

from NEMO_publications import app_settings

PUBLICATION_NOTIFICATION = "publications"


def get_publication_settings():
    pub_settings = app_settings.DEFAULT_PUBLICATION_SETTINGS
    pub_settings.update(settings.PUBLICATIONS_SETTINGS)
    return Namespace(**pub_settings)


def parse_bibtex(bibtex_string):
    bibtex_parsed = bparser.parse(bibtex_string)
    if len(bibtex_parsed.entries) != 1:
        raise Exception("multiple entries were found")
    else:
        return bibtex_parsed.entries[0]


# Fetch DOI metadata from https://doi.org
# key 'error' contains error message if an error was encountered
# key 'metadata' contains dict with metadata fields that were found
def fetch_publication_metadata_by_doi(doi):
    pub_settings = get_publication_settings()
    base_url = pub_settings.doi_search_url.format(doi)
    headers_options = pub_settings.headers
    result = {"metadata": {"doi": doi}}
    for headers in headers_options:
        result = {"metadata": {"doi": doi}}
        try:
            response = requests.get(base_url, headers=headers, timeout=pub_settings.timeout)
            if response.status_code == 200:
                bibtex_string = response.text.strip()
                try:
                    publication_parsed_metadata = parse_bibtex(bibtex_string)
                    result["metadata"] = {
                        "doi": publication_parsed_metadata.get("doi", doi),
                        "year": publication_parsed_metadata.get("year"),
                        "month": parse_month_from_metadata(publication_parsed_metadata.get("month")),
                        "journal": publication_parsed_metadata.get("journal"),
                        "title": publication_parsed_metadata["title"],
                        "bibtex": bibtex_string,
                        "json_metadata": fetch_json_metadata(doi),
                    }
                    return result
                except Exception as parse_error:
                    result["error"] = "Search returned invalid publication metadata, " + parse_error.__str__()
            elif response.status_code == 404:
                result["error"] = "Publication information was not found."
            else:
                result["error"] = "Search query has failed."
        except Timeout:
            result["error"] = (
                "The request timed out. Please try again or contact your administrator to increase the timeout"
            )
    return result


def fetch_json_metadata(doi):
    pub_settings = get_publication_settings()
    base_url = pub_settings.doi_search_url.format(doi)
    headers = {"Accept": "application/json"}
    try:
        response = requests.get(base_url, headers=headers, timeout=pub_settings.timeout)
        if response.status_code == 200:
            response_text = response.text.strip()
            parsed_json = json.loads(response_text)
            return json.dumps(parsed_json, indent=2)
        return None
    except Exception:
        return None


def parse_month_from_metadata(month_str) -> Optional[int]:
    if month_str:
        try:
            parsed_date = parser.parse(month_str)
            month_number = parsed_date.month
            return month_number
        except ValueError:
            pass
    return None


def sanitize_doi(doi: str):
    return urlparse(doi).path.lstrip("/")
