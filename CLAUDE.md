# CLAUDE.md — Codex Harness Lab operating rules

Reload these every session. They are binding, not suggestions. Tagline: **DO THE IMPOSSIBLE.**

## Objective
- This folder holds a clone of OpenAI Codex (Rust coding-agent harness) plus lab files.
- Understand its agent loop, context handling, tool execution, sandboxing/approvals, sub-agents.
- Invent harness ideas that are *categorically new* (not "harness X has it"). Reject catch-up features.
- Prove each idea with real numbers from a real model driving the real harness on real tasks
  (success rate, cost/task, tokens, latency, wall time, correctness). No number => not an idea.
- Autoresearch style: loop idea -> experiment -> log (pass or fail) -> learn. Depth beats count.

## Secrets
- OpenRouter key lives ONLY in `../codex-harness-sandboxes/.openrouter_key` (mode 600). Load from there.
- Never write the key into the repo, commits, logs, transcripts, or RESULTS.md.
- Before EVERY commit: `scripts/scan_secrets.sh` (greps staged files for `sk-or-v1-[0-9a-f]{20,}`); abort on hit.
- Budget: $10 OpenRouter total. Cheapest capable model for most runs, stronger model only to confirm,
  local ollama (qwen2.5:7b-instruct) for free dry runs. Track spend in RESULTS.md.

## Operating rules
1. Run forever. Never stop, never ask for permission, never idle. Check long jobs every 20–30 min.
2. Touch only this folder (+ its git history) and `../codex-harness-sandboxes/` (agent runs, toolchains,
   caches). Never touch anything else, including ~/.claude.
3. DO NOT MODIFY: benchmark tasks, graders/scoring code, success definitions, recorded baselines,
   the instructions. If a metric is flawed: keep it, add a better one beside it, document why.
   Tempted to redefine a metric to hit a target = cheating; note it in RESULTS.md instead.
   (Files under `bench/tasks/` and `bench/grade*` and `bench/baselines/` are frozen once committed.)
4. No rewrites in other languages, no unrelated refactors. One idea per experiment.
5. Each experiment: branch `experiment/<short-slug>` off main. BEFORE running live, commit a plan:
   metric, number of runs, time limit, cost limit. Kill any single agent run after 15 minutes.
   Over limits => log failed/inconclusive and move on.
6. Commit after every experiment, pass or fail. Message: idea, metric, before/after numbers, verdict.
7. GitHub: private repo under khushpanchal, Actions disabled, snapshot commit of upstream (no history),
   push every commit and branch as you go.
8. RESULTS.md: top = one screen (running now, spend so far, best ideas ranked by evidence strength).
   Below: table `idea | branch | metric | baseline | result | verdict (kept/reverted) | why new`.
   Update + push after every experiment.
9. README.md: what the lab is, validated ideas worth building, how to reproduce each result.
10. This file encodes the rules; keep it current.
11. Parallelize independent experiments. Be the adversarial verifier for any big win before "validated".
12. Targeted experimenter, not token maximizer. Every experiment ends in a clear verdict.
13. MODEL POLICY (verbatim): You (the main session) run all planning, idea generation, and verification;
    this is not to be changed. Keep your own context lean: summarize logs with scripts instead of reading
    them whole, and run long jobs as background scripts rather than agents. When you spawn a sub-agent via
    the Agent tool, explicitly pass model "sonnet" for writing experiment code, "haiku" for simple
    mechanical work, and "opus" only if the experiment requires deep architectural reasoning (note why in
    RESULTS.md).

## Lessons (avoid past mistakes)
- Replays/simulations mislead: agent behavior changes with the harness. Confirm with LIVE A/B on same tasks.
- Broken setups produce believable numbers. Check grader on known pass + known fail; prove the change
  actually altered agent behavior; confirm after each run the real repo was not modified.
- Agents escape sandboxes. Each task runs in a standalone copy outside the repo: own deps, no .git, no links back.
- Capture everything: stdout+stderr, streaming output, saved transcript per run.
- Calibrate tasks: baseline near 0% or 100% can't show a difference.
- Keep top of RESULTS.md short.

## Layout
- `codex/` upstream Codex source snapshot (Rust in `codex/codex-rs`).
- `bench/` tasks (frozen), graders (frozen), runner scripts.
- `experiments/<slug>/` plan.md, results json, analysis.
- `scripts/` helpers (secret scan, spend tracker, summarizers).
- Sandbox: `../codex-harness-sandboxes/` — runs/, toolchains (CARGO_HOME/RUSTUP_HOME), key file.
