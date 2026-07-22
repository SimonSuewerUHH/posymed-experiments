#!/usr/bin/env python3
"""gmm.py -- faithful re-implementation of the PoSyMed 'GaussianMixtureModel' app.

Probabilistic clustering with scikit-learn Gaussian Mixture Models (EM).
Mirrors PoSyMed defaults: n_components=3, covariance_type=full, tol=1e-3,
reg_covar=1e-6, max_iter=100, n_init=1, init_params=kmeans, random_state=42,
warm_start=0, standardize=1, output_probabilities=1.

Outputs: labels.csv (index,label), responsibilities.csv, weights.csv,
means.csv, covariances.csv.
"""
import argparse
import sys
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.mixture import GaussianMixture


def _truthy(v):
    return str(v).strip().lower() in {"1", "true", "yes", "y", "t"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--labels-out", required=True)
    ap.add_argument("--responsibilities-out", required=True)
    ap.add_argument("--weights-out", required=True)
    ap.add_argument("--means-out", required=True)
    ap.add_argument("--covariances-out", required=True)
    ap.add_argument("--n-components", type=int, default=3)
    ap.add_argument("--covariance-type", default="full")
    ap.add_argument("--tol", type=float, default=1e-3)
    ap.add_argument("--reg-covar", type=float, default=1e-6)
    ap.add_argument("--max-iter", type=int, default=100)
    ap.add_argument("--n-init", type=int, default=1)
    ap.add_argument("--init-params", default="kmeans")
    ap.add_argument("--random-state", type=int, default=42)
    ap.add_argument("--standardize", default="1")
    args = ap.parse_args()

    df = pd.read_csv(args.inp)
    X = df.select_dtypes(include="number")
    if _truthy(args.standardize):
        X = StandardScaler().fit_transform(X)
    else:
        X = X.values

    model = GaussianMixture(
        n_components=args.n_components, covariance_type=args.covariance_type,
        tol=args.tol, reg_covar=args.reg_covar, max_iter=args.max_iter,
        n_init=args.n_init, init_params=args.init_params,
        random_state=args.random_state,
    )
    labels = model.fit_predict(X)
    resp = model.predict_proba(X)

    pd.DataFrame({"index": range(len(labels)), "label": labels}).to_csv(
        args.labels_out, index=False)
    pd.DataFrame(resp).to_csv(args.responsibilities_out, index=False)
    pd.DataFrame({"weight": model.weights_}).to_csv(args.weights_out, index=False)
    pd.DataFrame(model.means_).to_csv(args.means_out, index=False)
    # covariances -> flatten to 2D for CSV export
    cov = np.asarray(model.covariances_)
    pd.DataFrame(cov.reshape(cov.shape[0], -1)).to_csv(args.covariances_out, index=False)
    sys.stderr.write(f"[gmm] {len(labels)} samples -> "
                     f"{args.n_components} components -> {args.labels_out}\n")


if __name__ == "__main__":
    main()
