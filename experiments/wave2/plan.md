# Wave 2 — Exp2 re-run: blind-spec tester (information-firewalled tests) vs self-test nudge vs baseline, with A/A
Changes vs wave 1: web_search disabled (was 38% of spend + answer leak), shuffled python/rust order, cost cap $0.03/run.
Model z-ai/glm-5.3-flash. Tasks bench/subsets/all56_shuffled.txt, 1 seed/arm, all arms concurrent (parallel 5 each).
Arms: base (codex-main-v6), base2 (identical, A/A), blind (LAB_BLIND_TESTER=1, aux=glm-5.3-flash), selfnudge (LAB_SELF_TEST_NUDGE=1).
Primary: hidden-test pass rate, paired vs base (sign test). Secondary: paired fraction of hidden tests passed
(permutation test), exact $/run. A win must beat base AND exceed the base2-vs-base discordance.
Limits: $0.03/run cap, 900s/run, 60 tool items; wave budget $2.60 (guard kills beyond), wall <= 100 min.
