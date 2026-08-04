# pywikidata

Wikidata SPARQL entity sweeper — ~90 typed queries covering people, creative
works, taxonomies, organizations, and Spotify IDs across film, TV, music,
anime/manga, games, podcasts, and more — grouped onto the
[harvestkit](https://github.com/LeMetadatarr/harvestkit) resumable-harvest
engine. Extracted from [metadatarr](https://github.com/TigreGotico/metadatarr)'s
scraper collection into its own standalone package.

NOTE: a real-time query client for this source will be extracted from metadatarr's
resolver into this package as a follow-up (the "full extraction" step); this package
currently ships the bulk harvester only.

## Sources

| Scraper | Registry name | Source |
| --- | --- | --- |
| `wikidata_sparql` | `wikidata_entities` | Wikidata Query Service (WDQS), ~90 typed SPARQL queries |

Each query is independently resumable; use `--query NAME` to run a single one
or `--list-queries` to see all registered query names.

## Install

```bash
pip install pywikidata
# or, for the HuggingFace publisher (via harvestkit):
pip install "pywikidata[hf]"
# or, for Cloudflare-guarded sources:
pip install "pywikidata[stealth]"
```

## Usage

```bash
# list every registered scraper
pywikidata-harvest --list

# harvest the source (resumable — safe to Ctrl-C and rerun)
pywikidata-harvest wikidata_entities --output ~/.cache/metadatarr/scrapers/

# run just one query
pywikidata-harvest wikidata_entities --query films
```

Every scraper is a `harvestkit.engine.Source` subclass: checkpoint/dedup/
pagination/throttle are handled by the shared engine, each module only
answers `initial_cursor()` and `fetch(cursor)`. See
[harvestkit](https://github.com/LeMetadatarr/harvestkit) for the full engine
API.

## License

Apache-2.0
