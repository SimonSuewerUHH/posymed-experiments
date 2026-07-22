#!/usr/bin/env python3
"""split.py -- faithful re-implementation of the PoSyMed 'train-test-split' app.

Wraps scikit-learn train_test_split. Mirrors PoSyMed defaults:
  shuffle=1, test_size=0.25, random_state=42.
Outputs train.csv and test.csv (row indices preserved as in PoSyMed).
"""
import argparse
import sys
import pandas as pd
from sklearn.model_selection import train_test_split


def _truthy(v):
    return str(v).strip().lower() in {"1", "true", "yes", "y", "t"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--train-out", required=True)
    ap.add_argument("--test-out", required=True)
    ap.add_argument("--test-size", type=float, default=0.25)
    ap.add_argument("--random-state", type=int, default=42)
    ap.add_argument("--shuffle", default="1")
    args = ap.parse_args()

    df = pd.read_csv(args.inp)
    train, test = train_test_split(
        df, test_size=args.test_size, random_state=args.random_state,
        shuffle=_truthy(args.shuffle),
    )
    train.to_csv(args.train_out, index=False)
    test.to_csv(args.test_out, index=False)
    sys.stderr.write(f"[split] {len(df)} -> train={len(train)} test={len(test)}\n")


if __name__ == "__main__":
    main()
