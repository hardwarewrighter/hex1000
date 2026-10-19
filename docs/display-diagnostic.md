# Display and shifter first

Keep keypad and switches disconnected until the display works. Green
on the calculator indicates core ready, not successful SPI reception.
The first wired display remained blank. Reported supplies are display
VCC 5V, TXS VCCA 3.3V and VCCB 4.67V. Nano pin 23 measured 3.3V
unloaded, while both pin 23 and OE measured 0.87V connected. The OE
pull-down measured 9.94 kohm. These observations do not identify whether
the problem is GPIO drive, the physical pin, the wire or the shifter.

## OE is required for TXS0108E

The previous board diagram's "optional" label was misleading and is
removed. With this shifter, pin 23 connects directly to OE, with a
10 kohm branch from that node to ground. It must be driven high to
enable translation. With the 74AHCT125 alternative, pin 23 is unused.
Do not tie OE to 3V3 while it is connected to a driven FPGA pin.

## Isolate the GPIO load

Unloaded 3.3V does not prove an actively driven high: a weak pull-up
can read high on a meter and fall under load. With USB disconnected,
disconnect TXS OE from Nano pin 23. Put only a 10 kohm resistor between
Nano pin 23 and Nano GND. Power up and measure that pin against GND.
A properly driven high should remain near 3.3V with this modest load.
If it drops, investigate the pin/firmware/connection before blaming the
shifter. If it stays high, isolate the shifter and wiring next.

Disconnect USB before rewiring or resistance/continuity checks. Measure
supply voltages at each module's terminals, not only at the Nano end.

## Prepared display-only diagnostic

The fixture sends `DEADBEEF` (visible as `dEAdbEEF`) at minimum
brightness using about 482 kHz SPI, matching the calculator rate. There is no calculator, keypad or operator logic. Green blinks to
identify the fixture; this alone does not prove the display received it.
A simulated SPI receiver checks two complete frames. Build runs that
simulation before synthesis, timing-checked routing and packing.

```bash
export PATH="/disk1/tmp/oss-cad-suite/bin:$PATH"
just display-probe test
just display-probe build
just display-probe load
```

Loading requires a single GW1NZ-1 ID and matching source/image hashes.
It programs SRAM only, preserving the calculator in flash. Power cycling
removes the fixture. The board must be visible on this Linux machine's
USB data connection before loading. The diagnostic was loaded into SRAM on 2026-10-19 with CRC success.
The user corrected OE from a programmer GPIO to the actual FPGA23,
and measured 3.29V at OE. The user then found the display 5V lead disconnected. Reconnecting it
produced eight zeros with the original slow fixture. The updated fixture
produced `dEAdbEEF` at the calculator SPI rate, confirmed by the user.
This proves those glyphs and their ordering, not every hexadecimal glyph.

## Correct pin and diagnostic load

The user found the OE lead on a programmer GPIO marked 23, rather than
the FPGA pin. Use **the left side, eighth hole from the bottom**, USB
up, for FPGA23 (IOR8B/B3). The programmer's similarly numbered GPIO
is not interchangeable. After correcting this, OE measured 3.29V; the
calculator display remained blank. The slow diagnostic was then loaded
into SRAM with successful CRC. The successful display results are recorded in
boards/tangnano1k/evidence/display-probe.json.
