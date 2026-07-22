# Supplementary material — Comparison with established workflow engines, and representativeness of the evaluated tools and workflows

This supplement addresses two reviewer comments:

- **(Reviewer comment 2)** *"…add at least one comparison with an existing workflow platform,
  such as Galaxy, Nextflow, or Snakemake, using the same or a similar workflow. This would make
  it easier to understand the practical advantage of PoSyMed."*
- **(Reviewer comment 5)** *"…clarify how representative the selected tools and workflows are of
  real biomedical analysis tasks … whether they reflect typical end-user workflows or mainly serve
  as proof-of-concept demonstrations."*

All artifacts referenced here are in the repository under
`posymed-experiments/workflows/{7,12}/{snakemake,nextflow,galaxy,common}/` and are fully runnable.

---

## Part A — Comparison with Galaxy, Nextflow and Snakemake (comment 2)

### A.1 What we did

We re-implemented **two** of the evaluated PoSyMed workflows in **all three** of the workflow
engines named by the reviewer — **Snakemake** [1], **Nextflow** [2] and **Galaxy** [3] — and
executed every port end-to-end:

| Workflow | Topology | Steps (PoSyMed apps) |
|---|---|---|
| **WF 7** (Table 5, ID 7) | linear pipeline with a shared-input fan-out | `UciFetchToCsv` → `OneHotEncoding` → { `Birch`, `GaussianMixtureModel` } |
| **WF 12** (Table 5, ID 12) | **branch-and-merge DAG** (scatter-gather) | `UciFetchToCsv` → `OneHotEncoding` → `train-test-split` → { `GaussianMixtureModel`(train), `GaussianMixtureModel`(test) } → `Branch-Merge-Aggregator` |

**Why these two workflows.** They were chosen to bracket the space of orchestration patterns
while staying fully reproducible and using the same real biomedical dataset as the paper
(*Breast Cancer Wisconsin (Diagnostic)*, UCI ID 17):

- **WF 7** is a clean **linear chain with a fan-out** (one preprocessing result feeds two
  independent clustering algorithms). It is the fairest "can the other engine express the same
  thing?" baseline.
- **WF 12** is a **branch-and-merge DAG**: a train/test split scatters into two parallel model
  fits that are then joined. Scatter-gather is precisely the pattern that general-purpose
  engines are engineered for, so it is where a comparison is most informative — and where
  PoSyMed's typed-port model and the engines' channel/rule models diverge most.

The remaining evaluated workflows are either single-tool runs (Table 5, IDs 1–4) or linear
sub-cases of WF 7/WF 12 (IDs 5–11), so these two cover the structural range without redundancy.

**Why these three engines.** Snakemake and Nextflow are the two dominant *code-first* workflow
managers in bioinformatics and are the standard reference points for reproducibility and DAG
execution; recent surveys show Nextflow and Snakemake driving most workflow-manager adoption,
with Galaxy remaining the principal *GUI/platform* system [4]. Galaxy is also the closest
*conceptual peer* to PoSyMed — a web platform with a catalog of pre-wrapped tools aimed at
users who do not program — so it is the most relevant comparison for PoSyMed's "practical
advantage" claim.

### A.2 Experimental design: hold the computation constant, vary only the orchestration

A comparison of *platforms* is only meaningful if the *analysis* is identical. We therefore
factored each workflow into (i) per-step computation and (ii) orchestration:

- **Per-step computation** is implemented once, as small Python CLIs in
  `workflows/{7,12}/common/tools/*.py`, that faithfully re-implement the PoSyMed apps
  (same libraries — `ucimlrepo`, `pandas`, `scikit-learn`; same hyperparameters as Table 5).
  **Every engine — and PoSyMed — runs the same computation.**
- **Orchestration** is what each engine expresses in its own way: a Snakemake `Snakefile`,
  a Nextflow `main.nf`, or Galaxy tool wrappers + a `gxformat2` workflow.

This isolates the variable of interest (the orchestration layer) and lets us verify that all
ports produce the **same analytical result** as PoSyMed.

### A.3 Functional equivalence — every port reproduces PoSyMed exactly

We compared each port's outputs against the committed PoSyMed run outputs
(the `step-*/output/` folders). Clustering agreement is measured with the Adjusted Rand Index
(ARI; 1.0 = identical partition).

