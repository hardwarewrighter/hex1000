# Import validation

Validated locally on 2026-10-18:

- Pinned evaluator built using the existing local upstream checkout.
- `just gate` passed: shell syntax, 22 reg-rs baselines across three
  libraries, 156 documentation examples and the 1024-byte ROM check.
- The normal shell lacked HDL tools; the gate explicitly skipped those.
- With /disk1/tmp/oss-cad-suite/bin on PATH, `just check-core fit`
  passed the generated core simulation and reported 438 LUTs,
  81 flip-flops, 62 ALUs (included in the LUT count), 2 block RAMs
  and no multipliers.
- README and library documentation local links were checked.

Imported expected-output files retain their meaningful trailing spaces
(including the ASCII seven-segment font); no baselines were reblessed.

These are software simulation and core-only synthesis results. No 1K
placement, timing, board programming, button test or display test was
performed. The USB-only board setup is recorded in hardware.md.
