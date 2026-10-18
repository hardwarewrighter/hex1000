# Netlist and implementation review

Reviewed 2026-10-18 against Mac implementation notes at 9efedd3,
Sipeed's pinmap, Gowin UG842E and the installed Apicula GW1NZ-1
QFN48 database. No device was programmed.

## Confirmed issues

- The original hex1000.net assigned keypad R1 to FPGA package pin 25 and R2 to 26.
  In QFN48, 25 is VCCIO1 (power) and 26 is VSS (ground), not GPIO.
  This is a definite rejection, not a choice to leave pending.
- The Sipeed pinmap also shows a header connection numbered 26 for
  BL702 GPIO23. That is the USB programmer MCU, not FPGA package 26.
  Do not mix the two numbering domains.
- The proposed netlist has no repeated FPGA pin assignments. Its
  conflict is with package functions, not duplicate peripheral usage.
- hardware.md previously reversed the keypad directions from the Mac
  front-panel design. The agreed design drives rows R1-R4 low one at
  a time (others high impedance), reads columns C1-C4 with pull-ups,
  and maps left-to-right columns to machine K0-K3. Corrected there.
- The original direct MAX7219 signal nets omitted the planned level
  shifter. The corrected netlist includes a 74AHCT125 at 5 V, with
  active channels enabled and the unused channel disabled.

## Corrected connection choices

Use the Mac proposal's alternative R1=15, R2=16; keep R3=27, R4=28,
columns=31/20/35/34, operators=38/39/40/41, display=17/18/19.
All these corrected assignments are FPGA I/O present on Sipeed's side-header pinmap. They do not
collide with clock 47, RGB LEDs 9/10/11, buttons 13/44 or JTAG 3/4/5/7.
hex1000.net now uses this mapping. It identifies FPGA package numbering
explicitly and includes the level shifter. The [physical cable diagram](wiring.md) now maps the side-header holes.
Final constraints and hardware operation remain to be verified.

Several are dual-purpose configuration pins, so being valid FPGA I/O
is not sufficient for a working bitstream:

| Proposed pin | Apicula configuration functions |
| ------------ | ------------------------------ |
| 15 | MCLK, D4 |
| 19 | DOUT, WE_N |
| 27 | SSPI_CS_N, D0, GCLKT_3 |
| 28 | DIN, CLKHOLD_N |
| 31 | MI, D7 |


The remaining proposed peripheral pins have no configuration function
listed in this database. Verify the correct packer GPIO-release options
and run placement/routing with the final constraints. Global-clock/PLL
alternatives alone do not mean a pad must be excluded as ordinary I/O.
Do not treat the earlier implementation-notes recommendation to exclude
all SSPI/MSPI pins as a completed validation of its own proposed table.

## Software agreement

- Top-to-bottom keypad rows: C D E F / 8 9 A B / 4 5 6 7 / 0 1 2 3.
- Operators K1-K4: +, -, *, =; common ground, active-low inputs.
- The planned Front model/RTL must implement synchronization, debounce,
  row scanning, key translation, digit capture and MAX7219 output.
- This checkout has no libs/Front implementation yet. The Mac notes
  describe its interface; they are not evidence of completed firmware.
- Double-equals clear, overflow text and RAM clearing are still planned
  changes relative to the imported calculator.

Before connecting peripherals, reconcile the corrected mapping with
actual header locations and module labels, then match the software and
constraints to that same table. Keypad connector order still needs a
continuity check. The 1K remains USB-only; no external connections or
hardware tests are claimed.

## Sources

- [Sipeed board pinmap](https://en.wiki.sipeed.com/hardware/en/tang/Tang-Nano-1K/assets/1k-pin.png)
- [Gowin GW1NZ-1 pinout UG842E, QN48 column, pages 6-7](https://cdn.gowinsemi.com.cn/UG842E.pdf)
- [Sipeed LCD example constraints](https://github.com/sipeed/sipeed_wiki/blob/main/docs/hardware/en/tang/Tang-Nano-1K/examples/lcd.md)
- Local database: /disk1/tmp/oss-cad-suite/lib/python3.11/site-packages/apycula/GW1NZ-1.msgpack.xz,
  pinout['GW1NZ-1']['QFN48'].

## Side-header follow-up

Pins 32/33 are valid FPGA I/O but not shown on the physical side headers.
C2/C3 now use 20/35 instead. The earlier package-only review did not
establish header access; wiring.md provides the corrected diagram.
