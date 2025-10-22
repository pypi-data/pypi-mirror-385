"""
odphp_itemlist

This tools browses and returns available topics and categories and it is helpful to help narrow a...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def odphp_itemlist(
    lang: str,
    type: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    This tools browses and returns available topics and categories and it is helpful to help narrow a...

    Parameters
    ----------
    lang : str
        Language code (en or es)
    type : str
        topic or category
    stream_callback : Callable, optional
        Callback for streaming output
    use_cache : bool, default False
        Enable caching
    validate : bool, default True
        Validate parameters

    Returns
    -------
    dict[str, Any]
    """
    # Handle mutable defaults to avoid B006 linting error

    return get_shared_client().run_one_function(
        {"name": "odphp_itemlist", "arguments": {"lang": lang, "type": type}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["odphp_itemlist"]
