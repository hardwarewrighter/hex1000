# Changes

## 2026-10-19

- Diagnostics: add a temporary raw keypad row/column display probe,
  test all 16 positions and SPI framing, and load SRAM with CRC success
  to investigate reported duplicate and swapped rows without remapping.
  Confirm inverted row enables physically, set explicit TO=SIG on
  diagnostic/calculator row buffers, and guard constraints/routed cells;
  program corrected persistent calculator flash with CRC success.
  Record user-confirmed addition, subtraction, multiplication and
  negative-result display, plus the unlabeled operator button mapping.

- Calculator: show DEADBEEF until the first debounced key, process that
  key normally and keep equals-equals clear at zero; review updated Front
  regression/type baselines and test model/RTL startup equivalence.
  Confirm the display-only DEADBEEF fixture at the calculator SPI rate;
  record the disconnected display 5V lead as the blank-display cause.
  Program the uncompressed calculator into flash with CRC success;
  reject loader CRC failures even when its exit status is zero.

- Hardware: record corrected FPGA23 OE connection at 3.29V and load
  the display-only slow SPI diagnostic into Nano 1K SRAM with CRC
  success; preserve calculator flash and await display observation.

- Diagnostics: prepare a slow display-only 00000000 SRAM fixture with
  tested SPI initialization/brightness and a green heartbeat; remove
  the misleading optional TXS OE label and document the isolated
  10 kohm GPIO-load check for the observed OE voltage drop.

- Wiring: draw TXS0108E OE and its 10 kohm pull-down explicitly,
  distinguish the resistor branch from the signal wire, and record the
  first blank-display/green-LED report with diagnosis pending.

## 2026-10-18

- Calculator: add X_eTaL Front and reviewed new baselines, matching RTL,
  physical keypad debounce, MAX7219 output and double-equals clear;
  check model equivalence and production-timing board simulations, add
  guarded SRAM/flash builds and automatic TXS0108E OE on pin 23;
  program internal flash with CRC success for the first wired test.

- Hardware: add a guarded Nano 1K SRAM self-test that internally keys
  12+34=, checks 46 and reports via RGB LEDs; add simulation, failure
  injection, device/pin guards, reproducible build and timing records.

- Hardware: add printable TXS0108E breakout wiring PNG/SVG, including
  both power rails, channel assignments and the OE startup sequence.

- Hardware: add photo-based physical Dupont and level-shifter diagrams,
  editable SVGs, PNGs and a netlist-driven generator; move keypad C2/C3
  from non-header FPGA pins 32/33 to header-accessible 20/35.

- Hardware: correct keypad R1/R2 to FPGA package pins 15/16 in the
  netlist and docs; include the MAX7219 level shifter and distinguish
  package pins from header positions and programmer GPIO.

- Docs: verify proposed keypad pins 25/26 are power/ground, document
  the candidate replacements and configuration-pin checks, and align
  keypad directions with the Mac front-panel plan.

- Docs: implementation notes (docs/implementation-notes.md): the user's
  keypad legends and K1-K4 order, the key map onto the machine's scan,
  the front-panel design (scan, debounce, MAX7219 stream), what in
  hex1000.net needs changing (level shifter, pull-ups, pins 25/26
  unconfirmed) and what to verify on the Linux machine.

- Docs: clarify that hex1000.net records the proposed connection choices
  and is the starting point for pin and software mapping verification.

- Project: import pinned X_eTaL machine, calculator and panel sources,
  regression baselines, demos, reference circuit and local tooling;
  document Nano 1K scope, wiring verification and remaining hardware work.
