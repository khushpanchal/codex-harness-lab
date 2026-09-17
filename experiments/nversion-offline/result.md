# N-version test validation — offline evidence (zero/near-zero API cost)
Data: wave-5 blind-tester suites (glm-5.3-flash, spec-only), wave-5 base-arm agent implementations, Exercism reference
solutions as ground truth. Alarm = firewalled test failing on agent code; TRUE alarm = that test passes on the reference.

| policy (which failing tests reach the agent) | precision | recall of true alarms | extra cost |
|---|---|---|---|
| raw blind tester | 34% (86/256) | 100% | — |
| pass on 1 independent full agent run | 93% (76/82)* | 78% | ~1 agent run |
| pass on 1 one-call blind implementation | 84% (49/58) | 57% | ~$0.0004/task |
| pass on any of 3 one-call impls | 66% (71/107) | 83% | ~$0.0012 |
| pass on majority of 3 | 76% (57/75) | 66% | ~$0.0012 |
| pass on all 3 | 88% (43/49) | 50% | ~$0.0012 |
*earlier subset of runs. Test-level: 24% of spec-only tests are wrong; filter removes 89-90% of wrong tests, keeps 94-95% of correct ones.
Run-level (1 impl): runs receiving only false alarms 10/38 -> 1/38.
Scripts: scripts/nversion_filter_sim.py, nversion_alarm_sim.py, nversion_singlecall_sim.py, nversion_vote_sim.py.
Also (wave-5 cost analysis): blind tester adds +$0.0078/run and +160s wall (p<0.001); probe replay cost -16% not significant (p=0.38).

## Cross-model check (minimax/minimax-m3 writes both the tests and the independent implementation) — INCONCLUSIVE
Only 4 usable runs / 48 alarms (most of its suites did not run against the reference API, and for `forth` its own
independent implementation passed 0/74 of its own tests, so the filter suppressed everything):
raw precision 27% -> N-version 42%, recall 85%, aux cost $0.032. Too small to generalize; a proper cross-model
replication needs ~10x more tasks and is left as the first follow-up.
Note: one minimax-written suite hung forever (infinite loop) — a harness running model-written tests must time-box them.
