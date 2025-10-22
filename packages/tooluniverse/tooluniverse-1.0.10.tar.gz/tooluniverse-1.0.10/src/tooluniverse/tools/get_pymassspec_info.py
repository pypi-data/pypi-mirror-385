"""
get_pymassspec_info

Get comprehensive information about PyMassSpec – mass spectrometry data analysis
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def get_pymassspec_info(
    info_type: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get comprehensive information about PyMassSpec – mass spectrometry data analysis

    Parameters
    ----------
    info_type : str
        Type of information to retrieve about PyMassSpec
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
        {"name": "get_pymassspec_info", "arguments": {"info_type": info_type}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["get_pymassspec_info"]
