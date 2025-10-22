"""
HPA_get_gene_tsv_data_by_ensembl_id

Get detailed gene data in TSV format from Human Protein Atlas using Ensembl Gene ID (backward com...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def HPA_get_gene_tsv_data_by_ensembl_id(
    ensembl_id: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get detailed gene data in TSV format from Human Protein Atlas using Ensembl Gene ID (backward com...

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
            "name": "HPA_get_gene_tsv_data_by_ensembl_id",
            "arguments": {"ensembl_id": ensembl_id},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["HPA_get_gene_tsv_data_by_ensembl_id"]
