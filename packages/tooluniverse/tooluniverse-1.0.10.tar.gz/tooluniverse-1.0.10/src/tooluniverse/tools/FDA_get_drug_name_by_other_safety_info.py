"""
FDA_get_drug_name_by_other_safety_info

Retrieve the drug name based on the provided safety information. This tool looks through safety i...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def FDA_get_drug_name_by_other_safety_info(
    safety_info: str,
    limit: Optional[int] = None,
    skip: Optional[int] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve the drug name based on the provided safety information. This tool looks through safety i...

    Parameters
    ----------
    safety_info : str
        Information about safe use and handling of the product.
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
            "name": "FDA_get_drug_name_by_other_safety_info",
            "arguments": {"safety_info": safety_info, "limit": limit, "skip": skip},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["FDA_get_drug_name_by_other_safety_info"]
