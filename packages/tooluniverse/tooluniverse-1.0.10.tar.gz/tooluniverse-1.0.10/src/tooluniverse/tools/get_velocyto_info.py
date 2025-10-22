"""
get_velocyto_info

Get information about the velocyto package. RNA velocity analysis for single cell RNA-seq data
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def get_velocyto_info(
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get information about the velocyto package. RNA velocity analysis for single cell RNA-seq data

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
        {"name": "get_velocyto_info", "arguments": {}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["get_velocyto_info"]
