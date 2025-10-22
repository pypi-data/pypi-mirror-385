"""
OpenTargets_get_drug_id_description_by_name

Fetch the drug chemblId and description based on the drug generic name.
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def OpenTargets_get_drug_id_description_by_name(
    drugName: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Fetch the drug chemblId and description based on the drug generic name.

    Parameters
    ----------
    drugName : str
        The name of the drug for which the ID is required.
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
            "name": "OpenTargets_get_drug_id_description_by_name",
            "arguments": {"drugName": drugName},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenTargets_get_drug_id_description_by_name"]
