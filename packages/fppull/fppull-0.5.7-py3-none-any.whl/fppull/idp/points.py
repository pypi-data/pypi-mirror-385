from __future__ import annotations
import json
from typing import Iterable, Optional
import pandas as pd


def _extract_slot_override(row) -> Optional[float]:
    """
    Return the slot-17 (IDP) override for this stat row if present, else None.
    Expects row["pointsOverrides"] to be a JSON string or dict mapping slotId->points.
    """
    po = row.get("pointsOverrides")
    if po is None or (isinstance(po, float) and pd.isna(po)):
        return None
    if isinstance(po, str) and po.strip():
        try:
            po = json.loads(po)
        except Exception:
            return None
    if isinstance(po, dict):
        v = po.get("17")
        try:
            return float(v) if v is not None else None
        except Exception:
            return None
    return None


def _build_idp_scoring_map(scoring_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a mapping of statId -> points for IDP slot.
    Priority: use slot-17 override; else fall back to generic 'points'.
    Expected scoring_df columns: ['statId', 'points', 'pointsOverrides'].
    """
    cols_needed = {"statId", "points"}
    if not cols_needed.issubset(scoring_df.columns):
        missing = cols_needed - set(scoring_df.columns)
        raise ValueError(f"scoring_df missing required columns: {missing}")

    df = scoring_df.copy()
    df["__idp_override"] = df.apply(_extract_slot_override, axis=1)
    df["idp_points"] = df["__idp_override"].where(
        df["__idp_override"].notna(), df["points"]
    )
    df["idp_points"] = df["idp_points"].astype(float)
    return df[["statId", "idp_points"]].drop_duplicates("statId")


def compute_idp_points(
    idp_stats: pd.DataFrame,
    scoring_df: pd.DataFrame,
    *,
    group_keys: Iterable[str] = ("season", "week", "player_id"),
    stat_id_col: str = "statId",
    value_col: str = "value",
) -> pd.DataFrame:
    """
    Compute IDP fantasy points from per-stat counts and league scoring.

    Returns DataFrame with group_keys + ['points', 'components_json'].
    """
    for col in list(group_keys) + [stat_id_col, value_col]:
        if col not in idp_stats.columns:
            raise ValueError(f"idp_stats missing required column: {col}")

    idp_map = _build_idp_scoring_map(scoring_df)

    merged = idp_stats.merge(
        idp_map, how="left", left_on=stat_id_col, right_on="statId"
    )
    if merged["idp_points"].isna().any():
        merged["idp_points"] = merged["idp_points"].fillna(0.0)

    merged["__contrib"] = merged[value_col].astype(float) * merged["idp_points"].astype(
        float
    )

    group_cols = list(group_keys)

    # Sum points per grouping
    points_df = (
        merged.groupby(group_cols, dropna=False, as_index=False)["__contrib"]
        .sum()
        .rename(columns={"__contrib": "points"})
    )

    # Build a compact JSON of per-stat contributions per group (scalar apply; no grouping cols included)
    def _components(g: pd.DataFrame) -> str:
        return json.dumps(
            [
                {
                    "statId": int(sid),
                    "count": float(val),
                    "pts_per": float(w),
                    "contrib": float(val) * float(w),
                }
                for sid, val, w in zip(
                    g[stat_id_col].tolist(),
                    g[value_col].astype(float).tolist(),
                    g["idp_points"].astype(float).tolist(),
                )
            ]
        )

    # Build components_json per group using a small Python loop (avoids groupby.apply warning)
    recs = []
    for keys, g in merged.groupby(group_cols, dropna=False):
        # keys can be scalar or tuple depending on len(group_cols)
        if not isinstance(keys, tuple):
            keys = (keys,)
        row = dict(zip(group_cols, keys))
        row["components_json"] = _components(g)
        recs.append(row)
    comps_df = pd.DataFrame.from_records(recs)

    out = points_df.merge(comps_df, on=group_cols, how="inner")
    return out
