"""
get_pypdf2_info

Get comprehensive information about PyPDF2 – PDF manipulation library
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def get_pypdf2_info(
    info_type: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get comprehensive information about PyPDF2 – PDF manipulation library

    Parameters
    ----------
    info_type : str
        Type of information to retrieve about PyPDF2
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
        {"name": "get_pypdf2_info", "arguments": {"info_type": info_type}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["get_pypdf2_info"]
