# HEX1000 on the Tang Nano 1K

A physical hexadecimal calculator with a 4x4 keypad, four operator
buttons (+ - * =) and an eight-digit MAX7219 display. X_eTaL is the
executable specification; the FPGA circuit must produce the same screens.

## Wiring diagram

[Physical Dupont cable map and MAX7219 level shifter](docs/wiring.md).
USB connector up; the diagram shows each cable at its header hole.

## Test the board without peripherals

The USB-connected FPGA identifies as a GW1NZ-1. A peripheral-free
[self-test](boards/tangnano1k/README.md) enters `12+34=` internally,
checks `46` and uses the RGB LED: green/cyan heartbeat means pass;
red/magenta means failure. `just board-selftest load` is SRAM-only,
with a device-ID guard; power cycling restores the installed flash image.

## Current state

The physical calculator now has a tested front panel: row scanning,
input synchronization, debounce, held-key suppression, MAX7219 output
and equals-equals clear. The X_eTaL Front model matches 1100 RTL clocks;
board simulations pass arithmetic and serial display tests at production
debounce timing. The complete image fits and passes routed timing.

[First wired test](docs/calculator-test.md) explains the persistent flash
image and how to unplug, wire, reconnect and test. TXS0108E users must
use the updated OE wire on FPGA pin 23 and a 10 kohm pull-down. The
display and TXS0108E now show `dEAdbEEF` at the calculator SPI rate;
the keypad and operator buttons remain disconnected. The calculator
starts with that banner until the first debounced key, which is processed
normally. `==` clears to zero without restoring the banner.

Overflow still wraps; OuErFLO and ROM-side RAM clearing remain planned.
The Hex1000, Radix and Panel sources and original core are unchanged.

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
| libs/Front | Physical scanner, debounce, == clear and MAX7219 model/RTL |
| libs/Panel | Hex font, panel geometry and key model |
| docs/machine.md | Instruction set and machine I/O |
| docs/hardware.md | Peripheral interfaces and wiring verification status |
| docs/plan.md | Implementation order and acceptance checks |
| docs/implementation-notes.md | Key map, front-panel design, netlist corrections, pins to verify |
| docs/provenance.md | Import source, pins and artifact limitations |

See [the hardware plan](docs/hardware.md) before using the corrected
hex1000.net connection proposal. It uses FPGA package pins (R1/R2 on
15/16) and includes the display level shifter; header mapping and
configuration-pin handling still need verification.
