from typing import List, Optional, Tuple

from .version import __version__
from .transport import make_session

# Canonical user-agent string for this client. Keeping this in one place
# means a version bump doesn't need to touch the client constructor.
_USER_AGENT = f"pywikidata/{__version__}"

from .models import WikidataSearchHit, WikidataExternalIds

# Wikidata property -> WikidataExternalIds field mapping. Same precedence
# metadatarr's resolver provider used, copied verbatim (order matters for
# reverse lookup — most discriminating IDs first).
PROP_MAP = {
    "P345": "imdb",                       # IMDb ID
    "P4947": "tmdb_movie",                # TMDB movie ID
    "P4983": "tmdb_tv",                   # TMDB TV series ID
    "P4835": "tvdb",                      # TVDB series ID
    "P436": "musicbrainz_release_group",  # MB release group ID
    "P434": "musicbrainz_artist",         # MB artist ID
    "P435": "musicbrainz_work",           # MB work ID
    "P648": "olid",                       # Open Library ID
    "P212": "isbn_13",
    "P957": "isbn_10",
    "P2969": "goodreads",
}


class WikidataClient:
    """Client for the Wikidata action API (free, no key required).

    Uses ``wbsearchentities`` to find candidate Q-ids by title, then
    ``wbgetentities`` to read cross-reference claims — the same two-step
    flow metadatarr's resolver provider used.
    """

    API = "https://www.wikidata.org/w/api.php"

    def __init__(self, user_agent: str = _USER_AGENT):
        self._session = make_session()
        self._session.headers["User-Agent"] = user_agent
        self._session.headers["Accept"] = "application/json"

    def _get(self, **params) -> Optional[dict]:
        try:
            r = self._session.get(self.API, params=params, timeout=20)
            r.raise_for_status()
            return r.json()
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(self, title: str, language: str = "en", limit: int = 5) -> List[WikidataSearchHit]:
        if not title:
            return []
        data = self._get(
            action="wbsearchentities",
            search=title,
            language=language,
            format="json",
            limit=limit,
        )
        if not data:
            return []
        hits = data.get("search") or []
        out = []
        for h in hits:
            try:
                out.append(WikidataSearchHit.model_validate(h))
            except Exception:
                continue
        return out

    # ------------------------------------------------------------------
    # Claims -> external ids
    # ------------------------------------------------------------------

    def get_external_ids(self, qid: str) -> Optional[WikidataExternalIds]:
        """Fetch *qid*'s entity, walk its cross-reference claims, return a
        :class:`WikidataExternalIds` carrying every mapped property that's set.

        Note: unlike metadatarr's provider, ISBN values are returned as-is
        (no ``normalize_isbn`` cross-fill) since that helper lives in
        metadatarr's sibling ``mediavocab`` package, which this standalone
        client does not depend on.
        """
        if not qid:
            return None
        entity = self._get(action="wbgetentities", ids=qid, props="claims|labels", format="json")
        if not entity:
            return None

        claims = (entity.get("entities", {}).get(qid, {}).get("claims") or {})
        external = WikidataExternalIds(wikidata=qid)
        for prop, field in PROP_MAP.items():
            stmts = claims.get(prop) or []
            if not stmts:
                continue
            try:
                value = stmts[0]["mainsnak"]["datavalue"]["value"]
            except (KeyError, TypeError, IndexError):
                continue
            if field in {"tmdb_movie", "tmdb_tv", "tvdb"}:
                try:
                    setattr(external, field, int(value))
                except (TypeError, ValueError):
                    pass
            else:
                setattr(external, field, str(value))
        return external

    # ------------------------------------------------------------------
    # Reverse lookup — find a Q-id from a known cross-ref ID
    # ------------------------------------------------------------------

    @staticmethod
    def _reverse_probe_value(external_ids: WikidataExternalIds) -> Optional[Tuple[str, str]]:
        """First (property, value) pair we can query Wikidata's
        haswbstatement for. Order matters: prefer the most discriminating
        IDs first (same precedence as ``PROP_MAP``)."""
        for prop, field in PROP_MAP.items():
            value = getattr(external_ids, field, None)
            if value not in (None, ""):
                return prop, str(value)
        return None

    def find_qid(self, external_ids: WikidataExternalIds) -> Optional[str]:
        """Find the Q-id matching any populated cross-ref field, searching
        ``haswbstatement`` in ``PROP_MAP`` precedence order."""
        probe = self._reverse_probe_value(external_ids)
        if probe is None:
            return None
        prop, value = probe
        data = self._get(
            action="query",
            list="search",
            srsearch=f"haswbstatement:{prop}={value}",
            format="json",
            srlimit=1,
        )
        if not data:
            return None
        hits = (data.get("query") or {}).get("search") or []
        if not hits:
            return None
        return hits[0].get("title")

    def enrich(self, external_ids: WikidataExternalIds) -> Optional[WikidataExternalIds]:
        """Find this entity's Q-id (if not already given) and return its
        full claims-derived :class:`WikidataExternalIds`."""
        if external_ids.wikidata:
            return self.get_external_ids(external_ids.wikidata)
        qid = self.find_qid(external_ids)
        if qid is None:
            return None
        return self.get_external_ids(qid)

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    def lookup(self, title: str, language: str = "en") -> Optional[WikidataExternalIds]:
        """Search by title and return the top hit's cross-reference IDs."""
        hits = self.search(title, language=language, limit=1)
        if not hits:
            return None
        return self.get_external_ids(hits[0].id)

    def lookup_candidates(self, title: str, language: str = "en") -> List[WikidataExternalIds]:
        """Fan out across the top-3 search hits.

        Each candidate costs one extra Wikidata entity-fetch, so cap small
        (same cap metadatarr's resolver provider used).
        """
        hits = self.search(title, language=language, limit=5)
        out: List[WikidataExternalIds] = []
        for hit in hits[:3]:
            external = self.get_external_ids(hit.id)
            if external is not None:
                out.append(external)
        return out
