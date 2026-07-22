#!/usr/bin/env python3
"""birch.py -- faithful re-implementation of the PoSyMed 'Birch' app.

Scalable clustering with scikit-learn BIRCH (CF tree). Mirrors PoSyMed defaults:
  threshold=0.5, branching_factor=50, use_global_clustering=1, n_clusters=3,
  compute_labels=1, standardize=1. Numeric columns only are used; when
  standardize=1 a StandardScaler is applied before fitting.

Outputs: labels.csv (index,label) and subcluster_centers.csv.
"""
import argparse
import sys
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import Birch


def _truthy(v):
    return str(v).strip().lower() in {"1", "true", "yes", "y", "t"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--labels-out", required=True)
    ap.add_argument("--centers-out", required=True)
    ap.add_argument("--threshold", type=float, default=0.5)
    ap.add_argument("--branching-factor", type=int, default=50)
    ap.add_argument("--use-global-clustering", default="1")
    ap.add_argument("--n-clusters", type=int, default=3)
    ap.add_argument("--standardize", default="1")
    args = ap.parse_args()

    df = pd.read_csv(args.inp)
    X = df.select_dtypes(include="number")

    if _truthy(args.standardize):
        X = StandardScaler().fit_transform(X)
    else:
        X = X.values

    n_clusters = args.n_clusters if _truthy(args.use_global_clustering) else None
    model = Birch(threshold=args.threshold, branching_factor=args.branching_factor,
                  n_clusters=n_clusters, compute_labels=True)
    labels = model.fit_predict(X)

    pd.DataFrame({"index": range(len(labels)), "label": labels}).to_csv(
        args.labels_out, index=False)
    pd.DataFrame(model.subcluster_centers_).to_csv(args.centers_out, index=False)
    sys.stderr.write(f"[birch] {len(labels)} samples -> "
                     f"{len(set(labels))} clusters -> {args.labels_out}\n")


if __name__ == "__main__":
    main()
