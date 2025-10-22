"""
ToolGraphGenerationPipeline

Generates a directed tool relationship graph among provided tool configs using ToolRelationshipDe...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def ToolGraphGenerationPipeline(
    tool_configs: list[Any],
    max_tools: int,
    output_path: str,
    save_intermediate_every: int,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Generates a directed tool relationship graph among provided tool configs using ToolRelationshipDe...

    Parameters
    ----------
    tool_configs : list[Any]
        List of tool configuration objects
    max_tools : int
        Optional max number of tools to process (debug)
    output_path : str
        Path for output graph JSON
    save_intermediate_every : int
        Checkpoint every N processed pairs
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
            "name": "ToolGraphGenerationPipeline",
            "arguments": {
                "tool_configs": tool_configs,
                "max_tools": max_tools,
                "output_path": output_path,
                "save_intermediate_every": save_intermediate_every,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ToolGraphGenerationPipeline"]
