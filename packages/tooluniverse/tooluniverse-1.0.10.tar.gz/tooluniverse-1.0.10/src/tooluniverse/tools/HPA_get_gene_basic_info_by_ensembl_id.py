"""
HPA_get_gene_basic_info_by_ensembl_id

Get gene basic information and expression data from Human Protein Atlas using Ensembl Gene ID. En...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def HPA_get_gene_basic_info_by_ensembl_id(
    ensembl_id: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get gene basic information and expression data from Human Protein Atlas using Ensembl Gene ID. En...

    Parameters
    ----------
    ensembl_id : str
        Ensembl Gene ID, e.g., 'ENSG00000134057', 'ENSG00000141510', etc.
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
            "name": "HPA_get_gene_basic_info_by_ensembl_id",
            "arguments": {"ensembl_id": ensembl_id},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["HPA_get_gene_basic_info_by_ensembl_id"]
