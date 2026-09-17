# RESULTS — Codex Harness Lab

**Running now (22:05):** Wave 6 — live A/B of **N-version test validation** (base vs raw blind tester vs N-version-filtered), 11 bug-prone tasks x 3 seeds.
**Spend so far:** $8.04 / $10.00 (exact provider-reported cost). Wave 6 guard $1.30.
**Model:** z-ai/glm-5.3-flash. Bench: 56 Exercism tasks (python+rust), original hidden-test variant + held-out variants (see below).

**Best ideas so far (by strength of evidence):**
1. **N-version test validation** (new, born from a failed experiment): report a firewalled spec-test failure only if an
   independent one-call blind implementation passes that test. Offline on real agent code: alarm precision **38% -> 94%**
   (recall 52%), runs receiving only false alarms 10/38 -> 1/38, for **$0.0004/task**. Live A/B running (wave 6).
2. Everything else live-tested so far shows **no effect** on glm-5.3-flash: probe replay, blind-spec tester, self-test nudge,
   mutation blind spots (wave 5: pass Δ within ±0.02, all p>0.25, 185 runs, 3 seeds, stratified permutation test).

**Evaluation findings (confirmed, useful to anyone building an agent):**
1. Codex's hosted `web_search` tool ran server-side on OpenRouter: 38% of spend, invisible in token counts, and an answer leak.
2. Hidden-test benchmarks mostly measure API-convention guessing: showing half the tests lifts pass 25% -> 91%.
3. Firewalled "spec-only" test writers are wrong 24% of the time per test; 11/13 suites contain a wrong test -> raw alarms are 31-38% precise and can make agents break correct code.
4. Agents try to cheat (curl upstream tests, search sibling dirs, grep toolchains for canonical data); a "write tests from the spec" nudge increased hunting.
5. Cost accounting: killed runs report no usage (estimates undercount 3x) -> log provider cost per request inside the harness.
6. Identical noise arms (A/A) differed by 5 passes / 26 tasks: single-seed agent A/Bs are close to meaningless.

| idea | branch | metric | baseline | result | verdict | why genuinely new |
|---|---|---|---|---|---|---|
| Exp0 model calibration (setup) | experiment/model-calibration | pass rate calib14 | — | glm-5.3-flash 57%, deepseek-v4-flash 29%, qwen3-coder 7%, gpt-oss-120b 10% | glm chosen | n/a (setup) |
| Exp1 probe replay (agent's own checks auto re-run after every edit, behavior diffs reported) | experiment/probe-replay | pass rate (paired) | wave1 base 22% (n=9) | wave1 26% (n=23), no paired diff | inconclusive (wave1 stopped for budget); re-run in wave3 | harness turns ad-hoc agent experiments into a live regression suite; no harness replays the agent's own probes |
| Exp2 blind-spec tester (firewalled tests from spec only) + self-nudge control | experiment/blind-spec-tester | pass rate (paired) | wave1 base | wave1 n=7, no signal | inconclusive (wave1); re-run in wave2 | verification by an information-firewalled role; control isolates firewall vs nudge |
| Exp3 mutation-guided blind spots | experiment/mutation-blindspots | pass rate (paired) | — | unit test passes; live in wave3 | pending | mutation analysis over the agent's *own* ad-hoc checks, fed back mid-task |
| Loop "attractor erasure" | — | exact-repeat rate | — | 3.4% of commands repeat | rejected by pre-analysis | (not run: too rare to matter) |
| Wave 5 (sensitive regime, 3 seeds): probe replay | experiment/probe-replay | pass / test frac | 0.500 / 0.870 | 0.523 / 0.870 (p=0.85) | reverted | replays the agent's own ad-hoc checks after every edit |
| Wave 5: mutation blind spots | experiment/mutation-blindspots | pass / test frac | 0.500 / 0.870 | 0.523 / 0.823 (p=1.0) | reverted (rust half invalid: sandbox bug) | mutation analysis over the agent's own checks |
| Wave 5: blind-spec tester | experiment/blind-spec-tester | pass / test frac | 0.500 / 0.870 | 0.545 / 0.830 (p=0.97) | reverted (rust half invalid) | epistemic firewall between implementer and tester |
| Wave 5: self-test nudge (control) | experiment/blind-spec-tester | pass / test frac | 0.500 / 0.870 | 0.516 / 0.803 (p=0.92) | reverted | control |
| Benchmark variant: half tests visible | main | pass | 25% (original) | 91% (21/23) | kept as finding (ceiling) | shows failures are convention-guessing |
| N-version test validation (offline sim) | experiment/nversion-test-filter | alarm precision | 38% raw | 94% (recall 52%) | promising -> live wave 6 | independent blind implementation as a noisy oracle for test correctness |
