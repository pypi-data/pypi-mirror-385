"""
FDA_get_dependence_info_by_drug_name

Retrieve information about dependence characteristics based on the drug name.
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def FDA_get_dependence_info_by_drug_name(
    drug_name: str,
    limit: Optional[int] = None,
    skip: Optional[int] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve information about dependence characteristics based on the drug name.

    Parameters
    ----------
    drug_name : str
        The name of the drug.
    limit : int
        The number of records to return.
    skip : int
        The number of records to skip.
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
            "name": "FDA_get_dependence_info_by_drug_name",
            "arguments": {"drug_name": drug_name, "limit": limit, "skip": skip},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["FDA_get_dependence_info_by_drug_name"]
