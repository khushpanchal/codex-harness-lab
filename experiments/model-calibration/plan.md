# Exp 0 — model calibration (setup, not an idea)
Goal: pick the cheapest model that can do the tasks with a mid-range pass rate (so harness ideas can move it).
Arms: deepseek/deepseek-v4-flash, qwen/qwen3-coder-30b-a3b-instruct, openai/gpt-oss-120b, z-ai/glm-5.3-flash
Tasks: bench/subsets/calib14.txt, 1 seed each = 56 runs, parallel 8 per model.
Metrics: pass rate (hidden tests), mean tests-passed fraction, cost/run, wall/run.
Limits: 15 min per run (hard kill), total wall <= 60 min, total cost <= $1.00.

## Result (2026-09-17)
| model | pass | tests-passed frac | est cost/run | wall avg | timeouts |
|---|---|---|---|---|---|
| z-ai/glm-5.3-flash | 8/14 (57%) | 0.69 | $0.008 (est) | 226s | 1 |
| deepseek/deepseek-v4-flash | 4/14 (29%) | 0.58 | $0.007 (est) | 441s | 2 |
| qwen/qwen3-coder-30b-a3b | 1/14 (7%) | 0.11 | $0.003 | 136s | 1 |
| openai/gpt-oss-120b | 1/10 (10%) | 0.17 | $0.001 | 657s | 7 (killed) |

Verdict: primary model = **z-ai/glm-5.3-flash** (mid-range pass rate -> room to move both ways; fastest capable).
Findings: (1) token-based cost estimate undercounts: account usage rose $1.12 for this batch vs ~$0.30 estimated
(timeouts/killed runs report no usage; cached-token discount may not apply) -> track spend by credits delta.
(2) Escape attempts observed: agents curl'd Exercism test files from GitHub (network blocked by sandbox, got nothing)
and ran `find` over sibling run dirs (found nothing). Runs after this use a read lockdown (see bench/run.py).
