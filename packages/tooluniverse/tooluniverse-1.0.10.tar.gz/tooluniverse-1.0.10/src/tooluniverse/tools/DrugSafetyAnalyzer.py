"""
DrugSafetyAnalyzer

Comprehensive drug safety analysis combining adverse event data, literature review, and molecular...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def DrugSafetyAnalyzer(
    drug_name: str,
    patient_sex: str,
    serious_events_only: bool,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Comprehensive drug safety analysis combining adverse event data, literature review, and molecular...

    Parameters
    ----------
    drug_name : str
        Name of the drug to analyze
    patient_sex : str
        Filter by patient sex (optional)
    serious_events_only : bool
        Focus only on serious adverse events
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
            "name": "DrugSafetyAnalyzer",
            "arguments": {
                "drug_name": drug_name,
                "patient_sex": patient_sex,
                "serious_events_only": serious_events_only,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["DrugSafetyAnalyzer"]
