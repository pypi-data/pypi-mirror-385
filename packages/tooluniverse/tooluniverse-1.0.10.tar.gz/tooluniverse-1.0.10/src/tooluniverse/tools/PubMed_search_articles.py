"""
PubMed_search_articles

Search PubMed using NCBI E-utilities (esearch + esummary) and return articles. Returns articles w...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def PubMed_search_articles(
    query: str,
    limit: Optional[int] = 10,
    api_key: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> list[Any]:
    """
    Search PubMed using NCBI E-utilities (esearch + esummary) and return articles. Returns articles w...

    Parameters
    ----------
    query : str
        Search query for PubMed articles. Use keywords separated by spaces to refine ...
    limit : int
        Number of articles to return. This sets the maximum number of articles retrie...
    api_key : str
        Optional NCBI API key for higher rate limits. Get your free key at https://ww...
    stream_callback : Callable, optional
        Callback for streaming output
    use_cache : bool, default False
        Enable caching
    validate : bool, default True
        Validate parameters

    Returns
    -------
    list[Any]
    """
    # Handle mutable defaults to avoid B006 linting error

    return get_shared_client().run_one_function(
        {
            "name": "PubMed_search_articles",
            "arguments": {"query": query, "limit": limit, "api_key": api_key},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["PubMed_search_articles"]
