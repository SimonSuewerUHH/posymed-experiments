#!/usr/bin/env nextflow
// Nextflow (DSL2) re-implementation of PoSyMed Workflow 12

nextflow.enable.dsl = 2

params.tools    = "${projectDir}/../common/tools"
params.fallback = "${projectDir}/../step-1/output/uci_dataset17.csv"
params.gmm_args = "--n-components 3 --covariance-type full --tol 0.001 --reg-covar 0.000001 " +
                  "--max-iter 100 --n-init 1 --init-params kmeans --random-state 42 --standardize 1"

process FETCH {
    publishDir "results", mode: 'copy'
    output: path "dataset.csv"
    script: "python ${params.tools}/fetch.py --dataset-id 17 --out dataset.csv --fallback ${params.fallback}"
}

process ONEHOT {
    publishDir "results", mode: 'copy'
    input:  path dataset
    output: path "encoded.csv"
    script: "python ${params.tools}/onehot.py --in ${dataset} --out encoded.csv"
}

process SPLIT {
    publishDir "results", mode: 'copy'
    input:  path encoded
    output:
    path "train.csv"
    path "test.csv"
    script:
    """
    python ${params.tools}/split.py --in ${encoded} \
        --train-out train.csv --test-out test.csv \
        --test-size 0.25 --random-state 42 --shuffle 1
    """
}

process GMM {                         // one reusable GMM process, run once per branch
    tag "${split}"
    publishDir "results", mode: 'copy'
    input:
    tuple val(split), path(data)
    output:
    tuple val(split), path("gmm_${split}_labels.csv")
    script:
    """
    python ${params.tools}/gmm.py --in ${data} \
        --labels-out gmm_${split}_labels.csv \
        --responsibilities-out gmm_${split}_resp.csv --weights-out gmm_${split}_weights.csv \
        --means-out gmm_${split}_means.csv --covariances-out gmm_${split}_cov.csv \
        ${params.gmm_args}
    """
}

process MERGE {                       // PoSyMed app: Branch-Merge-Aggregator (concat_columns)
    publishDir "results", mode: 'copy'
    input:
    path left                         // gmm(test) labels  (shorter frame -> left, matches PoSyMed)
    path right                        // gmm(train) labels
    output: path "merged.csv"
    script:
    """
    python ${params.tools}/merge.py --left ${left} --right ${right} \
        --out merged.csv --mode concat_columns --how inner
    """
}

workflow {
    dataset = FETCH()
    encoded = ONEHOT(dataset)
    (train, test) = SPLIT(encoded)

    // scatter: run the same GMM process over both splits in parallel
    branches = train.map { t -> tuple('train', t) }
                    .mix( test.map { t -> tuple('test', t) } )
    labels = GMM(branches)

    // gather: route each branch's labels to the merge inputs by tag
    test_labels  = labels.filter { it[0] == 'test'  }.map { it[1] }
    train_labels = labels.filter { it[0] == 'train' }.map { it[1] }
    MERGE(test_labels, train_labels)
}
