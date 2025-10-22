"""
FAERS_count_patient_age_distribution

Analyze the age distribution of patients experiencing adverse events for a specific drug. The age...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def FAERS_count_patient_age_distribution(
    medicinalproduct: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Analyze the age distribution of patients experiencing adverse events for a specific drug. The age...

    Parameters
    ----------
    medicinalproduct : str
        Drug name.
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
            "name": "FAERS_count_patient_age_distribution",
            "arguments": {"medicinalproduct": medicinalproduct},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["FAERS_count_patient_age_distribution"]
