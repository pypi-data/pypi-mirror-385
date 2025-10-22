"""
GO_get_annotations_for_gene

Finds all GO annotations for a specific gene/protein using GOlr search.
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def GO_get_annotations_for_gene(
    gene_id: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Finds all GO annotations for a specific gene/protein using GOlr search.

    Parameters
    ----------
    gene_id : str
        A gene identifier such as gene symbol (e.g., 'TP53') or database ID.
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
        {"name": "GO_get_annotations_for_gene", "arguments": {"gene_id": gene_id}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["GO_get_annotations_for_gene"]
