from __future__ import annotations

import argparse
import json
from typing import Iterable, Optional, Sequence

import pandas as pd


REQUIRED_SIDS_DEFAULT = [210, 211, 212, 213, 216, 217, 218, 219]


def _parse_overrides(x: object) -> dict:
    """
    pointsOverrides is usually a JSON object mapping slotId->points.
    Handle blanks/NaN/empty gracefully.
    """
    if x is None:
        return {}
    if isinstance(x, dict):
        return x
    s = str(x).strip()
    if not s or s.lower() in {"nan", "none"}:
        return {}
    try:
        return json.loads(s)
    except Exception:
        # If it's malformed, treat as missing overrides
        return {}


def _missing_required_slot17(
    df: pd.DataFrame, required_sids: Iterable[int]
) -> list[int]:
    df = df.copy()
    if "statId" not in df.columns:
        # if statId column missing entirely, all required are "missing"
        return sorted(set(required_sids))

    # limit to rows we care about
    sub = df[df["statId"].isin(required_sids)].copy()
    if sub.empty:
        return sorted(set(required_sids))

    # parse overrides and check for "17"
    sub["__ov"] = sub.get("pointsOverrides", "").map(_parse_overrides)
    has17 = sub["__ov"].map(lambda d: "17" in d or 17 in d)
    present = set(sub.loc[has17, "statId"].astype(int).tolist())
    missing = sorted(set(int(s) for s in required_sids if int(s) not in present))
    return missing


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="QC gate: ensure slot-17 overrides exist for key IDP statIds."
    )
    ap.add_argument("--scoring", required=True, help="Path to scoring table CSV")
    ap.add_argument(
        "--required",
        help="Comma-separated list of required statIds (default: common IDP set)",
        default=",".join(str(s) for s in REQUIRED_SIDS_DEFAULT),
    )
    args = ap.parse_args(argv)

    # resolve required list
    required = [int(s.strip()) for s in str(args.required).split(",") if s.strip()]

    # load scoring
    try:
        df = pd.read_csv(args.scoring)
    except FileNotFoundError:
        print(f"❌ scoring file not found: {args.scoring}")
        return 2

    # check
    missing = _missing_required_slot17(df, required)
    if missing:
        print(
            f"❌ IDP QC FAILED: missing slot-17 overrides for statIds {missing}. "
            f"Add per-slot weights in 'pointsOverrides' (e.g. {{'17': 1.0}})."
        )
        return 3

    print(f"✅ IDP QC OK: all required statIds present ({required})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
