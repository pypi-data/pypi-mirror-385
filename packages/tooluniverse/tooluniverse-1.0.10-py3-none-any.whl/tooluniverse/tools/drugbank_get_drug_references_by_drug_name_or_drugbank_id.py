"""
drugbank_get_drug_references_by_drug_name_or_drugbank_id

Get drug literature references, patents, and external links by drug name or DrugBank ID.
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def drugbank_get_drug_references_by_drug_name_or_drugbank_id(
    query: str,
    case_sensitive: bool,
    exact_match: bool,
    limit: int,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Get drug literature references, patents, and external links by drug name or DrugBank ID.

    Parameters
    ----------
    query : str
        Drug name or Drugbank ID to search for references
    case_sensitive : bool
        Select True to perform a case-sensitive search
    exact_match : bool
        Select True to require an exact match
    limit : int
        Maximum number of results to return
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
            "name": "drugbank_get_drug_references_by_drug_name_or_drugbank_id",
            "arguments": {
                "query": query,
                "case_sensitive": case_sensitive,
                "exact_match": exact_match,
                "limit": limit,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["drugbank_get_drug_references_by_drug_name_or_drugbank_id"]
