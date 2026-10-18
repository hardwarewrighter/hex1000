# Implementation notes

Inputs and recommendations from the X_eTaL-fpga (Mac) side, 2026-10-18,
for whoever wires, builds and programs the Nano 1K. What is decided,
what in hex1000.net needs changing, and what still has to be verified
with the tools on the Linux machine before anything is wired or loaded.

## Linux verification follow-up

See [pin-review.md](pin-review.md). QFN48 package pins 25 and 26 are
VCCIO1 and VSS, not user I/O. The conditional choice below is resolved:
do not use 25/26 for the keypad. The netlist now uses pins 15/16 instead, with configuration-pin handling
still to be verified.

## Decided by the user

| Item | Decision |
| ---- | -------- |
| Keypad legends | top row C D E F, second 8 9 A B, third 4 5 6 7, bottom 0 1 2 3 |
| Operator strip | K1 +, K2 -, K3 *, K4 = (common ground) |
| Display | 8-digit MAX7219 module (SPI style: DIN, CLK, CS/LOAD) |
| Calculator rules | negatives stay two's complement; `= =` clears; overflow shows `OuErFLO` (lamp on R14); the program clears its own RAM at startup (plan step 3) |
| No reset or clear button | power-up and reconfiguration reset the machine |

The keypad layout is the one the Panel library already models
(`pn:Keys`), so the 3D mockup, the X_eTaL model and the board agree.

## The key map follows from the machine

The calculator program scans six key columns on R8 to R13 and reads
the row on K0 to K3: key code c is in column c / 4 (R8 + c / 4) and
drives K bit c mod 4 (`hx:m_atrix`; codes 0 to 15 the digits, 16 + 17 -
18 * 19 =, 20 X). On this keypad that is exactly one physical row per
machine column:

| Keypad row (top to bottom) | Legends | Codes | Machine column |
| -------------------------- | ------- | ----- | -------------- |
| R1 | C D E F | 12 to 15 | R11 |
| R2 | 8 9 A B | 8 to 11 | R10 |
| R3 | 4 5 6 7 | 4 to 7 | R9 |
| R4 | 0 1 2 3 | 0 to 3 | R8 |
| strip | + - * = | 16 to 19 | R12 |

Keypad column C1 to C4 (left to right) gives K bit 0 to 3. There is no
X (clear) key; `= =` takes its place once calc-rules lands, and `0 * =`
clears meanwhile.

That R1 is the top row and C1 the left column is the usual convention
for these membrane pads, not a measured fact: check it with a meter
(press C, expect continuity between R1 and C1) before wiring. If the
order differs, change only the key map table in the front panel module
(`Map` in libs/Front), not the wiring.

## Why a front-panel module, not wires to the machine

The machine could scan the pad directly (R8 to R11 driving the rows,
the columns into K), but:

1. Keys bounce for a few milliseconds. The program waits for every key
   to be up and then takes the next press, so at a million instructions
   a second one bounce would enter a digit twice.
2. The operator strip's buttons share ground; they cannot be selected
   by R12 without logic.
3. The MAX7219 needs a serial stream, not the program's digit strobes.

So the board top wraps the unchanged `hex1000` core in a front-panel
module, modeled in X_eTaL first (libs/Front, in progress) and written
as Verilog checked clock for clock against that model:

- scan: drives one keypad row low at a time (the others high
  impedance, so two keys pressed at once never short two outputs), and
  reads the four columns and the four operator buttons through a
  two-flip-flop synchronizer (inputs pulled up, a pressed key reads 0);
- debounce: a complete scan (16 keys plus 4 buttons) is accepted only
  after it has been identical for D scans in a row. The board uses 256
  machine clocks a row (about 1 ms a scan) and D = 8, about 9 ms;
- the key the machine sees: the first pressed key of the accepted scan,
  through the key map, shown on K the way `hx:m_atrix` does, while
  the program selects its column. The program does the rest: it takes a
  key once and waits until every key is up;
- the digits: digit p latches O (bits 0 to 4) when R p rises, as the
  9K glue and `hx:t_ype` do;
- the display: a loop of 13 16-bit words, MSB first, data changing
  while CLK is low, CLK rising mid-bit, LOAD (CS) low for the 16 bits
  and high for 4 clocks after them. The first five words set it up and
  are resent every pass (so a display powered after the FPGA, or
  disturbed by noise, recovers within a millisecond): 0x0C01 (run),
  0x0F00 (test off), 0x0900 (no decode: our own hex font), 0x0B07
  (eight digits), 0x0A04 (intensity 4 of 15). Then digits 1 to 8:
  register p + 1 takes digit p's segments (digit 0 is the right-hand
  digit, register 1 on the usual modules). The segment bytes are the
  Panel font's (`pn:Font`) in the MAX7219's order (DP A B C D E F G);
  a blank digit sends 0;
- at the machine clock (27 MHz / 28, about 0.96 MHz) the serial clock
  is about 480 kHz (the MAX7219 accepts 10 MHz) and the whole display is
  rewritten about 2000 times a second.

## Original hex1000.net review and corrections

The original proposal (from docs/research.txt) was reviewed below.
The current hex1000.net corrects R1/R2 to 15/16 and includes the
74AHCT125 signal paths and power. Remaining checks still apply.

