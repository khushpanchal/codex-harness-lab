# Codex Harness Lab — DO THE IMPOSSIBLE

An autonomous research lab: a real model drives a (modified) OpenAI Codex harness on real coding tasks,
and every harness idea is judged by live A/B numbers (success rate, tokens, cost, wall time).
Methodology modeled on karpathy/autoresearch: frozen benchmark + graders, every attempt logged.

- `codex/` — upstream snapshot of openai/codex (Rust, `codex/codex-rs`)
- `bench/` — frozen tasks and graders, runner
- `experiments/` — one folder per experiment (plan committed before running)
- `RESULTS.md` — live scoreboard

## Validated ideas
None yet.

## Reproduce
TBD as experiments land.
