"""
get_harmony_pytorch_info

Get comprehensive information about harmony-pytorch – single-cell data integration
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def get_harmony_pytorch_info(
    info_type: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get comprehensive information about harmony-pytorch – single-cell data integration

    Parameters
    ----------
    info_type : str
        Type of information to retrieve about harmony-pytorch
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
        {"name": "get_harmony_pytorch_info", "arguments": {"info_type": info_type}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["get_harmony_pytorch_info"]
