"""Pydantic models returned by :class:`pywikidata.client.WikidataClient`.

``WikidataExternalIds`` mirrors the subset of ``mediavocab.models.ExternalIds``
fields metadatarr's Wikidata resolver provider populates from claims — this
package has no dependency on metadatarr or mediavocab, so the field set is
copied rather than imported.
"""
from typing import Optional
from pydantic import BaseModel, ConfigDict


class WikidataSearchHit(BaseModel):
    """One row of a ``wbsearchentities`` result."""

    model_config = ConfigDict(extra="ignore")

    id: str
    label: Optional[str] = None
    description: Optional[str] = None


class WikidataExternalIds(BaseModel):
    """Cross-reference IDs read off a Wikidata entity's claims.

    Field names mirror metadatarr's ``ExternalIds`` model so downstream
    consumers can map 1:1, without this package importing that model.
    """

    model_config = ConfigDict(extra="ignore")

    wikidata: Optional[str] = None
    imdb: Optional[str] = None
    tmdb_movie: Optional[int] = None
    tmdb_tv: Optional[int] = None
    tvdb: Optional[int] = None
    musicbrainz_release_group: Optional[str] = None
    musicbrainz_artist: Optional[str] = None
    musicbrainz_work: Optional[str] = None
    olid: Optional[str] = None
    isbn_13: Optional[str] = None
    isbn_10: Optional[str] = None
    goodreads: Optional[str] = None
