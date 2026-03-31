# PoSyMed Experiments

This repository contains the experimental material used to evaluate the PoSyMed framework across a diverse set of bioinformatics tools and workflow patterns. It serves as a structured companion repository for the associated report and provides concrete execution artifacts, representative inputs and outputs, and run-level reports for both individual tools and composed workflows.

## Overview

PoSyMed was assessed using a broad range of tools that cover core categories of bioinformatics and biomedical data analysis. The evaluated set spans simple acquisition and transformation steps, classical machine learning methods, clustering and biclustering approaches, network-based analysis tools, and single-cell analysis components. The repository is organized to make these experiments inspectable and reproducible at the level of individual tool executions as well as end-to-end workflows.

The experiments emphasize several aspects that are central to PoSyMed:

- integration of tools implemented in different programming languages, especially Python and R
- harmonization of heterogeneous input and output formats
- explicit handling of hyperparameters and tool-specific configuration
- traceable execution through stored reports and run artifacts
- composition of tools into deterministic, multi-step workflows

Together, these materials illustrate how PoSyMed supports practical biomedical analysis scenarios, particularly those relevant to extracting knowledge from omics cohort studies.

## Repository Structure

```text
posymed-experiments/
├── README.md
├── tools/
│   ├── R1.pdf ... R19.pdf
│   ├── 1/ ... 32/
│   └── <tool execution folders with input/ and output/>
└── workflows/
    ├── R1.pdf ... R10.pdf
    ├── 1/ ... 12/
    └── <workflow execution folders with step-wise inputs/outputs>
```

### `tools/`

The `tools/` directory contains standalone executions of individual tools. Each numbered folder corresponds to one tool run and usually follows this structure:

```text
<tool-id>/
├── input/
└── output/
```

The `input/` folder contains the data provided to the tool, while the `output/` folder contains the generated results. Depending on the tool, outputs may include:

- transformed datasets in CSV format
- clustering labels and model parameters
- train/test splits
- regression outputs and explanations
- network analysis result tables
- plots such as scatter plots, silhouette plots, heatmaps, dendrograms, and network visualizations
- single-cell analysis outputs such as processed `h5ad` files and annotation figures

The PDF files `R1.pdf` to `R19.pdf` document the corresponding tool runs and provide run-level reports for inspection.

### `workflows/`

The `workflows/` directory contains composed, multi-step experiments. Each numbered workflow folder stores the intermediate and final artifacts generated during a workflow execution. Workflow folders are organized by step:

```text
<workflow-id>/
├── step-1/
├── step-2/
├── ...
└── step-n/
```

Each step contains its own `input/` and/or `output/` directories, enabling inspection of how data moves through the pipeline. This structure makes the execution trace explicit and allows users to examine both intermediate representations and final results.

The PDF files `R1.pdf` to `R10.pdf` provide workflow-level reports.

## What Is Included

The repository includes experiments covering several recurring classes of operations:

### 1. Data acquisition and extraction
Examples include extraction of benchmark datasets and SQL-based retrieval steps. These runs demonstrate how PoSyMed can ingest data from external repositories and structured data sources.

### 2. Data transformation and preprocessing
Several experiments focus on preprocessing operations such as encoding categorical variables, splitting data into train and test sets, and combining tables. These steps are essential for preparing data for downstream modelling.

### 3. Unsupervised learning
The repository contains outputs from clustering and mixture-model approaches, including examples such as:

- Spectral Clustering
- Agglomerative Clustering
- Gaussian Mixture Models
- biclustering-related methods

Typical outputs include label assignments, cluster centers, covariance estimates, score plots, and diagnostic visualizations.

### 4. Supervised learning
At least one experiment demonstrates classical supervised modelling, such as linear regression, including prediction files, coefficients, and explanatory outputs.

### 5. Network and systems-biology analysis
The repository also contains runs for network-oriented and systems-biology tools, including outputs such as interaction plots, association tables, heatmaps, and graph visualizations.

### 6. Single-cell analysis
The presence of `pbmc3k.h5ad` inputs and corresponding `h5ad` outputs and figures shows that the evaluation also includes single-cell analysis scenarios, with outputs such as reduced representations, processed datasets, highly variable gene plots, clustering figures, and cell annotation visualizations.


## Purpose of This Repository

This repository is intended to support the report by providing concrete evidence for the experimental evaluation of PoSyMed. In particular, it helps document:

- the breadth of supported tool categories
- the practical handling of heterogeneous software stacks
- the management of varying input and output contracts
- the reproducibility of tool and workflow executions through stored artifacts
- the ability to inspect results at both run level and workflow level

Rather than only describing the framework abstractly, the repository exposes the actual experimental traces that underlie the evaluation.