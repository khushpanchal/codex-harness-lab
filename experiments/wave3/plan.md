# Wave 3 — Exp1 re-run (probe replay) + Exp3 (mutation-guided blind spots), same binary for all arms
Binary: experiment/mutation-blindspots build (contains probe replay + mutation; flags off == baseline code path).
Model z-ai/glm-5.3-flash, tasks bench/subsets/all56_shuffled.txt, 1 seed/arm, arms concurrent (parallel 5 each).
Arms: base (no flags), probe (LAB_PROBE_REPLAY=1), mutation (LAB_MUTATION_BLINDSPOTS=1; records probes, no replay).
Primary: hidden-test pass rate paired vs base (sign test); secondary: paired test fraction (permutation), $/run.
Noise floor reference: wave2 base vs base2 (A/A).
Validity: lab_events show replay / mutation_check fired; escape scan; integrity hash.
Limits: $0.03/run cap, 900s, 60 items; wave budget $1.20 (guard), wall <= 100 min.
