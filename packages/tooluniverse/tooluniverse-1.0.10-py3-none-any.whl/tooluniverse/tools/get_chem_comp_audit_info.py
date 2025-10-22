"""
get_chem_comp_audit_info

Fetch audit history for a chemical component: action type, date, details, ordinal, and processing...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def get_chem_comp_audit_info(
    pdb_id: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Fetch audit history for a chemical component: action type, date, details, ordinal, and processing...

    Parameters
    ----------
    pdb_id : str
        Chemical component ID to retrieve audit info for
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
        {"name": "get_chem_comp_audit_info", "arguments": {"pdb_id": pdb_id}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["get_chem_comp_audit_info"]
