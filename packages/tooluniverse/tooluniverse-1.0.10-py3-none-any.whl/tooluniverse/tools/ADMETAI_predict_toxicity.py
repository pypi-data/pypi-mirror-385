"""
ADMETAI_predict_toxicity

Predicts toxicity endpoints (AMES, Carcinogens_Lagunin, ClinTox, DILI, LD50_Zhu, Skin_Reaction, h...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def ADMETAI_predict_toxicity(
    smiles: list[Any],
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Predicts toxicity endpoints (AMES, Carcinogens_Lagunin, ClinTox, DILI, LD50_Zhu, Skin_Reaction, h...

    Parameters
    ----------
    smiles : list[Any]
        The list of SMILES strings.
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
        {"name": "ADMETAI_predict_toxicity", "arguments": {"smiles": smiles}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ADMETAI_predict_toxicity"]
