"""
get_webpage_title

Fetch a webpage and return the content of its <title> tag.
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def get_webpage_title(
    url: str,
    timeout: int,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Fetch a webpage and return the content of its <title> tag.

    Parameters
    ----------
    url : str
        HTTP or HTTPS URL to fetch (e.g. https://www.example.com)
    timeout : int
        Request timeout in seconds
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
        {"name": "get_webpage_title", "arguments": {"url": url, "timeout": timeout}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["get_webpage_title"]
