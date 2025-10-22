"""
OpenTargets_get_target_genomic_location_by_ensemblID

Retrieve genomic location data for a specific target, including chromosome, start, end, and strand.
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def OpenTargets_get_target_genomic_location_by_ensemblID(
    ensemblId: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve genomic location data for a specific target, including chromosome, start, end, and strand.

    Parameters
    ----------
    ensemblId : str
        The Ensembl ID of the target for which to retrieve genomic location information.
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
            "name": "OpenTargets_get_target_genomic_location_by_ensemblID",
            "arguments": {"ensemblId": ensemblId},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenTargets_get_target_genomic_location_by_ensemblID"]
