#!/usr/bin/env nextflow
// Nextflow (DSL2) re-implementation of PoSyMed Workflow 7
// (Supplementary material 2, Table 5, ID 7):
//
//   fetch (UCI 17) --> one-hot --> [ Birch , GaussianMixtureModel ]
//
// The per-step computation is delegated to the SAME Python tools used by the
// Snakemake and Galaxy re-implementations (../common/tools/*.py). Only the
// orchestration differs.

nextflow.enable.dsl = 2

params.tools    = "${projectDir}/../common/tools"
params.fallback = "${projectDir}/../step-1/output/uci_dataset17.csv"   // offline fallback

process FETCH {                       // PoSyMed app: UciFetchToCsv
    publishDir "results", mode: 'copy'
    output:
    path "dataset.csv"
    script:
    """
    python ${params.tools}/fetch.py --dataset-id 17 --out dataset.csv --fallback ${params.fallback}
    """
}

process ONEHOT {                      // PoSyMed app: OneHotEncoding
    publishDir "results", mode: 'copy'
    input:
    path dataset
    output:
    path "encoded.csv"
    script:
    """
    python ${params.tools}/onehot.py --in ${dataset} --out encoded.csv
    """
}

process BIRCH {                       // PoSyMed app: Birch
    publishDir "results", mode: 'copy'
    input:
    path encoded
    output:
    path "birch_labels.csv"
    path "birch_centers.csv"
    script:
    """
    python ${params.tools}/birch.py --in ${encoded} \
        --labels-out birch_labels.csv --centers-out birch_centers.csv \
        --threshold 0.5 --branching-factor 50 --n-clusters 3 --standardize 1
    """
}

process GMM {                         // PoSyMed app: GaussianMixtureModel
    publishDir "results", mode: 'copy'
    input:
    path encoded
    output:
    path "gmm_labels.csv"
    path "gmm_responsibilities.csv"
    path "gmm_weights.csv"
    path "gmm_means.csv"
    path "gmm_covariances.csv"
    script:
    """
    python ${params.tools}/gmm.py --in ${encoded} \
        --labels-out gmm_labels.csv --responsibilities-out gmm_responsibilities.csv \
        --weights-out gmm_weights.csv --means-out gmm_means.csv \
        --covariances-out gmm_covariances.csv \
        --n-components 3 --covariance-type full --tol 0.001 --reg-covar 0.000001 \
        --max-iter 100 --n-init 1 --init-params kmeans --random-state 42 --standardize 1
    """
}

workflow {
    dataset = FETCH()
    encoded = ONEHOT(dataset)
    BIRCH(encoded)                    // shared input -> two parallel branches
    GMM(encoded)
}
