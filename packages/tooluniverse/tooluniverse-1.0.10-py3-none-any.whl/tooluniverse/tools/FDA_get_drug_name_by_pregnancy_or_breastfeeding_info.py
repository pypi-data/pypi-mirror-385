"""
FDA_get_drug_name_by_pregnancy_or_breastfeeding_info

Retrieve the drug names based on pregnancy or breastfeeding information.
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def FDA_get_drug_name_by_pregnancy_or_breastfeeding_info(
    pregnancy_info: str,
    limit: Optional[int] = None,
    skip: Optional[int] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve the drug names based on pregnancy or breastfeeding information.

    Parameters
    ----------
    pregnancy_info : str
        Information related to pregnancy or breastfeeding.
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
            "name": "FDA_get_drug_name_by_pregnancy_or_breastfeeding_info",
            "arguments": {
                "pregnancy_info": pregnancy_info,
                "limit": limit,
                "skip": skip,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["FDA_get_drug_name_by_pregnancy_or_breastfeeding_info"]
