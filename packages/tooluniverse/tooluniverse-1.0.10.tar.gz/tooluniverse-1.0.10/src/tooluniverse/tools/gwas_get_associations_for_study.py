"""
gwas_get_associations_for_study

Get all associations for a specific study, sorted by p-value.
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def gwas_get_associations_for_study(
    accession_id: str,
    size: Optional[int] = None,
    page: Optional[int] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Get all associations for a specific study, sorted by p-value.

    Parameters
    ----------
    accession_id : str
        Study accession identifier
    size : int
        Number of results to return per page
    page : int
        Page number for pagination
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
            "name": "gwas_get_associations_for_study",
            "arguments": {"accession_id": accession_id, "size": size, "page": page},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["gwas_get_associations_for_study"]
