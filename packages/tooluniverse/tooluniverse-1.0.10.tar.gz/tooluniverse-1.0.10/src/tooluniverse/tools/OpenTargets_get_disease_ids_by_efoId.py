"""
OpenTargets_get_disease_ids_by_efoId

Given an EFO ID, retrieve all cross-referenced external disease IDs including MONDO, OMIM, MeSH, ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def OpenTargets_get_disease_ids_by_efoId(
    efoId: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Given an EFO ID, retrieve all cross-referenced external disease IDs including MONDO, OMIM, MeSH, ...

    Parameters
    ----------
    efoId : str
        The EFO ID of the disease or phenotype.
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
        {"name": "OpenTargets_get_disease_ids_by_efoId", "arguments": {"efoId": efoId}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenTargets_get_disease_ids_by_efoId"]
