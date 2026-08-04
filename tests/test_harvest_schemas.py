"""Row-schema equivalence tests for the Wikidata SPARQL scraper.

Relocated verbatim (assertions untouched) from metadatarr's
test_scrapers_batch3.py, keeping only the tests for the scraper that lives in
this package, re-pointed at pywikidata.harvest.*. These lock the exact
flat-row shape the scraper emits (the contract the LeData datasets depend on)
against a realistic upstream sample, so a future engine change can't
silently alter the output schema.
"""
from __future__ import annotations

import argparse

from harvestkit.engine import all_sources

from pywikidata.harvest.wikidata_sparql import (
    WikidataEntitiesSource,
    QUERIES,
    QUERY_INDEX,
)


def test_wikidata_parse_film_binding():
    src = WikidataEntitiesSource()
    spec = QUERY_INDEX["films"]
    b = {
        "item": {"value": "http://www.wikidata.org/entity/Q83495"},
        "itemLabel": {"value": "The Matrix"},
        "itemDescription": {"value": "1999 film"},
        "year": {"value": "1999"},
        "countryLabel": {"value": "United States"},
        "imdb": {"value": "tt0133093"},
    }
    row = spec.parse_binding(b)
    assert row["wikidata_id"] == "Q83495"
    assert row["label_en"] == "The Matrix"
    assert row["year"] == 1999
    assert row["imdb_id"] == "tt0133093"
    assert row["entity_type"] == "film"


def test_wikidata_query_registry_has_expected_names():
    names = {q.name for q in QUERIES}
    for expected in ("films", "singers", "music_genres", "spotify_artists",
                     "video_game_series", "board_games"):
        assert expected in names
    assert len(QUERIES) == len(QUERY_INDEX)


def test_wikidata_fetch_short_page_ends_query_moves_to_next():
    src = WikidataEntitiesSource()
    src.queries = QUERIES[:2]
    src._sparql = lambda q: [{"item": {"value": "http://www.wikidata.org/entity/Q1"}}]
    rows, cursor = src.fetch({"qidx": 0, "offset": 0})
    assert len(rows) == 1
    assert cursor == {"qidx": 1, "offset": 0}


def test_wikidata_fetch_empty_page_ends_query():
    src = WikidataEntitiesSource()
    src.queries = QUERIES[:1]
    src._sparql = lambda q: []
    rows, cursor = src.fetch({"qidx": 0, "offset": 0})
    assert rows == []
    assert cursor is None


def test_wikidata_configure_restricts_to_single_query():
    src = WikidataEntitiesSource()
    src.configure(argparse.Namespace(query="films", list_queries=False))
    assert len(src.queries) == 1
    assert src.queries[0].name == "films"


def test_wikidata_registered():
    assert all_sources().get("wikidata_entities") is WikidataEntitiesSource
