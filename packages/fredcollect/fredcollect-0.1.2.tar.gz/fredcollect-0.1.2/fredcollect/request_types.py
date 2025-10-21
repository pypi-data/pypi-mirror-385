"""
FRED API endpoint mappings to their respective data cleaning functions.
"""

from .clean.categories import *
from .clean.releases import *
from .clean.releases import _releases
from .clean.series import *
from .clean.series import _series
from .clean.sources import *
from .clean.sources import _sources
from .clean.tags import *
from .clean.tags import _tags

# Mapping of FRED API endpoints to their respective cleaning functions
FRED_ENDPOINTS = {
    # Categories
    "category": category,
    "category/children": category_children,
    "category/related": category_related,
    "category/series": category_series,
    
    # Releases
    "releases": _releases,
    "releases/dates": releases_dates,
    "release": release,
    "release/dates": release_dates,
    "release/series": release_series,
    "release/sources": release_sources,
    "release/tags": release_tags,
    "release/related_tags": release_related_tags,
    "release/tables": release_tables,
    
    # Series
    "series": _series,
    "series/categories": series_categories,
    "series/observations": series_observations,
    "series/release": series_release,
    "series/search": series_search,
    "series/search/tags": series_search_tags,
    "series/search/related_tags": series_search_related_tags,
    "series/tags": series_tags,
    "series/updates": series_updates,
    "series/vintagedates": series_vintagedates,
    
    # Sources
    "sources": _sources,
    "source": source,
    "source/releases": source_releases,
    
    # Tags
    "tags": _tags,
    "related_tags": related_tags,
    "tags/series": tags_series,
}