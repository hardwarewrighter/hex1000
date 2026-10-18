# Hardware interfaces

Target: Tang Nano 1K, GW1NZ-LV1QN48C6/I5, nominal 27 MHz clock.
The board has USB JTAG but no onboard USB UART. The physical calculator
uses its keys and display directly.

## Current physical setup

As reported by the user on 2026-10-18, a Tang Nano 1K is connected by
USB. The keypad, four-button strip and SPI MAX7219 display are not yet
connected. This is user-reported presence, not a tool-verified device ID.
No board programming or peripheral wiring was performed during import.

Before connecting anything, establish a shared, verified connection
table and matching software signal mapping. The table must include
board orientation/revision, header position, package pad, peripheral
terminal, direction, voltage and pull mode. Resolve the keypad's actual
key legends and connector order, the K1-K4 operator order, display
module pin labels, level-shifter wiring and power source together.
The existing netlist is not an approved wiring plan.

## Proposed connection choices

See [the pin review](pin-review.md): original FPGA pins 25 and 26 are
power and ground. The corrected netlist uses 15 and 16 for R1 and R2.

hex1000.net records the user's proposed assignments and is the starting
point for verification and the software pin map. Preserve those choices
where valid; identify specific conflicts and explain any needed changes
before wiring. Package pad numbers and physical header positions must
be distinguished during verification.

## Wiring status

The original docs/research.txt conversation is historical research.
hex1000.net now records corrected FPGA package pins, but board revision,
header positions and final constraints still require reconciliation.
The JSON .net file is a custom connection list,
not a KiCad or Fritzing schematic.

Before assigning pins, check the board schematic, package pinout,
Apicula device support and loader board identity. Record each peripheral
signal, header position, FPGA package pad, direction and pull mode.
Exclude JTAG, clock and board-driven signals from peripheral assignments.

## Intended interfaces

| Peripheral | Signals | Behavior |
| ---------- | ------- | -------- |
| Hex keypad | R1-R4 outputs, C1-C4 inputs | Scan rows low, read columns with pull-ups; debounce and translate to the machine's K inputs |
| Operator strip | K1-K4 inputs, common GND | Active low, pull-ups; map to +, -, *, = |
| MAX7219 | DIN, CLK, LOAD outputs; VCC, GND | Eight digits, no-decode mode, software hex font |

Confirm the keypad connector order by continuity measurement. Its
physical labels do not establish the machine's logical key mapping.
Drive inactive rows high impedance or use suitable current limiting;
multiple simultaneous keys must not short opposing FPGA outputs.

The FPGA uses 3.3 V I/O. The intended 5 V MAX7219 interface includes a
74AHCT125 at 5 V on DIN, CLK and LOAD, with common ground. The corrected
netlist includes that part with logical channel terminal names. Final wiring,
power sourcing and component values must be documented with the board
and module datasheets before hardware bring-up.

## Core integration

The unchanged hex1000 module has clk, synchronous active-high rst,
in_k[4:0], out_o[5:0] and out_r[15:0]. Hold reset across at least one
machine clock. The imported RAM initializes at configuration but is not
cleared by reset; reload configuration for a clean start until the ROM
clears it itself. See the historical handoff for exact smoke-test traces.

The proposed panel captures digit strobes R0-R7 and O, scans keys through
the machine's R8-R13 protocol, and serializes completed display frames.
R14 is reserved for overflow and R15 indicates ready. Neither a complete
panel RTL driver nor its final resource usage has been established here.
