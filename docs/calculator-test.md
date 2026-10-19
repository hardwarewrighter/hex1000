# First wired calculator test

This is the physical keypad/display calculator, not the internally keyed
self-test. The X_eTaL Front model matches the controller RTL clock for
clock; complete board simulations pass keypad scanning, debounce, key
release, 12+34=46, A*B=6E, 5-7=FFFFFFFE, C0DE+BEEF=17FCD,
second-equals clear and MAX7219 command/segment framing. The production
256-clocks-per-row debounce setting is tested, not just an accelerated
simulation. The user confirmed `dEAdbEEF` with the display-only fixture
at the calculator SPI rate. Physical keypad tests remain pending.

## Programming complete

On 2026-10-18, the connected GW1NZ-1 was reidentified and its internal
flash was programmed with this calculator image. openFPGALoader reported
**CRC check: Success**. The original color-cycling demo was replaced.
The full gate passed (25 baselines, 178 doc examples and board tests).
On 2026-10-19, the updated calculator was programmed into persistent
flash with **CRC check: Success** using an uncompressed image. It adds a DEADBEEF startup banner until the first
debounced key. That key is processed normally. Banner, first-key and
clear behavior are checked in the X_eTaL model and board simulation.
The display-only fixture was confirmed physically; the updated calculator
and its first physical keypad calculation require user observation.

## Before unplugging

Persistent flash programming must finish successfully. The load record
is boards/tangnano1k/evidence/calculator.json. SRAM programming alone
will not survive unplugging. The flash image replaces the original
color-cycling demo. Only an identified GW1NZ-1 is programmed, with
source/bitstream hash checks; JTAG pins are retained.

Pull the latest hex1000 repository on the Mac and print the updated
[board cable map](images/dupont-board.png) and, for your chosen shifter,
[TXS0108E diagram](images/txs0108e-wiring.png) or
[74AHCT125 diagram](images/level-shifter.png).

**TXS0108E wiring changed:** FPGA package pin 23 (left eighth from
bottom) now drives OE. Add 10 kohm between OE and ground. Remove any
old OE-to-3V3 jumper. Firmware enables OE after about 39 ms. Use
hex1000-txs0108e.net for this variant; hex1000.net is the 74AHCT125
variant. With the 74AHCT125, leave FPGA 23 unconnected.

## Unplug, wire, reconnect

1. Disconnect USB and any other power before moving wires.
2. Wire the passive keypad and operator strip following wiring.md.
   The four row resistors are **1 kohm, not 1 ohm**. The strip GND goes
   to common ground. Confirm the keypad connector order with a meter.
3. Wire the level shifter and display using the selected diagram.
   Display VCC is 5V, with a common ground. TXS VCCA is 3V3 and VCCB
   is 5V. Use DIN on the display's input header, not DOUT. Leave short
   signal leads and use local supply capacitors. Confirm your USB supply
   and board power path can supply the module; do not add another 5V
   source while USB is attached.
4. Reconnect USB. The persistent calculator should show `dEAdbEEF` on
   the display until a key is pressed. The green LED channel means the core is ready; blue is
   a heartbeat, so cyan may also appear. The old rainbow demo should
   no longer run. Display digit order depends on the module: reversed
   digits are a wiring/module-orientation issue to diagnose next.
5. Enter 1, 2, +, 3, 4, =. Expect 46. Press = once more: expect 0.
6. Enter A, *, B, =. Expect 6E. Press = again to clear. Then test
   5 - 7 = (FFFFFFFE) and C0DE + BEEF = (17FCD).

Use one key at a time and release fully between presses. The passive
matrix has no anti-ghosting diodes. If keys differ from their legends,
stop and report the physical key and displayed digit; the connector
order may differ from the assumed R1/C1 convention.

## Behavior and limits

Equals-equals clears the calculation; it does not reset or reconfigure
the FPGA. The panel translates the second consecutive equals into the
existing ROM's Clear key. Power cycling initializes RAM at configuration.
Overflow still wraps modulo eight hex digits; OuErFLO is future work.
There is no UART in this image.

The external keypad, display module, level shifter and power draw cannot
be fully validated while they are disconnected. A successful flash write
is programming evidence; the first cold boot and these wired tests are
reported separately as user observations.

## Reproduce

With OSS CAD Suite on PATH:

```bash
just board-calculator test
just board-calculator build
just board-calculator load    # SRAM only, temporary
just board-calculator flash   # persistent; replaces current flash image
```

The build explicitly routes the divided clock on a global network and
frees the required SSPI/MSPI/CPU configuration pins as GPIO. Reports,
source/image hashes and programming logs are under work/board/calculator/.

Routing uses a global machine clock. The router falls back to ordinary
routing for the divider's own data-feedback inverter (one warning);
clock sinks use the global network and final setup/hold checks pass.
The initial attempt without the global clock failed RAM hold timing
and was not used for programming.

The compressed startup image passed SRAM CRC but reported a flash-reload
checksum mismatch at both 6 MHz and 1 MHz JTAG. Repacking without
compression produced a successful flash CRC. The programming script now
requires explicit CRC success, since this loader can return exit status
zero after reporting a CRC failure. A regression test covers that case.
Use `just board-calculator flash --freq 1000000` to reproduce the
successful programming settings.
