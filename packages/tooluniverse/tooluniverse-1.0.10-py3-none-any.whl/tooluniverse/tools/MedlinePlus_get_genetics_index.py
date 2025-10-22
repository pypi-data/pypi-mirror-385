"""
MedlinePlus_get_genetics_index

Download index file (XML) of all genetics entries in MedlinePlus, get complete list in one call.
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def MedlinePlus_get_genetics_index(
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Download index file (XML) of all genetics entries in MedlinePlus, get complete list in one call.

    Parameters
    ----------
    No parameters
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
        {"name": "MedlinePlus_get_genetics_index", "arguments": {}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["MedlinePlus_get_genetics_index"]
