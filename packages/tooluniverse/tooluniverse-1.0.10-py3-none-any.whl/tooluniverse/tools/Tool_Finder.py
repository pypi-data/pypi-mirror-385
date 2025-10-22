"""
Tool_Finder

Retrieve related tools from the toolbox based on the provided description, advanced version with ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Tool_Finder(
    description: str,
    limit: int,
    picked_tool_names: Optional[list[Any]] = None,
    return_call_result: Optional[bool] = None,
    categories: Optional[list[Any]] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve related tools from the toolbox based on the provided description, advanced version with ...

    Parameters
    ----------
    description : str
        The description of the tool capability required.
    limit : int
        The number of tools to retrieve
    picked_tool_names : list[Any]
        Pre-selected tool names to process. If provided, tool selection will skip the...
    return_call_result : bool
        Whether to return both prompts and tool names. If false, returns only tool pr...
    categories : list[Any]
        Optional list of tool categories to filter by
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
            "name": "Tool_Finder",
            "arguments": {
                "description": description,
                "limit": limit,
                "picked_tool_names": picked_tool_names,
                "return_call_result": return_call_result,
                "categories": categories,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Tool_Finder"]
