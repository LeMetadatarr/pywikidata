"""Network-free smoke test for the real-time Wikidata query client.

The client's ``_get`` is monkeypatched to return captured sample
``wbsearchentities`` / ``wbgetentities`` responses, so parsing and
claims-to-external-ids mapping are exercised without ever touching the
network.
"""
from __future__ import annotations

from pywikidata import WikidataClient, WikidataSearchHit, WikidataExternalIds

_SAMPLE_SEARCH = {
    "search": [
        {"id": "Q189330", "label": "Inception", "description": "2010 film by Christopher Nolan"},
    ]
}

_SAMPLE_ENTITY = {
    "entities": {
        "Q189330": {
            "claims": {
                "P345": [{"mainsnak": {"datavalue": {"value": "tt1375666"}}}],   # IMDb
                "P4947": [{"mainsnak": {"datavalue": {"value": "27205"}}}],       # TMDB movie
            }
        }
    }
}


def _client_with_fake_get(payloads):
    """*payloads* is a callable(params) -> dict, so different actions can
    return different fixtures."""
    client = WikidataClient()
    client._get = payloads
    return client


def test_search_parses_hits():
    client = _client_with_fake_get(lambda **params: _SAMPLE_SEARCH)
    hits = client.search("Inception")
    assert len(hits) == 1
    assert isinstance(hits[0], WikidataSearchHit)
    assert hits[0].id == "Q189330"
    assert hits[0].label == "Inception"


def test_get_external_ids_maps_claims():
    client = _client_with_fake_get(lambda **params: _SAMPLE_ENTITY)
    external = client.get_external_ids("Q189330")
    assert isinstance(external, WikidataExternalIds)
    assert external.wikidata == "Q189330"
    assert external.imdb == "tt1375666"
    assert external.tmdb_movie == 27205


def test_lookup_chains_search_and_claims():
    def _fake_get(**params):
        if params.get("action") == "wbsearchentities":
            return _SAMPLE_SEARCH
        return _SAMPLE_ENTITY

    client = _client_with_fake_get(_fake_get)
    external = client.lookup("Inception")
    assert external is not None
    assert external.tmdb_movie == 27205
