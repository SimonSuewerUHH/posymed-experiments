# Response to Reviewer — comments 2 and 5

We thank the reviewer for these constructive suggestions. Both have led to a new supplementary
section and a set of fully runnable, independently reproducible artifacts in the repository
(`posymed-experiments/workflows/`). We respond to each comment below.

---

## Comment 2

> *The workflow evaluation is helpful, but it is mostly limited to showing that workflows can be
> built and executed within PoSyMed. I would suggest adding at least one comparison with an
> existing workflow platform, such as Galaxy, Nextflow, or Snakemake, using the same or a similar
> workflow. This would make it easier to understand the practical advantage of PoSyMed.*

We agree, and we have added a direct, executed comparison. Rather than a single platform, we
re-implemented **two of the evaluated PoSyMed workflows in all three engines the reviewer names —
Snakemake, Nextflow and Galaxy — and ran every port end-to-end**. This is described in the new
**Supplementary material — "Comparison with established workflow engines"** (Part A), with all
code and outputs in `workflows/{7,12}/{snakemake,nextflow,galaxy,common}/`.

**Which workflows and why.** We chose two workflows that bracket the space of orchestration
patterns while using the same real biomedical dataset as the paper (Breast Cancer Wisconsin,
UCI ID 17):

- **Workflow 7** (Table 5, ID 7) — a linear pipeline with a shared-input fan-out
  (`fetch → one-hot → {Birch, GaussianMixtureModel}`); the fairest baseline for "can the other
  engine express the same analysis?".
- **Workflow 12** (Table 5, ID 12) — a **branch-and-merge DAG**
  (`fetch → one-hot → train/test-split → {GMM(train), GMM(test)} → merge`); scatter-gather is
  precisely the pattern general-purpose engines are engineered for, and therefore the most
  informative point of comparison.

**Design.** To compare *platforms* fairly we held the *computation* constant: the per-step logic
is implemented once (faithful re-implementations of the PoSyMed apps, same libraries and
hyperparameters) and called identically by all three engines; only the orchestration differs.

**Result 1 — analytical equivalence.** Every port reproduces PoSyMed's committed outputs
**exactly**: Adjusted Rand Index = 1.000 for all clustering steps in both workflows, and the
merged branch-and-merge table is identical. The three engines are additionally byte-identical to
one another (Galaxy executed on a real, ephemeral Galaxy server via planemo). This establishes
that the ports differ only in orchestration, not in results.

**Result 2 — the practical advantage, made concrete.** Because the results are identical, the
advantage lies in the *cost of expressing and operating* the same workflow, which we quantify in
the supplement. Reproducing Workflow 12 required, respectively: a Groovy DSL with explicit channel
scatter/gather (Nextflow, ~78 code lines + config + JVM runtime); a rule graph with manual filename
wiring (Snakemake, ~52 code lines + conda env); or five per-tool XML wrappers plus a workflow
document that must be linted and installed into a Galaxy server (~182 XML + 77 workflow lines +
a running instance). In PoSyMed the same six-step analysis is assembled from six catalog apps with
typed ports that auto-connect and validate at design time — **no orchestration code and no runtime
to operate** — and, as described in the main text, can be composed with LLM assistance. We also note
explicitly that Nextflow/Snakemake retain their advantages for HPC/cloud scaling and Galaxy for its
public tool ecosystem; PoSyMed's contribution is to make the *same governed biomedical analysis
composable by a non-programmer* while producing identical output.

---

## Comment 5

> *It would be useful to clarify how representative the selected tools and workflows are of real
> biomedical analysis tasks. The examples are helpful, but it is not fully clear whether they
> reflect typical end-user workflows or mainly serve as proof-of-concept demonstrations.*

We have added **Part B — "Representativeness of the evaluated tools and workflows"** to the same
supplement, and we clarify the point directly: the evaluation deliberately contains **both**
proof-of-concept and typical-end-user components, for complementary reasons.

1. **The tool catalog is built from established, peer-reviewed biomedical methods.** Beyond the
   generic ML utilities, PoSyMed integrates independently published, in-use systems-medicine tools
   that perform exactly the tasks biomedical end-users perform: **UnPaSt** (patient stratification
   by biclustering of omics data), **DysRegNet** (patient-specific, confounder-aware dysregulated
   network inference across 11 TCGA cancers), **Spycone** (splicing-aware time-course
   transcriptomics), **MoSBi** (automated molecular stratification/subtyping, PNAS 2022),
   **BiCoN** (network-constrained biclustering of patient subgroups), **SCANet** (single-cell
   RNA-seq analysis and co-expression networks), and **MOFA+** (multi-omics/multi-modal single-cell
   factor analysis). Full citations are given in the supplement.

2. **The datasets are standard biomedical benchmarks and real disease cohorts** — Breast Cancer
   Wisconsin (clinical tabular benchmark), GSE30219 (Non-Small-Cell Lung Cancer, GEO), PBMC 3k
   (the canonical 10x single-cell reference), plus TCGA-derived / BioGRID interaction data and
   time-course expression matrices — rather than synthetic-only inputs.

3. **We now state the roles of the two workflow families explicitly.** The numbered ML workflows
   (WF 1–12) use *deterministic, generic* building blocks on purpose: their role is to
   **stress and verify the orchestration engine** (linear chains, fan-out, branch-and-merge DAGs)
   with exactly reproducible, independently checkable runs — as demonstrated in Part A. They are
   proof-of-concept for orchestration, not novel biomedical analyses. The domain tools in (1), run
   on the datasets in (2) (Table 4), are representative of *typical end-user tasks* — patient
   stratification, subnetwork/biomarker discovery, single-cell characterization, multi-omics
   integration.

4. **Limitations, stated honestly.** The workflows demonstrate that these representative tools can
   be *composed and executed* within PoSyMed; we do not claim to reproduce a specific published
   biomedical *finding* end-to-end, and the ML-utility workflows are proof-of-concept for
   orchestration rather than clinical analyses in themselves. The representativeness argument rests
   on the catalog being assembled from independently published, in-use biomedical methods and on the
   inputs being standard benchmarks and real disease cohorts, while the deterministic ML workflows
   provide the controllable backbone needed to evaluate the orchestration layer itself.

---

All artifacts supporting this response are in `posymed-experiments/workflows/`
(see `supplementary_material_engine_comparison.md` and the per-workflow `README.md` files) and can
be reproduced with a single conda environment plus `planemo` for the Galaxy ports.
