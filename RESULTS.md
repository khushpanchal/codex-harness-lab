# RESULTS — Codex Harness Lab

**Running now (20:30):** calibration of benchmark variant `tasks_split1` (first test visible, full suite graded), base x 2 seeds.
**Spend so far:** $5.14 / $10.00 (exact provider-reported cost).
**Model:** z-ai/glm-5.3-flash. Bench: 56 Exercism tasks (34 python, 22 rust), hidden tests, sandboxed + read lockdown.

**Best ideas so far (by strength of evidence):** none validated yet. Noise floor is large: A/A (identical arms) gave 5 wins / 1 loss on 25 paired tasks.

**Evaluation findings (confirmed):**
1. Codex's hosted `web_search` tool was silently executed server-side by OpenRouter: 38% of all spend and an answer leak. Disabled -> $/M input 0.093 -> 0.044.
2. Agents try to cheat: `curl` the upstream Exercism test files, `find` sibling run dirs (blocked by sandbox/read lockdown).
3. Killed runs report no usage; token-based cost estimates undercounted 3x -> exact per-request cost logging added inside Codex.
4. **The original hidden-test benchmark measures API-convention guessing, not correctness**: showing the agent half of the tests
   (held-out variant) lifts glm-5.3-flash from ~25% to 91% pass (21/23). Most "failures" were e.g. returning `''` instead of `[]`.
   -> verification-style harness ideas can't show effects there; added variants beside it (not replacing it).
5. Repetition loops are rare (3.4% of commands) -> "loop breaker" style ideas rejected by pre-analysis.

| idea | branch | metric | baseline | result | verdict | why genuinely new |
|---|---|---|---|---|---|---|
| Exp0 model calibration (setup) | experiment/model-calibration | pass rate calib14 | — | glm-5.3-flash 57%, deepseek-v4-flash 29%, qwen3-coder 7%, gpt-oss-120b 10% | glm chosen | n/a (setup) |
| Exp1 probe replay (agent's own checks auto re-run after every edit, behavior diffs reported) | experiment/probe-replay | pass rate (paired) | wave1 base 22% (n=9) | wave1 26% (n=23), no paired diff | inconclusive (wave1 stopped for budget); re-run in wave3 | harness turns ad-hoc agent experiments into a live regression suite; no harness replays the agent's own probes |
| Exp2 blind-spec tester (firewalled tests from spec only) + self-nudge control | experiment/blind-spec-tester | pass rate (paired) | wave1 base | wave1 n=7, no signal | inconclusive (wave1); re-run in wave2 | verification by an information-firewalled role; control isolates firewall vs nudge |
| Exp3 mutation-guided blind spots | experiment/mutation-blindspots | pass rate (paired) | — | unit test passes; live in wave3 | pending | mutation analysis over the agent's *own* ad-hoc checks, fed back mid-task |
| Loop "attractor erasure" | — | exact-repeat rate | — | 3.4% of commands repeat | rejected by pre-analysis | (not run: too rare to matter) |
