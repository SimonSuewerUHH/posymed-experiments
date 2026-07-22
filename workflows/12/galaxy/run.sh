#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
planemo run workflow.gxwf.yml job.yml \
  --extra_tools tools/ \
  --conda_dependency_resolution --conda_auto_install --conda_auto_init \
  --output_directory results --download_outputs
