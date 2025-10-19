from __future__ import annotations
import argparse
import json
import pandas as pd


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Merge IDP default weights into ESPN scoring_table.csv if missing."
    )
    ap.add_argument(
        "--in", dest="inp", required=True, help="Path to ESPN scoring_table.csv"
    )
    ap.add_argument(
        "--defaults", required=True, help="CSV with columns: statId,idp_points"
    )
    ap.add_argument("--out", required=True, help="Output merged scoring CSV")
    args = ap.parse_args(argv)

    base = pd.read_csv(args.inp)
    defs = pd.read_csv(args.defaults, comment="#").rename(columns=str.strip)

    # Normalize columns
    if "statId" not in defs.columns or "idp_points" not in defs.columns:
        raise SystemExit("defaults CSV must have columns: statId,idp_points")

    base_ids = set(base.get("statId", []))
    rows = []
    for _, r in defs.iterrows():
        sid = int(r["statId"])
        if sid in base_ids:
            # Keep ESPN-provided rows as-is
            continue
        # Create a synthetic row with slot-17 override so our IDP engine picks it up
        rows.append(
            {
                "statId": sid,
                "points": 0.0,
                "pointsOverrides": json.dumps({"17": float(r["idp_points"])}),
            }
        )

    add_df = pd.DataFrame(rows, columns=["statId", "points", "pointsOverrides"])
    merged = pd.concat([base, add_df], ignore_index=True)
    merged.to_csv(args.out, index=False)
    print(f"✅ wrote merged scoring to {args.out} (added {len(rows)} IDP rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
