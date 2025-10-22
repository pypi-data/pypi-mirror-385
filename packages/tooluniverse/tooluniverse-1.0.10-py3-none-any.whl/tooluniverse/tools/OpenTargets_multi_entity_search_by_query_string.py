"""
OpenTargets_multi_entity_search_by_query_string

Perform a multi-entity search based on a query string, filtering by entity names and pagination s...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def OpenTargets_multi_entity_search_by_query_string(
    queryString: str,
    entityNames: Optional[list[Any]] = None,
    page: Optional[dict[str, Any]] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Perform a multi-entity search based on a query string, filtering by entity names and pagination s...

    Parameters
    ----------
    queryString : str
        The search string for querying information.
    entityNames : list[Any]
        List of entity names to search for (e.g., target, disease, drug).
    page : dict[str, Any]
        Pagination settings with index and size.
    stream_callback : Callable, optional
        Callback for streaming output
    use_cache : bool, default False
        Enable caching
    validate : bool, default True
        Validate parameters

    Returns
    -------
    Any
    """
    # Handle mutable defaults to avoid B006 linting error

    return get_shared_client().run_one_function(
        {
            "name": "OpenTargets_multi_entity_search_by_query_string",
            "arguments": {
                "queryString": queryString,
                "entityNames": entityNames,
                "page": page,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenTargets_multi_entity_search_by_query_string"]
