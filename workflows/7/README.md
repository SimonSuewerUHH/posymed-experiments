# Workflow 7 — cross-engine re-implementations

PoSyMed **Workflow 7** (Supplementary material 2, Table 5, ID 7) is a shared-preprocessing
pipeline with two clustering branches:

```
fetch (UCI 17) ─▶ one-hot ─▶ ┌─▶ Birch
                             └─▶ GaussianMixtureModel
```

To make the reviewer-requested comparison fair, the **per-step computation is held
constant**: every engine calls the *same* Python scripts in [`common/tools/`](common/tools),
which faithfully re-implement the corresponding PoSyMed apps
(`UciFetchToCsv`, `OneHotEncoding`, `Birch`, `GaussianMixtureModel`). Only the
*orchestration* differs between engines.

| Folder | Engine | Entry point |
|--------|--------|-------------|
| [`snakemake/`](snakemake) | Snakemake 9 | `Snakefile` (`snakemake --cores 2`) |
| [`nextflow/`](nextflow)   | Nextflow 26 (DSL2) | `main.nf` (`nextflow run main.nf`) |
| [`galaxy/`](galaxy)       | Galaxy (via planemo) | `workflow.gxwf.yml` + `tools/*.xml` |
| [`common/`](common)       | shared tool scripts + `environment.yml` | — |

## Reproduce

```bash
conda env create -f common/environment.yml && conda activate posymed-cmp
bash snakemake/run.sh      # or nextflow/run.sh, or galaxy/run.sh (needs planemo)
```

The UCI fetch uses `ucimlrepo` when online and otherwise falls back to the committed
`step-1/output/uci_dataset17.csv` (identical bytes), so the pipelines run offline too.

## Equivalence to PoSyMed (validation)

Each engine's outputs were compared to the committed PoSyMed run outputs
(`step-3/`, `step-4/`). Agreement is measured with the Adjusted Rand Index (ARI);
1.0 = identical clustering.

| Engine | Birch vs PoSyMed | GMM vs PoSyMed |
|--------|:---:|:---:|
| Snakemake | ARI = 1.000 | ARI = 1.000 |
| Nextflow  | ARI = 1.000 | ARI = 1.000 |
| Galaxy    | ARI = 1.000 | ARI = 1.000 |

The three engines also produce **byte-identical** label files to one another (Galaxy
via conda-resolved scikit-learn 1.5.2, the others via 1.9.0 — the clustering is
deterministic across both).
