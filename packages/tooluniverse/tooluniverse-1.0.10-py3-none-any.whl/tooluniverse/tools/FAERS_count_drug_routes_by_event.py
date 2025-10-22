"""
FAERS_count_drug_routes_by_event

Count the most common routes of administration for drugs involved in adverse event reports. Data ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def FAERS_count_drug_routes_by_event(
    medicinalproduct: str,
    serious: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Count the most common routes of administration for drugs involved in adverse event reports. Data ...

    Parameters
    ----------
    medicinalproduct : str
        Drug name.
    serious : str
        Seriousness of event.
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
            "name": "FAERS_count_drug_routes_by_event",
            "arguments": {"medicinalproduct": medicinalproduct, "serious": serious},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["FAERS_count_drug_routes_by_event"]
