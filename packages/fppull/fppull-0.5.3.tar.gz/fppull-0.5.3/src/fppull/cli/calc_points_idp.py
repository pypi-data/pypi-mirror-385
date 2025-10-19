from __future__ import annotations
import argparse
import json
import pandas as pd
from fppull.idp.points import compute_idp_points


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Compute IDP fantasy points from normalized stat rows."
    )
    ap.add_argument(
        "--input",
        required=True,
        help="CSV with IDP stat rows (season, week, player_id, statId, value).",
    )
    ap.add_argument(
        "--scoring", required=True, help="CSV scoring table (from fetch_espn_scoring)."
    )
    ap.add_argument(
        "--out", required=True, help="Output CSV with per-player/week points."
    )
    ap.add_argument("--stat-id-col", default="statId")
    ap.add_argument("--value-col", default="value")
    args = ap.parse_args(argv)

    stats = pd.read_csv(args.input)
    scoring = pd.read_csv(args.scoring)

    out = compute_idp_points(
        stats,
        scoring,
        stat_id_col=args.stat_id_col,
        value_col=args.value_col,
    )
    out.to_csv(args.out, index=False)
    print(
        json.dumps(
            {
                "ok": True,
                "rows_out": int(out.shape[0]),
                "out": args.out,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
