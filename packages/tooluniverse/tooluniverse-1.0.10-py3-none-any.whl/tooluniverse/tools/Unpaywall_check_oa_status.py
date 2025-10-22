"""
Unpaywall_check_oa_status

Query Unpaywall by DOI to check open-access status and OA locations. Requires a contact email for...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Unpaywall_check_oa_status(
    doi: str,
    email: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Query Unpaywall by DOI to check open-access status and OA locations. Requires a contact email for...

    Parameters
    ----------
    doi : str
        DOI (Digital Object Identifier) of the article to check for open access status.
    email : str
        Contact email address required by Unpaywall API for polite usage tracking.
    stream_callback : Callable, optional
        Callback for streaming output
    use_cache : bool, default False
        Enable caching
    validate : bool, default True
        Validate parameters

    Returns
    -------
    dict[str, Any]
    """
    # Handle mutable defaults to avoid B006 linting error

    return get_shared_client().run_one_function(
        {
            "name": "Unpaywall_check_oa_status",
            "arguments": {"doi": doi, "email": email},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Unpaywall_check_oa_status"]
