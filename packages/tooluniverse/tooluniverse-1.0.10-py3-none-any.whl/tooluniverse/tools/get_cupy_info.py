"""
get_cupy_info

Get information about the cupy package. NumPy-compatible array library accelerated with CUDA
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def get_cupy_info(
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get information about the cupy package. NumPy-compatible array library accelerated with CUDA

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
        {"name": "get_cupy_info", "arguments": {}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["get_cupy_info"]
