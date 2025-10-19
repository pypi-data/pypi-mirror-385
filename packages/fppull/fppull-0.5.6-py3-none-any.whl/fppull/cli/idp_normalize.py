from __future__ import annotations
import argparse
import json
from typing import Optional, Sequence
import pandas as pd


def _auto_format(path: str) -> str:
    p = path.lower()
    if p.endswith(".csv"):
        return "csv"
    if p.endswith(".json"):
        return "json"
    return "csv"  # default


def _read_input(path: str, fmt: str) -> pd.DataFrame:
    if fmt == "csv":
        return pd.read_csv(path)
    if fmt == "json":
        # Expect a list[object] or an object with a top-level list field named "rows" / "items"
        raw = json.loads(open(path, "r", encoding="utf-8").read())
        if isinstance(raw, list):
            return pd.json_normalize(raw)
        if isinstance(raw, dict):
            for k in ("rows", "items", "data"):
                if isinstance(raw.get(k), list):
                    return pd.json_normalize(raw[k])
        # Fallback: normalize the dict itself
        return pd.json_normalize(raw)
    raise SystemExit(f"Unsupported format: {fmt}")


def _choose_first(df: pd.DataFrame, candidates: Sequence[str]) -> Optional[str]:
    for c in candidates:
        if c in df.columns:
            return c
    return None


def _coerce_numeric(s: pd.Series, dtype: str) -> pd.Series:
    if dtype == "i":
        return pd.to_numeric(s, errors="coerce").astype("Int64")
    if dtype == "f":
        return pd.to_numeric(s, errors="coerce").astype(float)
    return s


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="Normalize raw IDP rows into (season,week,player_id,statId,value). Aggregates duplicates."
    )
    ap.add_argument("--in", dest="inp", required=True, help="Input file (CSV or JSON)")
    ap.add_argument("--out", required=True, help="Output CSV path")
    ap.add_argument("--format", choices=("auto", "csv", "json"), default="auto")
    # Column mapping (try common aliases automatically; these override autodetect if provided)
    ap.add_argument(
        "--player-col", help="Column name for player id (aliases tried if omitted)"
    )
    ap.add_argument(
        "--statid-col", help="Column name for stat id (aliases tried if omitted)"
    )
    ap.add_argument(
        "--value-col", help="Column name for count/value (aliases tried if omitted)"
    )
    ap.add_argument("--season-col", help="Column name for season (or provide --season)")
    ap.add_argument("--week-col", help="Column name for week (or provide --week)")
    # Constant overrides (if season/week not present in data)
    ap.add_argument("--season", type=int, help="Constant season to use if not in data")
    ap.add_argument("--week", type=int, help="Constant week to use if not in data")
    args = ap.parse_args(argv)

    fmt = args.format if args.format != "auto" else _auto_format(args.inp)
    df = _read_input(args.inp, fmt)

    # Pick columns (auto + override)
    player_col = args.player_col or _choose_first(
        df, ("player_id", "playerId", "athleteId", "athlete_id", "pid", "id")
    )
    statid_col = args.statid_col or _choose_first(
        df, ("statId", "stat_id", "stat", "sid")
    )
    value_col = args.value_col or _choose_first(df, ("value", "count", "qty", "amount"))
    season_col = args.season_col or _choose_first(df, ("season", "year"))
    week_col = args.week_col or _choose_first(df, ("week", "wk", "gameWeek"))

    # Validate essentials
    missing = []
    if not player_col:
        missing.append("player_id")
    if not statid_col:
        missing.append("statId")
    if not value_col:
        missing.append("value")
    if missing:
        raise SystemExit(
            f"Missing required columns (auto-detect failed): {missing}. "
            f"Use --player-col/--statid-col/--value-col to map."
        )

    out = pd.DataFrame()
    out["player_id"] = _coerce_numeric(df[player_col], "i")
    out["statId"] = _coerce_numeric(df[statid_col], "i")
    out["value"] = _coerce_numeric(df[value_col], "f")

    # season/week (prefer columns, else constants, else error)
    if season_col and season_col in df.columns:
        out["season"] = _coerce_numeric(df[season_col], "i")
    elif args.season is not None:
        out["season"] = int(args.season)
    else:
        raise SystemExit("season missing: provide --season-col or constant --season")

    if week_col and week_col in df.columns:
        out["week"] = _coerce_numeric(df[week_col], "i")
    elif args.week is not None:
        out["week"] = int(args.week)
    else:
        raise SystemExit("week missing: provide --week-col or constant --week")

    # Drop rows missing essentials after coercion, then aggregate duplicates
    out = out.dropna(subset=["season", "week", "player_id", "statId", "value"])
    out["season"] = out["season"].astype(int)
    out["week"] = out["week"].astype(int)
    out["player_id"] = out["player_id"].astype(int)
    out["statId"] = out["statId"].astype(int)
    out["value"] = out["value"].astype(float)

    grouped = (
        out.groupby(
            ["season", "week", "player_id", "statId"], dropna=False, as_index=False
        )["value"]
        .sum()
        .rename(columns={"value": "value"})
    )

    grouped.to_csv(args.out, index=False)
    print(
        json.dumps(
            {
                "ok": True,
                "rows_in": int(len(df)),
                "rows_out": int(len(grouped)),
                "out": args.out,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
