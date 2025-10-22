"""
get_clinical_trial_references

Retrieves the references (if any) for the clinical trials, using their NCT IDs.
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def get_clinical_trial_references(
    nct_ids: list[Any],
    references: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieves the references (if any) for the clinical trials, using their NCT IDs.

    Parameters
    ----------
    nct_ids : list[Any]
        List of NCT IDs of the clinical trials (e.g., ['NCT04852770', 'NCT01728545']).
    references : str
        Placeholder.
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
            "name": "get_clinical_trial_references",
            "arguments": {"nct_ids": nct_ids, "references": references},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["get_clinical_trial_references"]
