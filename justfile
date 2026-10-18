set positional-arguments

default:
    @just --list

setup:
    scripts/xetal.sh
    scripts/xetal-libraries.sh

demo-lib name program="":
    scripts/run-lib.sh --demos "$1" "$2"

run-lib name program="":
    scripts/run-lib.sh "$1" "$2"

test:
    scripts/test-libs.sh
    scripts/doctest-libs.sh
    scripts/rom-hex.sh --check

fit:
    scripts/fit.sh hex1000

gate:
    scripts/gate.sh

check-core:
    scripts/check-core.sh

wiring-diagram:
    python3 scripts/wiring-diagram.py
