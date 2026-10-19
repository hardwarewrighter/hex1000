# Raw keypad diagnostic

Use this SRAM fixture to separate electrical row/column detection from
calculator key assignments. Power cycling restores the calculator flash.
No calculator or operator-button handling runs in this fixture.

Each row is driven low for two seconds in order R1, R2, R3, R4.
Other rows are high impedance. The existing row resistors and pin map
are retained. The display reads `000R000C`, where R is the selected
row (1-4) and C is the mask of columns detected low:

| Column | Mask |
| ------ | ---- |
| None | 0 |
| C1 | 1 |
| C2 | 2 |
| C3 | 4 |
| C4 | 8 |

With no keys held, expect `00010000`, `00020000`, `00030000`,
`00040000` repeatedly. Hold one key for eight seconds to observe all
four rows. S1 should produce `00010001` during R1, S5 `00020001`
during R2, S9 `00030001` during R3 and S13 `00040001` during R4.
The other three rows should show a zero column mask. More than one
column adds the corresponding mask bits. Ignore brief transition frames.

The 2026-10-19 calculator observation was S1-S4 -> 89AB, S5-S8 ->
CDEF, S9-S12 -> 4567, S13-S16 -> CDEF. The user confirmed that
S1, S5, S9 and S13 connect to keypad R1, R2, R3 and R4 respectively;
the wiring looks correct. This does not yet establish the cause.
Do not remap keys based on the duplicated CDEF row alone.

```bash
just keypad-probe test
just keypad-probe build
just keypad-probe load
```

Use OSS CAD Suite on PATH, or append `--tools /path/to/oss-cad-suite/bin`.
Loading checks a single GW1NZ-1 device ID and source/bitstream hashes,
then requires explicit successful CRC. There is no flash-writing action.
Build runs simulation first and checks routed timing. Simulation covers
all 16 positions, inactive-row high impedance, initial SPI display words
and visibility of an injected R1/R4 short. These simulated cases do not
establish the actual wiring fault. Physical observations are recorded
separately in boards/tangnano1k/evidence/keypad-probe.json.

## Output-enable investigation

The original probe reported S1 during rows 2/3/4 but not row 1, and
S5 during rows 1/3/4 but not row 2. Installed apycula TBUF defaults
include `TO=INV`. The candidate constraints explicitly set `TO=SIG`
for all four row outputs; the routed cells retain that setting.
The candidate passes simulation/timing and SRAM CRC. The user confirmed
S1 now reads `00010001`, `00020000`, `00030000`, `00040000`.
This confirms the polarity correction for S1. The same explicit
constraint is applied to the calculator; no row/key remapping is needed.
