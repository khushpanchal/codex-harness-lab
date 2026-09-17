# Wave 6 — Exp4: N-version test validation (live)
Idea: firewalled spec tests are only reported to the agent if they also PASS on an independent, firewalled one-call
implementation (offline: alarm precision 38% -> 94%). Binary: experiment/nversion-test-filter (cargo sandbox fixed).
Model z-ai/glm-5.3-flash (agent + aux, aux effort low). Tasks: bench/subsets/split1_bugprone11.txt, 3 seeds, arms concurrent:
- base; blind (LAB_BLIND_TESTER, raw alarms); nversion (LAB_BLIND_TESTER + LAB_NVERSION).
Metrics: pass rate + test fraction, stratified permutation by task; exact $/run incl. aux; alarm counts from lab events.
Limits: $0.03/run, 900s, 60 items; budget $1.30 (guard), wall <= 60 min. 99 runs.
