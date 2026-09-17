# Wave 1 — shared live A/B (all arms concurrent, same 56 tasks, same model, same time window)
Model: z-ai/glm-5.3-flash via OpenRouter. Tasks: bench/subsets/all56.txt, 1 seed per arm.
Per-run limits (all arms identical): 900s wall, 60 tool items, $0.05 provider cost -> kill (= fail).
Arms:
- `base`      codex-main-v5, no lab flags
- `base2`     identical to `base` (A/A noise floor; tells us how many discordant pairs pure noise produces)
- `probe`     experiment/probe-replay binary, LAB_PROBE_REPLAY=1                      (Exp1)
- `blind`     experiment/blind-spec-tester binary, LAB_BLIND_TESTER=1 (aux model = glm-5.3-flash) (Exp2)
- `selfnudge` experiment/blind-spec-tester binary, LAB_SELF_TEST_NUDGE=1 (control for Exp2)
Primary metric: hidden-test pass rate; paired per task vs `base`, exact sign test; compare discordance to base2.
Secondary: exact $ per run (provider-reported), wall time, tool calls, test fraction passed.
Validity checks: feature fired (lab_events), escape_hits == 0, bench integrity hash OK, repo git status clean.
Budget: <= $3.50 total for the wave (5 x 56 runs), wall <= 90 min. Overrun => inconclusive.
