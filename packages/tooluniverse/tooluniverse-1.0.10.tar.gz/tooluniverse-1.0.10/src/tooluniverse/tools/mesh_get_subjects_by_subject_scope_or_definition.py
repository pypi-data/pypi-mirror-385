"""
mesh_get_subjects_by_subject_scope_or_definition

Find MeSH (Medical Subject Heading) subjects with matching scopes (definitions).
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def mesh_get_subjects_by_subject_scope_or_definition(
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
    Find MeSH (Medical Subject Heading) subjects with matching scopes (definitions).

    Parameters
    ----------
    query : str
        Query string to search for in the scope notes of MeSH subjects
    case_sensitive : bool
        Select True to perform a case-sensitive search for the query
    exact_match : bool
        Select True to require an exact match for the query
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
            "name": "mesh_get_subjects_by_subject_scope_or_definition",
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


__all__ = ["mesh_get_subjects_by_subject_scope_or_definition"]
