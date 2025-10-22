"""
humanbase_ppi_analysis

Retrieve tissue-specific protein-protein interactions and biological processes from HumanBase. Re...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def humanbase_ppi_analysis(
    gene_list: list[Any],
    tissue: str,
    max_node: int,
    interaction: str,
    string_mode: bool,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve tissue-specific protein-protein interactions and biological processes from HumanBase. Re...

    Parameters
    ----------
    gene_list : list[Any]
        List of gene names or symbols to analyze for protein-protein interactions. Th...
    tissue : str
        Tissue type for tissue-specific interactions. Examples: 'brain', 'heart', 'li...
    max_node : int
        Maximum number of nodes to retrieve in the interaction network. Warning: the ...
    interaction : str
        Specific interaction type to filter by. Available types: 'co-expression', 'in...
    string_mode : bool
        Whether to return the result in string mode. If True, the result will be a st...
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
            "name": "humanbase_ppi_analysis",
            "arguments": {
                "gene_list": gene_list,
                "tissue": tissue,
                "max_node": max_node,
                "interaction": interaction,
                "string_mode": string_mode,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["humanbase_ppi_analysis"]
