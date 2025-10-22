"""
get_core_refinement_statistics

Retrieve essential refinement statistics for a given PDB structure including R-factors, occupancy...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def get_core_refinement_statistics(
    pdb_id: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve essential refinement statistics for a given PDB structure including R-factors, occupancy...

    Parameters
    ----------
    pdb_id : str
        PDB entry ID (e.g., '1ABC')
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
        {"name": "get_core_refinement_statistics", "arguments": {"pdb_id": pdb_id}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["get_core_refinement_statistics"]
