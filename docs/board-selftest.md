# Nano 1K test without peripherals

The USB-connected board identifies over JTAG as GW1NZ-1, ID 0x0100681b.
The [board self-test](../boards/tangnano1k/README.md) automatically enters
`12+34=` in the existing core, checks the output is `46`, and indicates
pass/failure using the RGB LED. It uses no keypad or display pins.

The original color-cycling demo was initially in flash, not evidence that
HEX1000 is running. The new SRAM test should alternate green and cyan
on pass; red/magenta means failure. User observation is required to
confirm which pattern is visible. The later physical calculator has now replaced flash; disconnecting
and reconnecting USB loads that calculator, not the original demo.

Simulation, synthesis, placement/routing and packing passed before load.
Reports and bitstream hashes are under work/board/selftest/. A compact
record is retained as boards/tangnano1k/evidence/selftest.json after load.
The board evidence must distinguish tool-reported programming success
from a user-confirmed LED observation.

## Programming result

The tested image was loaded into SRAM on 2026-10-18. openFPGALoader
reported a successful CRC check. The device was reidentified as
GW1NZ-1 immediately before loading. Flash was not written. The user subsequently reported solid green, confirming the pass
indicator. The expected blue heartbeat was not observed. The physical
calculator image is a separate build; see calculator-test.md.
