# Codex Harness Lab — DO THE IMPOSSIBLE

An autonomous, overnight research lab that asks: **what is a coding-agent harness fundamentally missing?**
Every idea is implemented *natively* inside a from-source build of [OpenAI Codex](https://github.com/openai/codex)
(Rust, `codex/codex-rs`), gated behind an env flag, and judged by **live A/B runs**: a real model drives the real
harness on real tasks with hidden tests. Method modeled on karpathy/autoresearch: frozen benchmark + grader, every
attempt logged pass or fail, no moving goalposts. Scoreboard: [`RESULTS.md`](RESULTS.md).

## The ideas under test (all harness-level, none copied from another harness)
| # | idea | one-line mechanism | code |
|---|---|---|---|
| 1 | **Probe replay** | every side-effect-free check the agent runs becomes a regression probe; after each edit the harness silently re-runs them (sandboxed) and reports which observable behaviors changed | `core/src/lab/probe_replay.rs` |
| 2 | **Blind-spec tester (epistemic firewall)** | at "done", a model call that sees ONLY the task text + starter interface (never the code) writes tests; harness runs them on a scratch copy; failures go back to the agent. Control arm: same stop gate, agent just told to write spec tests itself | `core/src/lab/blind_tester.rs` |
| 3 | **Mutation-guided blind spots** | at "done", harness mutates the agent's code line by line and re-runs the agent's own recorded checks; mutants nobody detects = logic the agent never verified | `core/src/lab/mutation.rs` |

Hook points in Codex: tool dispatch (`core/src/tools/registry.rs`) and the turn stop gate (`core/src/session/turn.rs`).

## Benchmark (frozen)
- 56 Exercism exercises (34 Python, 22 Rust) from Aider's polyglot benchmark; agent sees instructions + stubs only,
  hidden tests graded after the run (`bench/grade.py`; verified on reference solutions = pass, stubs = fail).
- Isolation: each run in its own dir outside the repo, own CODEX_HOME/HOME/TMPDIR; Codex seatbelt sandbox with
  network off and **reads denied** outside the run dir + toolchain; web search disabled; escape-attempt scanner.
- Exact cost: provider-reported `usage.cost` per request logged from inside Codex (validated against account credits).

## Validated ideas
None yet — see RESULTS.md for status.

## Findings about harness evaluation itself (useful for anyone building an agent)
1. **Hidden server-side tools silently dominate cost.** Codex exposes a hosted `web_search` tool; OpenRouter executed it
   server-side at ~$0.007/search. It was 38% of our spend and invisible in token counts — and an answer leak.
2. **Cheap agents actively try to cheat**: curl'ing the benchmark's upstream test files, `find` over sibling run dirs.
3. **Killed runs report no usage** (turn-level usage only arrives at the end) → token-based cost estimates undercount 3×.
4. Cheap models loop (e.g. 52 identical commands); loops dominate cost variance → per-run cost caps are essential.

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
