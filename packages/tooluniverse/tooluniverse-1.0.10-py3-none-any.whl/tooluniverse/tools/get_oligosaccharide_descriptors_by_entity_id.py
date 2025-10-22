"""
get_oligosaccharide_descriptors_by_entity_id

Retrieve structural descriptors for branched entities (e.g., oligosaccharides) in a PDB entry.
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def get_oligosaccharide_descriptors_by_entity_id(
    entity_id: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve structural descriptors for branched entities (e.g., oligosaccharides) in a PDB entry.

    Parameters
    ----------
    entity_id : str
        Branched entity ID like '5FMB_2'
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
            "name": "get_oligosaccharide_descriptors_by_entity_id",
            "arguments": {"entity_id": entity_id},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["get_oligosaccharide_descriptors_by_entity_id"]
