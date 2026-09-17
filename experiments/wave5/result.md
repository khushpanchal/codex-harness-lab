# Wave 5 result (glm-5.3-flash, split1 sensitive16, 3 seeds; guard stopped at $2.00 after 185/240 runs)
| arm | runs | pass | test frac | $/run | wall | vs base: pass Δ (p) | test-frac Δ (p) |
|---|---|---|---|---|---|---|---|
| base | 44 | 0.500 | 0.870 | 0.0094 | 153s | — | — |
| probe replay | 44 | 0.523 | 0.870 | 0.0079 | 145s | +0.021 (0.85) | +0.001 (0.98) |
| mutation blind spots | 44 | 0.523 | 0.823 | 0.0095 | 160s | −0.000 (1.00) | −0.044 (0.41) |
| blind-spec tester | 22 | 0.545 | 0.830 | 0.0166 | 300s | −0.010 (0.97) | −0.060 (0.33) |
| self-test nudge (control) | 31 | 0.516 | 0.803 | 0.0132 | 216s | −0.010 (0.92) | −0.068 (0.26) |
Stratified permutation test by task (scripts/analyze_multiseed.py; validated on synthetic data).
All features verified firing (probe_replay 55, mutation_check 22, blind_tests_run 33, nudges 26).
**Verdict: all four REVERTED (no measurable effect on pass rate; blind/nudge/mutation slightly lower test fraction).**

## Why the blind tester failed — measured, not guessed (offline, $0.005 total)
- 62/260 (24%) firewalled tests are WRONG vs the Exercism reference solution; 11/13 compiling suites contain >=1 wrong
  test; 4/17 suites don't compile against the real API.
- Alarm precision on real agent code: only **31-38%** of failing blind tests indicate a real bug. 24/54 simulated runs
  receive ONLY false alarms -> the agent "fixes" correct code (e.g. grade-school s0 ended at 0.35 test frac).
## Follow-up idea born here: N-version test validation (scripts/nversion_*_sim.py)
Report a failing firewalled test only if it PASSES on an independent, also-firewalled implementation.
- with a full independent agent run as the second version: precision **31% -> 93%**, recall 78%; false-only-alarm runs 24/54 -> 1/54
- with ONE cheap blind model call as the second version ($0.0004/task): precision **38% -> 94%**, recall 52%;
  false-only-alarm runs 10/38 -> 1/38. Wrong-test share among kept tests 24% -> 3.6%.
Security: 11 escape-flagged runs were attempts only (curl blocked, rg over readable toolchain found nothing).

## Post-hoc bug found (21:55) — affects the Rust half of two arms
The harness-side sandbox for blind-test and mutation runs did not allow writes to the scratch dir itself; cargo creates
`<target>XXXX` sibling temp dirs, so every Rust blind suite failed with "Operation not permitted" (agents received bogus
alarms) and Rust mutation checks never had usable probes. Python halves were unaffected (offline sims above are
unaffected: they ran outside the sandbox). Wave-5 verdicts for blind tester and mutation therefore rest on the Python
tasks only (~half the runs). Fixed in experiment/nversion-test-filter (scratch dir writable).
