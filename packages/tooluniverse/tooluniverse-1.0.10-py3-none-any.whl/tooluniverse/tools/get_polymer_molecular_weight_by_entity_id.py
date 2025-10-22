"""
get_polymer_molecular_weight_by_entity_id

Retrieve the molecular weight of a polymer entity.
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def get_polymer_molecular_weight_by_entity_id(
    entity_id: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve the molecular weight of a polymer entity.

    Parameters
    ----------
    entity_id : str
        Polymer entity ID like '1A8M_1'
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
            "name": "get_polymer_molecular_weight_by_entity_id",
            "arguments": {"entity_id": entity_id},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["get_polymer_molecular_weight_by_entity_id"]
