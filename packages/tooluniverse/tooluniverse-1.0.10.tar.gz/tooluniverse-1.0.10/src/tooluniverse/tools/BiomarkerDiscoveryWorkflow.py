"""
BiomarkerDiscoveryWorkflow

Discover and validate biomarkers for a specific disease condition using literature analysis, expr...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def BiomarkerDiscoveryWorkflow(
    disease_condition: str,
    sample_type: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Discover and validate biomarkers for a specific disease condition using literature analysis, expr...

    Parameters
    ----------
    disease_condition : str
        The disease condition to discover biomarkers for (e.g., 'breast cancer', 'Alz...
    sample_type : str
        The type of sample to analyze (e.g., 'blood', 'tissue', 'plasma')
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
            "name": "BiomarkerDiscoveryWorkflow",
            "arguments": {
                "disease_condition": disease_condition,
                "sample_type": sample_type,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["BiomarkerDiscoveryWorkflow"]
