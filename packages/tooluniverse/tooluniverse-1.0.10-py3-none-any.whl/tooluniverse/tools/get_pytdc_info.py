"""
get_pytdc_info

Get comprehensive information about PyTDC – Therapeutics Data Commons in Python
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def get_pytdc_info(
    info_type: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get comprehensive information about PyTDC – Therapeutics Data Commons in Python

    Parameters
    ----------
    info_type : str
        Type of information to retrieve about PyTDC
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
        {"name": "get_pytdc_info", "arguments": {"info_type": info_type}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["get_pytdc_info"]
