"""
get_ligand_smiles_by_chem_comp_id

Retrieve the SMILES chemical structure string for a given chemical component (ligand) ID.
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def get_ligand_smiles_by_chem_comp_id(
    chem_comp_id: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve the SMILES chemical structure string for a given chemical component (ligand) ID.

    Parameters
    ----------
    chem_comp_id : str
        Chemical component ID (e.g., 'ATP')
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
            "name": "get_ligand_smiles_by_chem_comp_id",
            "arguments": {"chem_comp_id": chem_comp_id},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["get_ligand_smiles_by_chem_comp_id"]
