# Nano 1K test without peripherals

The USB-connected board identifies over JTAG as GW1NZ-1, ID 0x0100681b.
The [board self-test](../boards/tangnano1k/README.md) automatically enters
`12+34=` in the existing core, checks the output is `46`, and indicates
pass/failure using the RGB LED. It uses no keypad or display pins.

The existing color-cycling demo is the current image, not evidence that
HEX1000 is running. The new SRAM test should alternate green and cyan
on pass; red/magenta means failure. User observation is required to
confirm which pattern is visible. Programming flash is not part of this
step: disconnect/reconnect USB to restore the existing flash demo.

Simulation, synthesis, placement/routing and packing passed before load.
Reports and bitstream hashes are under work/board/selftest/. A compact
record is retained as boards/tangnano1k/evidence/selftest.json after load.
The board evidence must distinguish tool-reported programming success
from a user-confirmed LED observation.

## Programming result

The tested image was loaded into SRAM on 2026-10-18. openFPGALoader
reported a successful CRC check. The device was reidentified as
GW1NZ-1 immediately before loading. Flash was not written. Physical
LED observation is pending; programming success alone does not confirm
the internally calculated answer.
