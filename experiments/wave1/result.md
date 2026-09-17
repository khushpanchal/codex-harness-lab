# Wave 1 result — INCONCLUSIVE (stopped early, budget)
Stopped at ~90 completed runs (+~25 killed in flight) after $2.15 spend; planned $3.50 for 280 runs was unreachable
because real cost was ~$0.021/run (plan assumed ~$0.012).

Partial numbers (glm-5.3-flash, python tasks only — task order put python first):
| arm | n | pass | test-frac | $/run |
|---|---|---|---|---|
| base | 9 | 22% | 0.69 | 0.024 |
| base2 (A/A) | 23 | 13% | 0.46 | 0.021 |
| probe-replay | 23 | 26% | 0.60 | 0.017 |
| blind-spec-tester | 7 | 14% | 0.37 | 0.026 |
| self-test nudge | 15 | 20% | 0.41 | 0.027 |
Paired vs base on common tasks: no significant differences (n<=9 pairs).

## What we learned (the valuable part)
1. **38% of all spend was OpenRouter server-side web search** triggered by Codex's hosted `web_search` tool
   ($0.007/search; `server_tool_use_details` in usage). It is also an answer leak: the model can search for Exercism
   tests. All wave-1 and calibration numbers are contaminated by it. Fixed: `web_search = "disabled"` for all arms.
2. Frequent cheat attempts even without web search: agents `curl` Exercism test files (blocked by the sandbox).
3. glm-5.3-flash loops (e.g. 52 identical commands) until the cost cap; loops dominate per-task cost variance.
4. Binary pass rate on this set is low (~15-25%) -> weak power. Next waves add a continuous metric beside it
   (fraction of hidden tests passed, paired per task) and pick tasks with low baseline cost.
