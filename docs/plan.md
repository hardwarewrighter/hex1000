# Implementation plan

1. Imported foundation: run the pinned X_eTaL demos, reg-rs tests, doc
   examples and ROM check locally. Preserve the evaluator as specification.
2. Before connecting peripherals, agree on a verified connection table
   and matching software mapping. The user reports the 1K is connected
   over USB only, with all peripherals disconnected. Verify board revision, device/family, loader name and pins.
   Add guarded constraints and a core smoke top. Simulate reset, shown
   digit, latched digit-0 strobe and ready; synthesize and route before
   programming an identified Nano 1K. Never use the attached 9K as a 1K.
   The peripheral-free self-test is now simulated and routed: it enters
   12+34= internally and checks 46. See boards/tangnano1k/README.md for
   SRAM loading and observation status.
3. Implement calculator rules in X_eTaL first: double equals clears,
   negatives remain two's complement, overflow shows OuErFLO, and startup
   clears RAM. Check whether newer upstream work already supplies them.
4. Model and test keypad synchronization/debounce, digit capture and
   MAX7219 initialization/serialization. Compare their emitted circuit
   traces against the X_eTaL model and measure the complete design's fit.
5. Publish a verified wiring table and editable schematic with the level
   shifter. Test each peripheral, then compare complete calculations
   against X_eTaL on physical hardware.
6. Verify explicit flash loading and cold boot, then battery power and
   enclosure. Record tools, revisions, timing and hardware evidence.

The imported 9K UART wrapper is not the 1K panel. Core-only utilization
is not proof that the complete keypad/display calculator fits.

## Physical calculator implementation, 2026-10-18

Front now supplies physical scanning, debounce, == translation and
MAX7219 output, with a clock-by-clock X_eTaL model comparison and
production-debounce board tests. The complete calculator fits the 1K
and passes routed timing with a dedicated global machine clock.
The TXS variant adds automatic OE on pin 23. Persistent flash loading
and the first wired/cold-boot observations are recorded in
boards/tangnano1k/evidence/calculator.json. Overflow text and ROM-side
RAM clearing remain separate future work; arithmetic currently wraps.

## Startup display, 2026-10-19

The display-only DEADBEEF fixture works physically at about 482 kHz SPI.
The blank-display fault was a disconnected display 5V lead; OE is now
3.29V on the correct FPGA23. Front overlays DEADBEEF until the first
debounced key, which is processed normally. Model and board simulations
cover the banner, rejected bounce, first key and clear-to-zero behavior.
Physical keypad tests remain pending.
