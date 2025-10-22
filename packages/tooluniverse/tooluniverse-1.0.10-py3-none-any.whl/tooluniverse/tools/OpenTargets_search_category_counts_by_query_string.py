"""
OpenTargets_search_category_counts_by_query_string

Get the count of entries in each entity category (disease, target, drug) based on a query string.
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def OpenTargets_search_category_counts_by_query_string(
    queryString: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get the count of entries in each entity category (disease, target, drug) based on a query string.

    Parameters
    ----------
    queryString : str
        The search string for querying information.
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
            "name": "OpenTargets_search_category_counts_by_query_string",
            "arguments": {"queryString": queryString},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenTargets_search_category_counts_by_query_string"]
