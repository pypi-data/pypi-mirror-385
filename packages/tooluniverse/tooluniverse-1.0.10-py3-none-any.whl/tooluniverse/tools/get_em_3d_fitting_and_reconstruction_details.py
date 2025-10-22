"""
get_em_3d_fitting_and_reconstruction_details

Retrieve EM 3D fitting model details and associated 3D reconstruction info for a given PDB entry.
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def get_em_3d_fitting_and_reconstruction_details(
    pdb_id: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve EM 3D fitting model details and associated 3D reconstruction info for a given PDB entry.

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
        {
            "name": "get_em_3d_fitting_and_reconstruction_details",
            "arguments": {"pdb_id": pdb_id},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["get_em_3d_fitting_and_reconstruction_details"]
