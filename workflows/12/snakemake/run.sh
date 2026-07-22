#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
snakemake --cores 2 -p
