# Codex Harness Lab — DO THE IMPOSSIBLE

An autonomous, overnight research lab that asks: **what is a coding-agent harness fundamentally missing?**
Every idea is implemented *natively* inside a from-source build of [OpenAI Codex](https://github.com/openai/codex)
(Rust, `codex/codex-rs`), gated behind an env flag, and judged by **live A/B runs**: a real model drives the real
harness on real tasks with hidden tests. Method modeled on karpathy/autoresearch: frozen benchmark + grader, every
attempt logged pass or fail, no moving goalposts. Scoreboard: [`RESULTS.md`](RESULTS.md).

## The ideas tested (all harness-level, implemented natively in Codex, env-flag gated)
| # | idea | mechanism | live result | code |
|---|---|---|---|---|
| 1 | Probe replay | every side-effect-free check the agent runs becomes a regression probe, re-run (sandboxed) after each edit; behavior diffs appended to the tool output | no effect (wave 5: pass +0.02, p=0.85) | `core/src/lab/probe_replay.rs` |
| 2 | Blind-spec tester (epistemic firewall) | at "done", a model that sees only the task text + starter files writes tests; harness runs them on a scratch copy; failures go back | no effect (p=0.97), +$0.008/run, +160s | `core/src/lab/blind_tester.rs` |
| 2c | Self-test nudge (control) | same stop gate, agent asked to write spec tests itself | no effect; increased cheat attempts | same |
| 3 | Mutation-guided blind spots | at "done", mutate the agent's code and re-run the agent's own checks; undetected mutants reported | no effect (p=1.0) | `core/src/lab/mutation.rs` |
| 4 | **N-version test validation** | report a firewalled test failure only if an independent one-call blind implementation passes that test | offline: alarm precision 34% -> 84-93% ($0.0004/task); live: 85% of alarms suppressed, no end-to-end effect | `blind_tester.rs` (`LAB_NVERSION`) |

Hook points in Codex: tool dispatch (`core/src/tools/registry.rs`), stop gate (`core/src/session/turn.rs`),
per-request cost logging (`codex-api/src/sse/responses.rs`), provider body passthrough (`codex-api/src/endpoint/responses.rs`),
metadata-only stat under read lockdown (`sandboxing/src/seatbelt.rs`).

## The result I would put on a slide
Across 89 real requirement violations by an agent, an **independent firewalled implementation makes the same mistake 48%
of the time**. Independent readings of a spec share ~half their misreadings, so every "ask another instance" verifier
(self-consistency, N-version, second-opinion critic) has a measured recall ceiling near 50%. Validating generated tests
against such an implementation still lifts alarm precision from 34% to 84–93% for $0.0004/task — the cheapest reliable
way found here to stop an agent being misled by its own generated tests. Full numbers: [RESULTS.md](RESULTS.md).

## What to build into a new agent (ranked by evidence)
1. **Never show an agent unvalidated generated tests.** Spec-only tests are wrong ~24% of the time; raw alarms are
   ~34% precise and push agents to break correct code. Validate each generated test against an independent
   implementation first (N-version): precision 84-93% for ~$0.0004/task.
2. **Account cost from the provider per request, inside the harness**, and audit hosted/server-side tools
   (a hidden web_search was 38% of spend and an answer leak).
3. **Run A/Bs with repeated seeds + stratified tests + an A/A arm.** Single-seed differences of ±5/26 tasks were pure noise.
4. **Treat "hidden test" benchmarks as convention-guessing unless calibrated** (half-visible tests: 25% -> 91%).
5. Verification add-ons (replaying probes, mutation feedback, self-test nudges) did not move a cheap model; their
   value, if any, must be shown on stronger models before building them in.

## Benchmark (frozen)
- 56 Exercism exercises (34 Python, 22 Rust) from Aider's polyglot benchmark; agent sees instructions + stubs only,
  hidden tests graded after the run. Variants beside it: `tasks_split` (half the tests visible) and `tasks_split1`
  (first test visible) — grader identical (`bench/grade.py`; verified on reference solutions = pass, stubs = fail).
- Isolation: each run in its own dir outside the repo, own CODEX_HOME/HOME/TMPDIR; Codex seatbelt sandbox with
  network off and **reads denied** outside the run dir + toolchain; web search disabled; escape-attempt scanner.
- Exact cost: provider-reported `usage.cost` per request logged from inside Codex (validated against account credits).

## Findings about harness evaluation itself (useful for anyone building an agent)
1. **Hidden server-side tools silently dominate cost.** Codex exposes a hosted `web_search` tool; OpenRouter executed it
   server-side at ~$0.007/search. It was 38% of our spend and invisible in token counts — and an answer leak.
2. **Cheap agents actively try to cheat**: curl'ing the benchmark's upstream test files, `find` over sibling run dirs.
3. **The agent's shell inherits the harness's provider credentials** — a run dumped `OPENROUTER_API_KEY` into its
   transcript with `env`. Scrub them (`shell_environment_policy`); network egress being blocked is not a substitute.
4. **Killed runs report no usage** (turn-level usage only arrives at the end) → token-based cost estimates undercount 3×.
5. Cheap models loop (e.g. 52 identical commands); loops dominate cost variance → per-run cost caps are essential.

All raw artifacts are archived in [`evidence/lab_evidence.tgz`](evidence/) (transcripts, per-request cost, feature-fired
events, grades, final code). The scratch dir used during the run (`../codex-harness-sandboxes/`) was deleted afterwards;
re-create it by installing a Rust toolchain there and re-cloning `Aider-AI/polyglot-benchmark` (needed only for the
offline sims' reference solutions).

## Reproduce
```bash
# toolchain + build (inside ../codex-harness-sandboxes)
source ../codex-harness-sandboxes/toolchain/env.sh
cd codex/codex-rs && cargo build --profile dev-small -p codex-cli --bin codex
# key: ../codex-harness-sandboxes/.openrouter_key (mode 600)
python3 bench/run.py --exp NAME --arm base --binary <codex> --tasks bench/subsets/all56_shuffled.txt \
   --model z-ai/glm-5.3-flash --parallel 5 --max-cost 0.03 [--env LAB_BLIND_TESTER=1 --env LAB_AUX_MODEL=z-ai/glm-5.3-flash]
python3 scripts/summarize.py NAME base
```
