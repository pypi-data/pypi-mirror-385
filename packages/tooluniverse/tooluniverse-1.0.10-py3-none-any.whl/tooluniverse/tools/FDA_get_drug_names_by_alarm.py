"""
FDA_get_drug_names_by_alarm

Retrieve drug names based on the presence of specific alarms, which are related to adverse reacti...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def FDA_get_drug_names_by_alarm(
    alarm_type: str,
    indication: Optional[str] = None,
    limit: Optional[int] = None,
    skip: Optional[int] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve drug names based on the presence of specific alarms, which are related to adverse reacti...

    Parameters
    ----------
    alarm_type : str
        The type of alarm to search for.
    indication : str
        The indication or usage of the drug.
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
            "name": "FDA_get_drug_names_by_alarm",
            "arguments": {
                "alarm_type": alarm_type,
                "indication": indication,
                "limit": limit,
                "skip": skip,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["FDA_get_drug_names_by_alarm"]
