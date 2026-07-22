#!/usr/bin/env python3
"""merge.py -- faithful re-implementation of the PoSyMed 'Branch-Merge-Aggregator' app.

Merges two branch outputs into one DataFrame. Modes mirror PoSyMed:
  - concat_columns : side-by-side concat (pd.concat axis=1); overlapping column
                     names get _left / _right suffixes; shorter frame NaN-padded.
  - concat_rows    : stacked concat (pd.concat axis=0) with an outer/inner join
                     on columns depending on `how`.
  - merge_on_key   : pd.merge(left, right, on=key, how=how).
Default: mode=concat_columns, how=inner.
"""
import argparse
import sys
import pandas as pd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--left", required=True)
    ap.add_argument("--right", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--mode", default="concat_columns",
                    choices=["concat_columns", "concat_rows", "merge_on_key"])
    ap.add_argument("--key", default="")
    ap.add_argument("--how", default="inner",
                    choices=["inner", "left", "right", "outer"])
    args = ap.parse_args()

    left = pd.read_csv(args.left)
    right = pd.read_csv(args.right)

    if args.mode == "concat_columns":
        overlap = set(left.columns) & set(right.columns)
        left = left.rename(columns={c: f"{c}_left" for c in overlap})
        right = right.rename(columns={c: f"{c}_right" for c in overlap})
        out = pd.concat([left.reset_index(drop=True),
                         right.reset_index(drop=True)], axis=1)
    elif args.mode == "concat_rows":
        join = "inner" if args.how == "inner" else "outer"
        out = pd.concat([left, right], axis=0, join=join, ignore_index=True)
    else:  # merge_on_key
        out = pd.merge(left, right, on=args.key, how=args.how)

    out.to_csv(args.out, index=False)
    sys.stderr.write(f"[merge] mode={args.mode} -> "
                     f"{out.shape[0]} rows x {out.shape[1]} cols -> {args.out}\n")


if __name__ == "__main__":
    main()
