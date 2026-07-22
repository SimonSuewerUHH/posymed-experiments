#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
nextflow run main.nf
