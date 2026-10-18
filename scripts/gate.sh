#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
for script in scripts/*.sh scripts/xt; do bash -n "$script"; done
scripts/test-libs.sh
scripts/doctest-libs.sh
scripts/rom-hex.sh --check
scripts/fit.sh hex1000
scripts/check-core.sh
