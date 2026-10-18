# Source provenance

Initial import from hardwarewrighter/X_eTaL-fpga commit `78bb13abe64068f9c71c6f77f8d1769ef2038790`.

The Hex1000, Radix and Panel libraries include their original X_eTaL
sources, demos, reg-rs outputs, pinned types, ROM and circuit artifacts.
The evaluator and shared libraries retain the upstream commit pins.
No files in the source repository were changed for this import.

The pinned RTL and XIR are reference artifacts. Regenerating RTL still
uses X_eTaL-fpga's generator at that commit; this repository does not yet
contain that Rust compiler. `just fit` measures synthesis, not placement,
timing closure or physical operation. The UART wrapper is reference-only
and is not the Nano 1K implementation.

The historical handoff describes work pending at import time. New work
and decisions belong in this repository's docs/plan.md.

The pinned scripts/hex1000.tb.v was generated from hex1000.xir with
`xetal-fpga testbench --memories`. `just check-core` runs it when
Icarus Verilog is on PATH; missing tools are explicitly skipped.
