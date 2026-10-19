#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
for script in scripts/*.sh scripts/xt; do bash -n "$script"; done
scripts/test-libs.sh
scripts/doctest-libs.sh
scripts/rom-hex.sh --check
scripts/fit.sh hex1000
scripts/check-core.sh
python3 scripts/test-board-selftest.py
python3 scripts/board-selftest.py test
python3 scripts/board-calculator.py test

if command -v iverilog >/dev/null && command -v vvp >/dev/null; then
    python3 scripts/keypad-probe.py test
else
    echo "SKIPPED raw keypad diagnostic: iverilog/vvp not on PATH"
fi
