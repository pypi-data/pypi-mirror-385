"""
get_chem_comp_charge_and_ambiguity

Retrieve the formal charge and ambiguity flag of a chemical component.
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def get_chem_comp_charge_and_ambiguity(
    pdb_id: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve the formal charge and ambiguity flag of a chemical component.

    Parameters
    ----------
    pdb_id : str
        Chemical component ID to query charge and ambiguity
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
        {"name": "get_chem_comp_charge_and_ambiguity", "arguments": {"pdb_id": pdb_id}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["get_chem_comp_charge_and_ambiguity"]
