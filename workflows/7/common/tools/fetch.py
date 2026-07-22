#!/usr/bin/env python3
"""fetch.py -- faithful re-implementation of the PoSyMed 'UciFetchToCsv' app.

Fetches a UCI ML Repository dataset by numeric id via ucimlrepo and exports a
single combined CSV (features + targets), mirroring the PoSyMed tool exactly:
  - ds.data.features  -> feature matrix X
  - ds.data.targets   -> target(s) y
  - horizontal (column-wise) concat into one flat table
  - overlapping target column names are prefixed with ':_'

The tool logic is identical for every engine (Snakemake / Nextflow / Galaxy);
only the *orchestration* around it differs. That is the point of the comparison.
"""
import argparse
import sys
import pandas as pd


def _as_frame(obj):
    if obj is None:
        return None
    if isinstance(obj, pd.Series):
        return obj.to_frame()
    return obj


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset-id", type=int, default=17,
                    help="UCI dataset id (17 = Breast Cancer Wisconsin Diagnostic)")
    ap.add_argument("--out", required=True, help="output CSV path")
    ap.add_argument("--fallback", default=None,
                    help="local CSV to use if the network fetch fails (keeps the "
                         "pipeline runnable offline with the identical input)")
    args = ap.parse_args()

    df = None
    try:
        from ucimlrepo import fetch_ucirepo
        ds = fetch_ucirepo(id=args.dataset_id)
        X = _as_frame(ds.data.features)
        y = _as_frame(ds.data.targets)
        if X is not None and y is not None:
            overlap = set(X.columns) & set(y.columns)
            if overlap:
                y = y.rename(columns={c: f":_{c}" for c in overlap})
            df = pd.concat([X.reset_index(drop=True), y.reset_index(drop=True)], axis=1)
        elif X is not None:
            df = X
        elif y is not None:
            df = y
        else:
            raise ValueError("dataset provides neither features nor targets")
    except Exception as exc:  # noqa: BLE001
        if args.fallback:
            sys.stderr.write(f"[fetch] network fetch failed ({exc}); "
                             f"using fallback {args.fallback}\n")
            df = pd.read_csv(args.fallback)
        else:
            raise

    df.to_csv(args.out, index=False)
    sys.stderr.write(f"[fetch] dataset_id={args.dataset_id} -> {df.shape[0]} rows x "
                     f"{df.shape[1]} cols -> {args.out}\n")


if __name__ == "__main__":
    main()
