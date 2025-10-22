"""
mesh_get_subjects_by_pharmacological_action

Find MeSH (Medical Subject Heading) subjects with matching pharmacological actions.
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def mesh_get_subjects_by_pharmacological_action(
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
    Find MeSH (Medical Subject Heading) subjects with matching pharmacological actions.

    Parameters
    ----------
    query : str
        Pharmacological action to search for in MeSH subjects
    case_sensitive : bool
        Select True to perform a case-sensitive search for the pharmacological action...
    exact_match : bool
        Select True to require an exact match for the pharmacological action query
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
            "name": "mesh_get_subjects_by_pharmacological_action",
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


__all__ = ["mesh_get_subjects_by_pharmacological_action"]
