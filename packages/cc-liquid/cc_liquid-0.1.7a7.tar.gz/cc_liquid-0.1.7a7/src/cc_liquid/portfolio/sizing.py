from __future__ import annotations

from typing import Dict, Iterable, Mapping, Sequence

import polars as pl


def weights_from_ranks(
    latest_preds: pl.DataFrame | Sequence[tuple[str, float]] | Mapping[str, float],
    *,
    id_col: str = "id",
    pred_col: str = "pred",
    long_assets: Sequence[str],
    short_assets: Sequence[str],
    target_gross: float,
    power: float = 0.0,
) -> Dict[str, float]:
    """Convert ranks (higher = stronger long) to signed weights using rank power weighting.

    The output weights sum in absolute value to ``target_gross``.
    
    Weighting uses (rank/n)^power formula where power=0.0 produces equal weights.

    ``latest_preds`` accepts either:
    - Polars DataFrame with ``id_col``/``pred_col``
    - Iterable mapping asset id to score
    - Dict[str, float]
    """

    # Normalize predictions into a simple dict for quick lookups.
    if isinstance(latest_preds, pl.DataFrame):
        preds_dict = dict(zip(latest_preds[id_col], latest_preds[pred_col]))
    elif isinstance(latest_preds, Mapping):
        preds_dict = dict(latest_preds)
    else:
        preds_dict = {asset: score for asset, score in latest_preds}

    n_long, n_short = len(long_assets), len(short_assets)
    total_positions = n_long + n_short
    if total_positions == 0 or target_gross <= 0:
        return {}

    gross_long = target_gross * (n_long / total_positions)
    gross_short = target_gross * (n_short / total_positions)

    def _side(ids: Iterable[str], gross: float, sign: float) -> Dict[str, float]:
        ids_list = [i for i in ids if i in preds_dict]
        n = len(ids_list)
        if n == 0 or gross <= 0:
            return {}

        # Fetch scores and rank within this side (best first).
        scored = sorted(
            ((preds_dict[i], i) for i in ids_list),
            key=lambda x: x[0],
            reverse=sign > 0,
        )

        # Use rank power weighting: when power=0, all weights equal 1.0
        p = max(1e-6, float(power))
        raw: list[float] = [((n - idx) / n) ** p for idx in range(n)]

        denom = sum(raw) or 1.0
        scale = gross / denom

        return {asset: sign * raw[idx] * scale for idx, (_, asset) in enumerate(scored)}

    weights_long = _side(long_assets, gross_long, +1.0)
    weights_short = _side(short_assets, gross_short, -1.0)

    return {**weights_long, **weights_short}