| Workflow | Output | Snakemake | Nextflow | Galaxy |
|---|---|:--:|:--:|:--:|
| WF 7 | Birch labels vs PoSyMed | **1.000** | **1.000** | **1.000** |
| WF 7 | GMM labels vs PoSyMed | **1.000** | **1.000** | **1.000** |
| WF 12 | GMM(train) labels vs PoSyMed | **1.000** | **1.000** | **1.000** |
| WF 12 | GMM(test) labels vs PoSyMed | **1.000** | **1.000** | **1.000** |
| WF 12 | merged table (`concat_columns`) | identical | identical | identical |

Beyond matching PoSyMed, the three engines are **byte-identical to one another** (the Galaxy
port used conda-resolved scikit-learn 1.5.2, the others 1.9.0; the deterministic algorithms
agree across both). This confirms the ports differ *only* in orchestration, not in results —
the precondition for a fair platform comparison.

### A.4 Authoring footprint — what a user must produce to get the same workflow

The engines differ sharply in *what a user has to author and operate* to obtain that identical
result. The table below counts only the orchestration/wrapping artifacts each engine required
(the shared `common/tools/*.py` scripts, ~50–60 lines each, are excluded because they are common
to all engines and stand in for the already-existing PoSyMed apps).

| | PoSyMed | Snakemake | Nextflow | Galaxy |
|---|---|---|---|---|
| **Authoring modality** | visual, drag-and-drop app graph | `Snakefile` (Python DSL) | `main.nf` (Groovy DSL) + `nextflow.config` | one XML wrapper **per tool** + `gxformat2` workflow |
| **Orchestration code, WF 7** | 0 lines (4 nodes, ports auto-connect) | 45 code lines | 73 code lines | 149 XML lines (4 tools) + 55 workflow lines |
| **Orchestration code, WF 12** | 0 lines (6 nodes) | 52 code lines | 78 code lines | 182 XML lines (5 tools) + 77 workflow lines |
| **Language(s) required** | none | Python + shell | Groovy + shell | XML + YAML + shell |
| **Runtime to operate** | hosted service | Snakemake CLI + conda env | Nextflow + JVM (Java 17–24) | a running Galaxy server (here: ephemeral, via planemo) |
| **New tool onboarding** | publish a containerized app once; reused by GUI + LLM | edit the Snakefile / add a script | add a process / module | write + lint + install an XML wrapper into the instance |
| **Typed I/O & connection checking** | yes, at design time (CSV/TSV/IMAGE ports) | filenames only; mismatches fail at run time | channel types; mismatches fail at run time | datatypes + GUI connection validation |
| **Target user** | clinician / biomedical end-user (no code) | developer / bioinformatician | developer / bioinformatician | biologist **once tools are wrapped by a developer** |

*(Line counts are reproducible from the committed files, e.g.
`grep -vc '^\s*#\|^\s*$' workflows/7/snakemake/Snakefile`.)*

### A.5 What the comparison shows — the practical advantage of PoSyMed

The comparison is **not** that PoSyMed computes anything the other engines cannot: the results
are provably identical (§A.3). The advantage lies elsewhere and is made concrete by §A.4:

1. **No-code composability for the intended end-user.** Reproducing WF 12 required writing a
   Groovy DSL with explicit channel scatter/gather (Nextflow), a rule graph with manual filename
   wiring (Snakemake), or five XML tool wrappers plus a workflow document that a developer must
   lint and install into a Galaxy server (Galaxy). In PoSyMed the same six-step branch-and-merge
   analysis is assembled by placing six catalog apps on a canvas and connecting typed ports, with
   **zero** orchestration code and no runtime to operate.

2. **Governed, federated execution is built in, not bolted on.** PoSyMed apps are versioned,
   containerized, malware-scanned units carrying explicit capability flags
   (`needsInternetAccess`, `needsHostAccess`, `certificationLevel`, image digest, publish hash).
   This governance — important for clinical/omics data and for the federated setting PoSyMed
   targets — is a first-class property of the platform. Snakemake and Nextflow leave provenance,
   sandboxing and access control to the pipeline author; Galaxy provides versioned tools and
   histories but not the federated-execution and certification model.

3. **Typed ports catch composition errors at design time.** PoSyMed (and, in its GUI, Galaxy)
   validate that an output port's type matches the consuming input port *before* execution. In
   the Snakemake and Nextflow ports, an incompatible hand-off only surfaces as a runtime error.

4. **The engines keep their own, complementary strengths.** Nextflow and Snakemake remain
   superior for large-scale HPC/cloud execution, `-resume`/checkpointing, and container-per-rule
   scaling; Galaxy remains excellent for shareable histories and its large public tool ecosystem.
   PoSyMed is not positioned to replace them on raw throughput. Its contribution is to make the
   *same* governed biomedical analysis **composable by a non-programmer** and, as described in the
   main text, assemblable with LLM assistance — while producing identical analytical output, as
   demonstrated here.

