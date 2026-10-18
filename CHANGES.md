# Changes

## 2026-10-18

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
