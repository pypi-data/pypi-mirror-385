"""
get_space_group_by_pdb_id

Get the crystallographic space group of the structure.
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def get_space_group_by_pdb_id(
    pdb_id: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get the crystallographic space group of the structure.

    Parameters
    ----------
    pdb_id : str
        4-character RCSB PDB ID
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
        {"name": "get_space_group_by_pdb_id", "arguments": {"pdb_id": pdb_id}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["get_space_group_by_pdb_id"]