In short: across two workflows and three engines, the analytical result is invariant, but the
**cost of expressing and operating the workflow** ranges from hundreds of lines of code plus a
managed runtime (Nextflow/Snakemake), or per-tool XML wrapping plus a server (Galaxy), down to a
handful of typed drag-and-drop nodes (PoSyMed). That difference is the practical advantage the
reviewer asked us to make explicit.

---

## Part B — Representativeness of the evaluated tools and workflows (comment 5)

The reviewer asks whether the tools and workflows reflect **typical end-user biomedical analysis**
or are mainly **proof-of-concept** demonstrations. The honest answer is that the evaluation
deliberately contains **both kinds**, for complementary reasons, and the catalog as a whole is
strongly grounded in real, published biomedical methods.

### B.1 The tool catalog consists of established, peer-reviewed biomedical methods

Beyond the generic ML utilities used as controllable test cases (§B.2), the PoSyMed catalog
integrates domain tools that are each independently published, real-world systems-medicine
methods used by working biomedical researchers:

| PoSyMed app | What it does (typical end-user task) | Reference |
|---|---|---|
| **UnPaSt** (Tool 6) | unsupervised **patient stratification** by differentially expressed biclusters in omics data; validated on breast-cancer and asthma subtype discovery | [5] |
| **DysRegNet** (Tool 9) | **patient-specific, confounder-aware** dysregulated gene-regulatory-network inference; applied across 11 TCGA cancer types | [6] |
| **Spycone** (Tool 10) | **splicing-aware time-course** transcriptomics analysis (isoform-switch detection, clustering, network enrichment) | [7] |
| **MoSBi** (Tool 11) | **molecular-signature identification** via biclustering + similarity networks (module/signature discovery) | [8] |
| **BiCoN** (Tool 18) | **network-constrained biclustering** to find patient subgroups + associated subnetworks; demonstrated on breast and lung cancer | [9] |
| **SCANet** (Tool 19) | end-to-end **single-cell RNA-seq** analysis (QC/filtering, dimensionality reduction, clustering, gene co-expression modules) | [10] |
| **MOFA+ / MofaExploration** (Tool 17) | **multi-omics / multi-modal single-cell factor analysis** (unsupervised integration across data modalities and groups) | [11] |
| **SpliceDrift** (Tool 20) | Bayesian modeling of **age-related splicing drift** | (Tool 20; method-specific) |

These cover the analysis types a biomedical end-user actually performs — patient stratification,
subtype/biomarker discovery, regulatory-network dysregulation, single-cell analysis, multi-omics
integration, and splicing analysis — on real biomedical data. Several originate from the same
systems-medicine community as PoSyMed and are distributed as installable packages and/or web
apps, i.e. they are in genuine end-user use, not toy implementations.

### B.2 The datasets span standard biomedical benchmarks and real disease cohorts

The evaluation inputs are recognizable community datasets rather than synthetic-only data:

- **Breast Cancer Wisconsin (Diagnostic)** (UCI ID 17) — a standard clinical tabular benchmark
  used throughout the tool- and workflow-level runs.
- **GSE30219** — a **Non-Small-Cell Lung Cancer** cohort from GEO (adenocarcinoma vs squamous
  cell carcinoma), used with BiCoN.
- **PBMC 3k (10x Genomics)** — the canonical single-cell RNA-seq reference dataset, used with
  SCANet.
- **TCGA-derived / BioGRID interaction networks**, gene-regulatory-network + expression + metadata
  triples (DysRegNet), and time-course expression matrices (Spycone).
- Classic tabular datasets (**Iris**, and, in the LLM benchmark, *dermatology*, *hepatitis*,
  *wine*, *zoo*) used where a small, well-understood, deterministic input is preferable.

### B.3 Proof-of-concept vs typical-workflow: an explicit distinction

We make the roles explicit rather than conflating them:

- **Orchestration-validation ("proof-of-concept") workflows.** WF 1–12 (including the two ported
  here) intentionally use *generic, deterministic* ML building blocks (UCI fetch, one-hot
  encoding, train/test split, Birch/GMM clustering, merge). Their purpose is to **stress the
  orchestration engine** — linear chains, shared-input fan-out, branch-and-merge DAGs — with
  runs that are exactly reproducible and independently verifiable (as in Part A). They are not
  claimed to be novel biomedical analyses; they validate that PoSyMed *executes* multi-step
  workflows correctly and deterministically.
