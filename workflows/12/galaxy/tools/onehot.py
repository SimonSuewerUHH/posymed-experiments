#!/usr/bin/env python3
"""onehot.py -- faithful re-implementation of the PoSyMed 'OneHotEncoding' app.

pandas-only one-hot encoding (pandas.get_dummies). Mirrors the PoSyMed defaults:
  drop_first=0, keep_original=0, bool_to_number=1, columns="", dummy_na=0,
  prefix_sep="__". If the first column is named 'id' (case-insensitive) it is
  preserved as an identifier and kept first.
"""
import argparse
import sys
import pandas as pd


def _truthy(v):
    return str(v).strip().lower() in {"1", "true", "yes", "y", "t"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--columns", default="")
    ap.add_argument("--drop-first", default="0")
    ap.add_argument("--bool-to-number", default="1")
    ap.add_argument("--dummy-na", default="0")
    ap.add_argument("--keep-original", default="0")
    ap.add_argument("--prefix-sep", default="__")
    args = ap.parse_args()

    drop_first = _truthy(args.drop_first)
    bool_to_number = _truthy(args.bool_to_number)
    dummy_na = _truthy(args.dummy_na)
    keep_original = _truthy(args.keep_original)

    df = pd.read_csv(args.inp)

    id_col = None
    if len(df.columns) and str(df.columns[0]).lower() == "id":
        id_col = df.columns[0]
        ids = df[[id_col]]
        df = df.drop(columns=[id_col])

    # bool -> numeric 0/1 (before encoding), if requested
    if bool_to_number:
        for c in df.columns:
            if df[c].dtype == bool:
                df[c] = df[c].astype(int)

    if args.columns.strip():
        cols = [c.strip() for c in args.columns.split(",") if c.strip()]
    else:
        # auto-detect categorical columns (object / string / category dtypes).
        # Robust across pandas versions incl. pandas 3.0 'str' dtype.
        cols = [c for c in df.columns
                if not pd.api.types.is_numeric_dtype(df[c])
                and not pd.api.types.is_bool_dtype(df[c])]
        if not bool_to_number:
            cols += [c for c in df.columns
                     if pd.api.types.is_bool_dtype(df[c]) and c not in cols]

    encoded = pd.get_dummies(
        df, columns=cols, prefix_sep=args.prefix_sep,
        drop_first=drop_first, dummy_na=dummy_na, dtype=int,
    )

    if keep_original and cols:
        encoded = pd.concat([df[cols], encoded], axis=1)

    if id_col is not None:
        encoded = pd.concat([ids.reset_index(drop=True),
                             encoded.reset_index(drop=True)], axis=1)

    encoded.to_csv(args.out, index=False)
    sys.stderr.write(f"[onehot] encoded {len(cols)} col(s) -> "
                     f"{encoded.shape[0]} rows x {encoded.shape[1]} cols -> {args.out}\n")


if __name__ == "__main__":
    main()
