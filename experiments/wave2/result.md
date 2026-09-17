# Wave 2 result — INCONCLUSIVE (runners killed externally at ~20:35; blind arm invalid)
Completed: base 26, base2 26+ (A/A), blind 11, selfnudge 15 (glm-5.3-flash, original hidden-test benchmark).
- **A/A noise floor:** base2 vs base on 26 paired tasks: 6 wins / 1 loss (sign p=0.125), test-fraction diff +0.023.
  Identical arms differ by 5 passes -> single-seed 56-task designs cannot detect effects under ~15pp.
- **Blind arm invalid:** the firewalled tester call timed out (curl exit 28 at 300s; glm-5.3-flash reasons >5 min
  when writing a test suite) in 6/10 inspected runs, so the feature mostly did not fire. Fixed: reasoning effort low,
  max_tokens 8000, 150s timeout + retry (tested: 17s).
- selfnudge vs base: 3 wins / 0 losses (n=15), within A/A noise.
Verdict: no conclusion on Exp2; design changed (held-out-test benchmark + repeated seeds on sensitive tasks).
