# Front reference

Front wraps the existing Hex1000 machine without changing its ROM or
instruction semantics. The second consecutive physical equals press
becomes the core's existing Clear key (20). It clears the calculation,
not the FPGA configuration. A held key is taken once, then all keys
must be released before another press. Multiple keys select the first
physical position; the passive matrix has no anti-ghosting diodes, so
use one key at a time.

| Export | Meaning |
| ------ | ------- |
| fr:Map | Keypad rows CDEF / 89AB / 4567 / 0123, then + - * = |
| fr:ScanReset, fr:s_can | Row timer, scan capture and full-frame debounce |
| fr:KeyReset, fr:k_ey, fr:k_inputs | Release/ready handshake and machine K input |
| fr:d_igits | O captured on rising R0-R7 strobes |
| fr:s_eg | Panel font mapped to MAX7219 segment order |
| fr:SpiReset, fr:w_ord, fr:s_pi | Five initialization commands, then eight digit writes |

The board uses 256 machine clocks per row; four rows form a scan.
After a frame changes, eight more identical frames are required to
accept it (about 9.6 ms worst case after a complete changed frame).
The serial controller sends 16 bits MSB first with CLK low when DIN
changes. LOAD stays high for four clocks between words. It continually
repeats setup and digits so a display enabled after the FPGA catches up.

The board synchronizes physical inputs through two flip-flops before
Front. The optional TXS0108E OE output rises only after a startup delay;
three SPI outputs also work with the 74AHCT125 wiring.

The unchanged calculator still wraps arithmetic on overflow; OuErFLO
and ROM-side RAM clearing remain future work. Configuration initializes
RAM. Clear uses the existing ROM routine. No button resets the FPGA.

The 1100-clock trace from scripts/front-trace.xtl is compared against
all front.v scan, debounce, key, digit and serial state registers. The
board testbench drives physical keypad connectivity, simulates bounce,
receives MAX7219 words and checks calculations and equals-equals clear.
