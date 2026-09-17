# Wave 6 result — Exp4: N-version test validation, live (11 bug-prone tasks x 3 seeds, 99 runs)
| arm | runs | pass | test frac | $/run | vs base pass Δ (p) | vs base test-frac Δ (p) |
|---|---|---|---|---|---|---|
| base | 33 | 0.455 | 0.858 | 0.0073 | — | — |
| blind (raw alarms) | 33 | 0.455 | 0.798 | 0.0169 | −0.000 (1.00) | −0.059 (0.36) |
| nversion (validated alarms) | 33 | 0.485 | 0.878 | 0.0067 | +0.030 (1.00) | +0.020 (0.70) |
**Verdict: no significant end-to-end effect** (as in wave 5). Direction is consistent with the offline evidence:
raw firewalled tests hurt the test fraction, validated ones help slightly, and the filter costs *less* than raw blind
testing ($0.0067 vs $0.0169/run) because it stops the extra continuation rounds caused by false alarms.

## Mechanism did work as designed (live)
- Filter suppressed **85% of raw failing tests** (159 -> 24 validated) across 26 filter events — matching the offline 84-94% precision estimate.
- Alarms are RARE: only 5/28 nversion runs got >=1 validated alarm. That rarity, not the alarm quality, is why the
  end-to-end effect is invisible at this sample size.
- Exploratory subgroup (n=5, post-hoc): runs with a validated alarm ended **+0.13 test fraction vs base on the same task**;
  runs without an alarm −0.02. Wave 7 tests this subgroup directly.
Note: this wave ran while a runaway analysis process pinned the machine (load 82); 14 runs hit the 900s wall limit in all
arms equally (base wall 965s avg). The cost/pass numbers are unaffected, wall-time comparisons for this wave are not usable.
