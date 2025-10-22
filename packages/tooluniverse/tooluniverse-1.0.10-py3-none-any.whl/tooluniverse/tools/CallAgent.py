"""
CallAgent

Give a solution plan to the agent and let it solve the problem. Solution plan should reflect a di...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def CallAgent(
    solution: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Give a solution plan to the agent and let it solve the problem. Solution plan should reflect a di...

    Parameters
    ----------
    solution : str
        A feasible and concise solution plan that address the question.
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
        {"name": "CallAgent", "arguments": {"solution": solution}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["CallAgent"]
