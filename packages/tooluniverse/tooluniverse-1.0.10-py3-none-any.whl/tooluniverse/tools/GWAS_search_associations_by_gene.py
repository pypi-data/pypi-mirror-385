"""
GWAS_search_associations_by_gene

Search GWAS Catalog associations by gene name (returns strongest risk allele and p-value fields).
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def GWAS_search_associations_by_gene(
    gene_name: str,
    size: Optional[int] = 5,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Search GWAS Catalog associations by gene name (returns strongest risk allele and p-value fields).

    Parameters
    ----------
    gene_name : str
        Gene symbol (e.g., BRCA1).
    size : int
        Max associations to return.
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
        {
            "name": "GWAS_search_associations_by_gene",
            "arguments": {"gene_name": gene_name, "size": size},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["GWAS_search_associations_by_gene"]
