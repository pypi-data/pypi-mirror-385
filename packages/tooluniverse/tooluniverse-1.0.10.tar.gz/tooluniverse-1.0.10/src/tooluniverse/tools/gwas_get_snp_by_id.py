"""
gwas_get_snp_by_id

Get a specific GWAS SNP by its rs ID.
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def gwas_get_snp_by_id(
    rs_id: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Get a specific GWAS SNP by its rs ID.

    Parameters
    ----------
    rs_id : str
        dbSNP rs identifier
    stream_callback : Callable, optional
        Callback for streaming output
    use_cache : bool, default False
        Enable caching
    validate : bool, default True
        Validate parameters

    Returns
    -------
    dict[str, Any]
    """
    # Handle mutable defaults to avoid B006 linting error

    return get_shared_client().run_one_function(
        {"name": "gwas_get_snp_by_id", "arguments": {"rs_id": rs_id}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["gwas_get_snp_by_id"]
