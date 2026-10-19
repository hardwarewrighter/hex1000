# Nano 1K peripheral-free self-test

Runs the existing HEX1000 machine with internally generated keys and
uses only the onboard clock and RGB LED. Leave keypad, operator strip
and display disconnected. No UART or level shifter is needed.

## What it checks

The machine gets startup reset for fifteen of its divided clocks.
The harness checks the initial shown zero and digit-0 strobe, waits
for ready, enters the six keys `1 2 + 3 4 =` through the machine's
K/R key-scan protocol, captures the display strobes and checks `46`
with the other six digits blank. It latches pass or failure; a watchdog
fails if the calculation takes more than about 1.09 seconds.

The clock divider is 27 MHz / 28 (about 0.964 MHz). The blue LED
channel blinks independently with an approximately 1.24-second period.
Active-low outputs are red pin 9, blue pin 10 and green pin 11;
the only input is the onboard oscillator on pin 47. All peripheral
header pins are absent from this top level.

| Appearance | Meaning |
| ---------- | ------- |
| Green alternating with cyan | Calculator passed; blue heartbeat is running |
| Red alternating with magenta | Wrong result or timeout; blue heartbeat is running |
| Blue only, briefly | Calculator has not completed yet |
| No heartbeat | Investigate clock, image loading or LED mapping |

A successful JTAG load is evidence of programming, not an observation
of LED colors. Physical pass requires the user to observe the expected
pattern. This test does not exercise external keys, the MAX7219, SPI,
debouncing, final peripheral constraints or flash boot.

## Commands

Activate the installed OSS CAD Suite (do not install tools from scripts):

```bash
export PATH="/disk1/tmp/oss-cad-suite/bin:$PATH"
just board-selftest test
just board-selftest build
just board-selftest detect
just board-selftest load
```

`test` runs a full internally keyed calculation in Icarus Verilog,
including reset, display capture and RGB polarity; fault injection
checks the wrong-result and watchdog failure paths. `build` synthesizes,
routes with 27 MHz and divided-clock constraints, and packs the image.
Build reports and the bitstream are under work/board/selftest/.

`detect` reads the JTAG identity. `load` requires exactly one detected
GW1NZ-1 ID 0x0100681b, verifies source and bitstream hashes against the
build manifest, and writes SRAM explicitly. There is no flash option.
Power cycling restores whatever is currently in flash, such as the
original color-cycling demo. Reload SRAM to restart a clean test; the
machine RAM initializes on configuration and is not cleared by reset.

Only the core is reused, not the larger 9K UART wrapper. That wrapper
is unsuitable for the 1K with its UART. The core and X_eTaL libraries
are unchanged by this test.

## Recorded checks

JTAG detection on 2026-10-18 reported GW1NZ-1, ID 0x0100681b.
Simulation passed initial zero, all six key handshakes and final 46
in 1755 machine clocks, plus heartbeat and negative-path tests.
Placement/routing reports 444 LUT4 cells plus 158 carry ALU cells,
164 flip-flops and 2 block RAMs. Timing passes both requested clocks:
27 MHz and 0.964 MHz. See docs/board-selftest.md for the load evidence
and observed hardware status.
