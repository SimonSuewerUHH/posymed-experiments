# Workflow 12 — cross-engine re-implementations

PoSyMed **Workflow 12** (Supplementary material 2, Table 5, ID 12) is a
split / parallel-analysis / merge **DAG** (a "scatter-gather" topology):

```
fetch (UCI 17) ─▶ one-hot ─▶ train-test-split ─▶ ┌─▶ GMM(train) ─┐
                                                 └─▶ GMM(test)  ─┴─▶ merge (concat_columns)
```

As for Workflow 7, the **per-step computation is held constant**: every engine calls the
*same* Python scripts in [`common/tools/`](common/tools), which faithfully re-implement the
PoSyMed apps (`UciFetchToCsv`, `OneHotEncoding`, `train-test-split`,
`GaussianMixtureModel`, `Branch-Merge-Aggregator`). Only the orchestration differs.
This workflow is the more interesting comparison, because branch-and-merge is exactly
the pattern general-purpose workflow engines are built for.

| Folder | Engine | Entry point |
|--------|--------|-------------|
| [`snakemake/`](snakemake) | Snakemake 9 | `Snakefile` |
| [`nextflow/`](nextflow)   | Nextflow 26 (DSL2) | `main.nf` (scatter via channels) |
| [`galaxy/`](galaxy)       | Galaxy (via planemo) | `workflow.gxwf.yml` + `tools/*.xml` |
| [`common/`](common)       | shared tool scripts + `environment.yml` | — |

## Reproduce

```bash
conda env create -f common/environment.yml && conda activate posymed-cmp
bash snakemake/run.sh      # or nextflow/run.sh, or galaxy/run.sh (needs planemo)
```

## Equivalence to PoSyMed (validation)

Compared to the committed PoSyMed run outputs (`step-4/`, `step-5/`, `step-6/`):

| Engine | GMM(train) | GMM(test) | merged table |
|--------|:---:|:---:|:---:|
| Snakemake | ARI = 1.000 | ARI = 1.000 | identical (426 × 4) |
| Nextflow  | ARI = 1.000 | ARI = 1.000 | identical (426 × 4) |
| Galaxy    | ARI = 1.000 | ARI = 1.000 | identical (426 × 4) |

All three engines reproduce the exact `train`/`test` split (426 / 143 rows) and the exact
merged `concat_columns` table (`index_left,label_left,index_right,label_right`) — including
PoSyMed's NaN-padding of the shorter (test) branch.
