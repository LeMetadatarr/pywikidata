# Datasets produced by pywikidata

This repo queries the Wikidata Query Service with about 90 typed SPARQL queries. It produces one JSONL dataset, `wikidata_entities`, where each row is a single Wikidata entity. Entity types include films, TV series, people, organizations, genres, musical instruments, games, podcasts, and Spotify-linked records.

## Dataset format

Rows are written as JSON objects, one per line. One row per Wikidata entity.

All rows share the following fields:

| Field | Type | Description |
| --- | --- | --- |
| `wikidata_id` | string | Wikidata Q identifier, for example `Q83495`. |
| `label_en` | string / null | English label. |
| `description_en` | string / null | English description. |
| `entity_type` | string | Query-specific type, for example `film` or `music_genre`. |

Type-specific fields are populated only when the source query returns them. Examples include:

| Field | Present for | Description |
| --- | --- | --- |
| `year` | films, albums, games, print works | Release or publication year. |
| `start_year` / `end_year` | TV series, audio works, organizations | Start and end years. |
| `country` / `country_qid` | works, people, organizations | Country name and QID. |
| `language` | works | Language name. |
| `genre` / `genre_qid` | works, people, organizations | Genre name and QID. |
| `director` / `director_qid` | films | Director name and QID. |
| `imdb_id` | films, TV series | IMDb identifier. |
| `tmdb_id` | films | TMDB movie identifier. |
| `thetvdb_id` | TV series | TheTVDB identifier. |
| `mb_artist_id` / `mb_release_group_id` | music entities | MusicBrainz identifiers. |
| `spotify_artist_id` / `spotify_album_id` / `spotify_track_id` / `spotify_show_id` | Spotify queries | Spotify identifiers. |
| `birth_year` / `death_year` / `gender` / `nationality` | people | Biographical fields. |
| `inception_year` / `dissolved_year` / `website` | organizations | Organizational fields. |
| `parent_genre` / `parent_genre_qid` | genre taxonomies | Parent genre name and QID. |

A full query list is available through the CLI with `--list-queries`.

## How to generate

Install the package with the optional HuggingFace publisher support:

```bash
pip install "pywikidata[hf]"
```

Run the full harvester:

```bash
pywikidata-harvest wikidata_entities --output ~/.cache/metadatarr/scrapers/
```

Run a single query:

```bash
pywikidata-harvest wikidata_entities --query films --output ~/.cache/metadatarr/scrapers/
```

The harvest is resumable per query. Stopping and rerunning the command continues from the last checkpoint kept in the output directory.

You can also run the source directly in Python:

```python
from pywikidata.harvest.wikidata_sparql import WikidataEntitiesSource

src = WikidataEntitiesSource()
rows, cursor = src.fetch({"qidx": 0, "offset": 0})
```

## Worth publishing on Hugging Face?

Yes. Wikidata content is in the public domain under CC0. The dataset gives a broad, cross-domain knowledge graph with stable identifiers and links to external catalogs such as IMDb, TMDB, MusicBrainz, and Spotify. This is useful for knowledge-base construction and entity-linking research.

## ML tasks served

- Knowledge graph completion and link prediction.
- Cross-catalog entity linking through shared external IDs.
- Multi-label classification across entity types and genres.
- Question answering and retrieval over structured entities.
- Dataset construction for named entity recognition and disambiguation.
