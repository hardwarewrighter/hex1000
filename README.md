# HEX1000 on the Tang Nano 1K

A physical hexadecimal calculator with a 4x4 keypad, four operator
buttons (+ - * =) and an eight-digit MAX7219 display. X_eTaL is the
executable specification; the FPGA circuit must produce the same screens.

## Current state

The machine, calculator ROM, panel model and regression baselines are
imported from X_eTaL-fpga. The core previously synthesized to 438 LUTs,
81 flip-flops and 2 block RAMs against the 1K's 1152/864/4 capacity.
The Nano 9K UART calculator was physically tested in the source project.
No Nano 1K hardware operation is claimed here.

The panel library models the font, layout and key behavior. A debounced
physical keypad interface, MAX7219 driver, verified Nano 1K constraints
and board top remain to be implemented.

## Run the specification

Requires bash, Python 3, Git, Rust/Cargo and just; regression tests also
need reg-rs. External HDL tools are optional and reported when absent.
Nothing installs tools or programs hardware automatically.

```bash
just setup
just demo-lib Hex1000 calc
just demo-lib Panel font
just test
just fit
just gate
```

Setup clones the exact commits in XETAL_COMMIT and
XETAL_LIBRARIES_COMMIT and builds the evaluator locally. Local checkout
sources can be supplied with XETAL_SOURCE and XETAL_LIBRARIES_SOURCE.
The scripts also run directly without just.

| Path | Contents |
| ---- | -------- |
| libs/Hex1000 | Machine specification, assembler, ROM, demos and reference RTL |
| libs/Radix | Calculator reference behavior |
| libs/Panel | Hex font, panel geometry and key model |
| docs/machine.md | Instruction set and machine I/O |
| docs/hardware.md | Peripheral interfaces and wiring verification status |
| docs/plan.md | Implementation order and acceptance checks |
| docs/implementation-notes.md | Key map, front-panel design, netlist corrections, pins to verify |
| docs/provenance.md | Import source, pins and artifact limitations |

See [the hardware plan](docs/hardware.md) before using the original
hex1000.net wiring proposal. It has unverified pin numbers and omits
the display level shifter. It is preserved as research, not constraints.
