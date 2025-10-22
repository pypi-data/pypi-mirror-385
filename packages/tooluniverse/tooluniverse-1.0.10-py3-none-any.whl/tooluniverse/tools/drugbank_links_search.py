"""
drugbank_links_search

Search the cross-reference table linking DrugBank IDs to external identifiers (CAS, KEGG, PubChem...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def drugbank_links_search(
    query: str,
    search_fields: list[Any],
    case_sensitive: bool,
    exact_match: bool,
    limit: int,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Search the cross-reference table linking DrugBank IDs to external identifiers (CAS, KEGG, PubChem...

    Parameters
    ----------
    query : str
        Free-text query (e.g. 'DB00002', 'Cetuximab').
    search_fields : list[Any]
        Columns to search. Choose from: 'DrugBank ID', 'Name', 'CAS Number', 'Drug Ty...
    case_sensitive : bool
        Match text with exact case if true.
    exact_match : bool
        Field value must equal query exactly if true; otherwise substring match.
    limit : int
        Maximum number of rows to return.
    stream_callback : Callable, optional
        Callback for streaming output
    use_cache : bool, default False
        Enable caching
    validate : bool, default True
        Validate parameters

    Returns
    -------
    dict[str, Any]
    """
    # Handle mutable defaults to avoid B006 linting error

    return get_shared_client().run_one_function(
        {
            "name": "drugbank_links_search",
            "arguments": {
                "query": query,
                "search_fields": search_fields,
                "case_sensitive": case_sensitive,
                "exact_match": exact_match,
                "limit": limit,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["drugbank_links_search"]
