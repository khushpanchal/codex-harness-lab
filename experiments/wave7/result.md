# Wave 7 result — N-version validation on the alarm subgroup (5 tasks x 4 seeds, 38 runs) — NOT EVIDENCE
| arm | runs | pass | test frac | $/run |
|---|---|---|---|---|
| base | 20 | 0.400 | 0.787 | 0.0065 |
| nversion | 18 | 0.611 | 0.922 | 0.0130 |
Stratified permutation: pass +0.200 (p=0.23), test fraction +0.132 (p=0.017).

## Adversarial verification (this is why the result is rejected)
If validated alarms caused the gain, runs that received an alarm should improve more than runs that received none.
They did not: mean test fraction vs base on the same task was **+0.063 in the 3 runs with a validated alarm** and
**+0.167 in the 15 runs without any alarm**. In 15/18 treated runs the harness injected nothing at all, so the arm was
behaviorally identical to base; the difference is therefore chance (it is also a secondary metric, chosen among several,
on 5 tasks). **Verdict: no causal evidence that N-version validation improves task outcomes.** The mechanism-level
claims (alarm precision, 85% suppression) stand; the end-to-end claim does not.
