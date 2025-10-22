"""
OpenTargets_get_disease_id_description_by_name

Retrieve the efoId and additional details of a disease based on its name.
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def OpenTargets_get_disease_id_description_by_name(
    diseaseName: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve the efoId and additional details of a disease based on its name.

    Parameters
    ----------
    diseaseName : str
        The name of the disease to search for.
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
            "name": "OpenTargets_get_disease_id_description_by_name",
            "arguments": {"diseaseName": diseaseName},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenTargets_get_disease_id_description_by_name"]
