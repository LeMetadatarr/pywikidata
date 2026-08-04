"""pywikidata — Wikidata SPARQL entity sweeper, grouped on harvestkit.

Importing this package imports :mod:`pywikidata.harvest`, which in turn
imports the scraper module so it registers itself with
:mod:`harvestkit.engine` (``@register``).
"""
from pywikidata.version import __version__

import pywikidata.harvest  # noqa: F401  (import for @register side effects)

from pywikidata.client import WikidataClient
from pywikidata.models import WikidataSearchHit, WikidataExternalIds

__all__ = ["__version__", "WikidataClient", "WikidataSearchHit", "WikidataExternalIds"]
