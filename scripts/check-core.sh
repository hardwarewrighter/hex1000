#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
mkdir -p work/rtl
if command -v iverilog >/dev/null && command -v vvp >/dev/null; then
    iverilog -g2005 -s tb -o work/rtl/hex1000.vvp libs/Hex1000/rtl/hex1000.v scripts/hex1000.tb.v
    (cd work/rtl && vvp -n hex1000.vvp) > work/rtl/simulation.log
    cat work/rtl/simulation.log
    if grep -q 'FAIL' work/rtl/simulation.log; then exit 1; fi
    grep -q '^PASS' work/rtl/simulation.log
else
    echo 'check-core: SKIPPED simulation (iverilog/vvp not on PATH)'
fi
