# Wave 5 — main live A/B on the sensitive regime (split1: first test visible, full suite graded)
Binary: lab/all-features (one binary, flags select arm). Model z-ai/glm-5.3-flash. Tasks: bench/subsets/split1_sensitive16.txt.
Seeds: 3 per task per arm (fresh; calibration runs NOT reused). Arms (all concurrent, parallel 4 each):
- base; probe (LAB_PROBE_REPLAY); blind (LAB_BLIND_TESTER, aux glm-5.3-flash effort low); selfnudge (LAB_SELF_TEST_NUDGE, control for blind);
  mutation (LAB_MUTATION_BLINDSPOTS).
Primary: pass rate; secondary: test fraction; both via stratified permutation test by task (scripts/analyze_multiseed.py,
validated on synthetic data). Cost: exact $/run incl. aux calls. Significance: p < 0.05 AND feature fired.
Limits: $0.03/run, 900s, 60 items; wave budget $2.00 (guard), wall <= 90 min. 240 runs.
