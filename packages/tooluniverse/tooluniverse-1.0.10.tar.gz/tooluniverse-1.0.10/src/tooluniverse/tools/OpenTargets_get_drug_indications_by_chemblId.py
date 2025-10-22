"""
OpenTargets_get_drug_indications_by_chemblId

Fetch indications (treatable phenotypes/diseases) for a given drug chemblId.
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def OpenTargets_get_drug_indications_by_chemblId(
    chemblId: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Fetch indications (treatable phenotypes/diseases) for a given drug chemblId.

    Parameters
    ----------
    chemblId : str
        The chemblId of the drug for which to retrieve treatable phenotypes information.
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
            "name": "OpenTargets_get_drug_indications_by_chemblId",
            "arguments": {"chemblId": chemblId},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenTargets_get_drug_indications_by_chemblId"]
