# Implementation plan

1. Imported foundation: run the pinned X_eTaL demos, reg-rs tests, doc
   examples and ROM check locally. Preserve the evaluator as specification.
2. Before connecting peripherals, agree on a verified connection table
   and matching software mapping. The user reports the 1K is connected
   over USB only, with all peripherals disconnected. Verify board revision, device/family, loader name and pins.
   Add guarded constraints and a core smoke top. Simulate reset, shown
   digit, latched digit-0 strobe and ready; synthesize and route before
   programming an identified Nano 1K. Never use the attached 9K as a 1K.
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