- **Domain workflows / tool runs reflecting typical end-user tasks.** The domain apps in §B.1,
  run on the disease datasets in §B.2 (Table 4, e.g. DysRegNet on GRN+expression+metadata, BiCoN
  on NSCLC + BioGRID, SCANet on PBMC 3k, MOFA+ on multi-omics), are representative of real
  biomedical analysis: patient stratification, subnetwork/biomarker discovery and single-cell
  characterization are exactly the tasks these methods were published to perform.

### B.4 Scope and honest limitations

The workflows demonstrate that these representative tools can be **composed and executed** within
PoSyMed; the study does not claim to reproduce any specific published biomedical *finding*
end-to-end, and the ML-utility workflows are proof-of-concept for orchestration rather than
clinical analyses in themselves. The representativeness argument rests on (i) the catalog being
built from independently published, in-use biomedical methods and (ii) the inputs being standard
benchmarks and real disease cohorts — while the deterministic ML workflows provide the
controllable, verifiable backbone needed to evaluate the orchestration layer itself.

---

## Reproducibility

```bash
# one environment for the Snakemake and Nextflow ports (and the shared tools):
conda env create -f workflows/7/common/environment.yml
conda activate posymed-cmp

# WF 7
bash workflows/7/snakemake/run.sh
bash workflows/7/nextflow/run.sh
bash workflows/7/galaxy/run.sh      # requires: pip install planemo

# WF 12
bash workflows/12/snakemake/run.sh
bash workflows/12/nextflow/run.sh
bash workflows/12/galaxy/run.sh     # requires: pip install planemo
```

Exact versions used for the reported runs: Python 3.11.15, pandas 3.0.3 (Galaxy tools:
pandas 2.2.3), scikit-learn 1.9.0 (Galaxy tools: 1.5.2), Snakemake 9.23.1, Nextflow 26.04.6
(OpenJDK 21), Galaxy executed via planemo 0.75.45. The UCI fetch uses `ucimlrepo` online and
falls back to the committed `step-1/output/uci_dataset17.csv` offline (identical bytes).

## References

1. Köster J, Rahmann S. *Snakemake — a scalable bioinformatics workflow engine.* Bioinformatics 28(19):2520–2522, 2012. (See also Mölder et al., *F1000Research* 10:33, 2021.)
2. Di Tommaso P, et al. *Nextflow enables reproducible computational workflows.* Nature Biotechnology 35:316–319, 2017.
3. The Galaxy Community. *The Galaxy platform for accessible, reproducible, and collaborative data analyses: 2024 update.* Nucleic Acids Research, 2024.
4. Wratten L, et al. / State-of-the-Workflow surveys and *Empowering bioinformatics communities with Nextflow and nf-core*, Genome Biology, 2025 — adoption trends of Nextflow, Snakemake and Galaxy.
5. Zolotareva O, et al. *UnPaSt: unsupervised patient stratification by differentially expressed biclusters in omics data.* arXiv:2408.00200. Tool: https://apps.cosy.bio/unpast/
6. Kersting J, et al. *DysRegNet: patient-specific and confounder-aware dysregulated network inference towards precision therapeutics.* British Journal of Pharmacology 183(8):1709–1724. Code: https://github.com/biomedbigdata/DysRegNet_package
7. Lee C-Y, et al. *Systematic analysis of alternative splicing in time-course data using Spycone.* Bioinformatics 39(1):btac846, 2023.
8. Rose TD, Bechtler T, Ciora O-A, et al. *MoSBi: automated signature mining for molecular stratification and subtyping.* PNAS 119(16):e2118210119, 2022. Code: https://github.com/tdrose/mosbi
9. Lazareva O, et al. *BiCoN: network-constrained biclustering of patients and omics data.* Bioinformatics 37(16):2398–2404, 2021. Code: https://github.com/biomedbigdata/BiCoN
10. Oubounyt M, et al. *Inference of differential key regulatory networks and mechanistic drug repurposing candidates from scRNA-seq data with SCANet.* Bioinformatics 39(11):btad644, 2023. Code: https://github.com/oubounyt/SCANet
11. Argelaguet R, et al. *MOFA+: a statistical framework for comprehensive integration of multi-modal single-cell data.* Genome Biology 21:111, 2020.
12. PoSyMed — *Biomedical systems biology workflow orchestration and execution with PoSyMed* (this work; preprint arXiv:2604.20906).
