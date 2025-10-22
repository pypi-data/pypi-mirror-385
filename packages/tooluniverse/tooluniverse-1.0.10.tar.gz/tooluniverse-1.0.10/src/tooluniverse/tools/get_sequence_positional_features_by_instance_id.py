"""
get_sequence_positional_features_by_instance_id

Retrieve sequence positional features (e.g., binding sites, motifs) for a polymer entity instance.
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def get_sequence_positional_features_by_instance_id(
    instance_id: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve sequence positional features (e.g., binding sites, motifs) for a polymer entity instance.

    Parameters
    ----------
    instance_id : str
        Polymer entity instance ID like '1NDO.A'
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
        {
            "name": "get_sequence_positional_features_by_instance_id",
            "arguments": {"instance_id": instance_id},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["get_sequence_positional_features_by_instance_id"]