| # | In hex1000.net | Problem | Recommendation |
| - | -------------- | ------- | -------------- |
| 1 | MAX7219 DIN, CS, CLK straight to pins 17, 18, 19 | The FPGA drives 3.3 V; the MAX7219 at 5 V wants at least 3.5 V for a high. It often works, unreliably | Through a 74AHCT125 (or 74HCT125/HCT245) powered at 5 V: FPGA pin to A, Y to the MAX7219, its OE pins to ground. Keep pins 17, 18, 19 |
| 2 | Keypad columns described as inputs with pull-down, rows driven | The module drives one row low at a time and reads the columns with pull-ups (a pressed key reads 0) | Rows R1 to R4 outputs (high impedance when not selected), columns C1 to C4 inputs with `PULL_MODE=UP` |
| 3 | Original keypad R1, R2 on pins 25, 26 | QFN48 pin 25 is VCCIO1 and 26 is VSS; neither is GPIO | Fixed in hex1000.net: R1 on 15, R2 on 16 |
| 4 | Pins 27, 28, 31-34 (keypad), 38-41 (strip), 17-19 (display) | Confirmed as user I/O in Sipeed's LCD example constraints (15-24, 27-35) and Apicula's tangnano1k.cst (38-41) | Keep |
| 5 | Operator strip K1-K4 on 38-41 with `PULL_MODE=UP` | Correct. Note Apicula's examples also use 39/40 as an LVDS pair and 40/41 for other tests: plain LVCMOS33 inputs are fine | Keep: K1 + (38), K2 - (39), K3 * (40), K4 = (41) |
| 6 | MAX7219 VCC from the board's "5V" pin | Check the Nano 1K actually brings 5 V (USB VBUS) to a header pin and how much current it can supply; the display can draw 150 mA or more at high intensity | Measure the pin; intensity 4 keeps current modest |
| 7 | Not in the netlist | Clock and status | Clock pin 47 (27 MHz). The onboard RGB LED (pins 9 red, 10 blue, 11 green; active low per Sipeed's examples) can show ready (R15), overflow (R14) and a heartbeat |
| 8 | Not in the netlist | Pin numbers vs header positions | The numbers above are FPGA package pins (what `IO_LOC` takes). Map each to its header hole from Sipeed's pinout picture before wiring |
| 9 | Not in the netlist | Series resistors | 330 ohm to 1 kohm in series on each keypad row line is cheap insurance against a wiring mistake; the high-impedance rows already prevent key-to-key shorts |

Avoid pins 13 and 44 (the onboard buttons; 44 is labeled nRST in
Sipeed's LCD constraints) and the JTAG pins.

### Proposed constraints (to verify, not yet a .cst)

| Signal | Package pin | Direction | Mode |
| ------ | ----------- | --------- | ---- |
| clk | 47 | in | LVCMOS33 |
| pad_row_n[0] (R1, C D E F) | 15 | out, high impedance when idle | LVCMOS33 |
| pad_row_n[1] (R2, 8 9 A B) | 16 | out, high impedance when idle | LVCMOS33 |
| pad_row_n[2] (R3, 4 5 6 7) | 27 | out, high impedance when idle | LVCMOS33 |
| pad_row_n[3] (R4, 0 1 2 3) | 28 | out, high impedance when idle | LVCMOS33 |
| pad_col_n[0..3] (C1..C4) | 31, 32, 33, 34 | in | LVCMOS33 PULL_MODE=UP |
| op_n[0..3] (K1 + .. K4 =) | 38, 39, 40, 41 | in | LVCMOS33 PULL_MODE=UP |
| max_din | 17 | out (via 74AHCT125) | LVCMOS33 |
| max_load (CS) | 18 | out (via 74AHCT125) | LVCMOS33 |
| max_clk | 19 | out (via 74AHCT125) | LVCMOS33 |
| led_n[0..2] (red, blue, green) | 9, 10, 11 | out | LVCMOS33 |

## To verify on the Linux machine (before wiring or loading)

1. The board: `openFPGALoader --detect` reports a GW1NZ-1, and
   `openFPGALoader --list-boards` has `tangnano1k`.
2. The pins: with Apicula, list the package's pins and their functions
   for GW1NZ-1, QN48 (Apicula's chip database names each pad's
   function); confirm every pin in the table above is ordinary I/O and
   none is JTAG, MODE, DONE, RECONFIG_N or the SSPI/MSPI pins (which
   gowin_pack only frees with `--sspi_as_gpio` / `--mspi_as_gpio`).
   Pins 25/26 have been rejected; verify GPIO release for the selected
   dual-purpose pins, including replacement pin 15.
3. The flow, from Apicula's own Makefile for this board:
   `synth_gowin`, then `nextpnr-himbaechel --device GW1NZ-LV1QN48C6/I5
   --vopt cst=...`, then `gowin_pack -c -d GW1NZ-1`. Confirm the
   placed resource numbers and the timing at the machine clock.
4. Tri-state: the row outputs use high impedance (Apicula has a
   `blinky-tbuf` example for this board). If the flow rejects it, drive
   the rows push-pull and fit the series resistors of item 9.

## Order of work

1. Smoke top (plan step 2): core only, LEDs for ready, shown and the
   digit-0 strobe latch, as in docs/handoff-1k.md. Proves the board, the
   flow and the block RAMs.
2. Front panel (plan step 4): libs/Front in X_eTaL, its Verilog, the
   clock-for-clock check, the full design's fit, then the calculator top
   and its constraints.
3. Calculator rules (plan step 3) change only the ROM; the front panel
   and the wiring do not change with them, so they can land in either
   order.
4. Wire one peripheral at a time: the display first (it shows 0 at
   power-up), then the strip, then the pad; compare screens with
   `hx:c_alc`.
