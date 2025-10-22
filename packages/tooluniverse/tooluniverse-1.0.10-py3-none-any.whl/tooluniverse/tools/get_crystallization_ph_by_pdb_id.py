"""
get_crystallization_ph_by_pdb_id

Fetch the pH used during crystallization of the sample.
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def get_crystallization_ph_by_pdb_id(
    pdb_id: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Fetch the pH used during crystallization of the sample.

    Parameters
    ----------
    pdb_id : str
        RCSB PDB ID of the structure
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
        {"name": "get_crystallization_ph_by_pdb_id", "arguments": {"pdb_id": pdb_id}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["get_crystallization_ph_by_pdb_id"]
