# RESULTS — Codex Harness Lab

**Status (01:30):** all waves finished; budget spent. Nothing is running.
**Spend:** $9.66 / $10.00 (exact provider-reported cost per request, validated against account credits).
**Setup:** OpenAI Codex built from source; 4 new harness features implemented natively in Rust behind env flags;
model z-ai/glm-5.3-flash via OpenRouter; 56 Exercism tasks (python+rust) with hidden tests + two held-out variants;
~700 live agent runs, each in an isolated sandbox (no network, reads denied outside the run dir).

### Headline
1. **Four original harness ideas were implemented and live-tested. All four show no effect** on task success for a
   cheap model (wave 5, 185 runs, 3 seeds/task, stratified permutation tests: |Δpass| ≤ 0.02, p > 0.25).
2. **The strongest result is a measurement, not a feature:** *spec-only ("firewalled") tests — the kind agents are
   routinely asked to trust — are wrong 24% of the time, and their failure alarms are only 31–38% precise.* Feeding them
   to an agent makes it break correct code.
3. **N-version test validation fixes that signal for $0.0004/task:** report a firewalled test failure only if an
   independent one-call blind implementation passes that test → alarm precision **34% → 84–93%** (recall 52–78%),
   runs receiving only-false alarms **10/38 → 1/38**; live it suppressed **85%** of raw failures and cost 2.5× *less*
   than raw blind testing. **It still did not move end-to-end success** (wave 6, 99 runs, p≈0.7), because validated
   alarms fire in only ~18% of runs. A promising wave-7 subgroup result (+0.13 test fraction, p=0.017) was **rejected by
   my own adversarial check** — runs with no alarm improved more than runs with alarms.

### The sharpest number of the night
Across 89 real requirement violations by the agent, an **independent firewalled implementation makes the same mistake
48% of the time**. Independent readings of a spec share about half their misreadings — so "ask another instance"
verification (self-consistency, N-version, second-opinion critics) has a hard recall ceiling near 50%, measured, not
argued. Beating it requires new *information* (a different rendering of the spec, an existing caller, a user question),
not more samples.

### Why all four ideas were null (three independent measurements)
- Agents **already self-verify in 96% of runs** (608/633); those runs pass 44% vs 12% without.
- Their informal checks are **good**: the mutation arm's telemetry shows the agent's own probes detect **83% of
  single-line mutants** (median 100%).
- What is left is not under-verification but **spec/API ambiguity**: showing half the hidden tests moves pass 25% → 91%.
So "make the agent verify more" is the wrong axis for this regime — the leverage is in *which claims to trust*
(N-version) and in resolving interface ambiguity (see `experiments/NEXT.md`).

### What I'd build into a new agent (evidence-ranked)
1. Never show an agent generated tests that have not been validated against an independent implementation.
2. Account cost inside the harness from provider-reported per-request usage, and audit hosted/server-side tools:
   Codex's hosted `web_search`, executed server-side, was **38% of all spend**, invisible in token counts — and an answer leak.
3. A/B agent changes with repeated seeds + an A/A arm + stratified tests. My A/A arms differed by 5 passes / 26 tasks.
4. Time-box and sandbox anything model-written that the harness executes (one model-written suite hung forever; cargo
   needs its scratch *parent* writable, which silently invalidated a whole arm's Rust half until I found it).
5. Hidden-test benchmarks measure API-convention guessing unless calibrated: showing half the tests took 25% → 91%.
6. Never grade files the agent could touch: 11.6% of runs modified the test file they were told not to modify.
7. **Scrub provider credentials from the agent's shell.** Codex passes `OPENROUTER_API_KEY` into the model's tool
   environment; one run dumped it into its transcript via `env`. Egress was blocked here, but a harness should set
   `shell_environment_policy` (or equivalent) so the agent never sees the keys that pay for it.

---

## Experiment table
| idea | branch | metric | baseline | result | verdict | why this is genuinely new |
|---|---|---|---|---|---|---|
| **Probe replay** — every side-effect-free check the agent runs becomes a regression probe; re-run sandboxed after each edit, behavior diffs appended to the tool output | experiment/probe-replay | pass / test frac (wave 5, 44 runs/arm) | 0.500 / 0.870 | 0.523 / 0.870 (p=0.85 / 0.98) | reverted | no harness replays the agent's *own ad-hoc* experiments as a growing regression suite |
| **Blind-spec tester** — at "done", a model that never sees the code writes tests from the spec; harness runs them in a scratch copy | experiment/blind-spec-tester | pass / test frac | 0.500 / 0.870 | 0.545 / 0.830 (p=0.97 / 0.33); +$0.008/run, +160s | reverted | verification by an information-firewalled role, enforced by the harness |
| **Self-test nudge** (control for the above) | experiment/blind-spec-tester | pass / test frac | 0.500 / 0.870 | 0.516 / 0.803 (p=0.92 / 0.26) | reverted | isolates "firewall" from "nudge"; also raised cheat attempts |
| **Mutation-guided blind spots** — mutate the agent's code, re-run the agent's own checks, report undetected mutants | experiment/mutation-blindspots | pass / test frac | 0.500 / 0.870 | 0.523 / 0.823 (p=1.0 / 0.41) | reverted | mutation analysis over the agent's own informal checks, fed back mid-task |
| **N-version test validation** (offline, on real agent code) | experiment/nversion-test-filter | alarm precision / recall | 34% / 100% | **84%** / 57% (one-call impl, $0.0004); 93% / 78% (full agent run) | mechanism validated | an independent blind implementation as a noisy oracle for *test* correctness |
| **N-version test validation** (live) | experiment/nversion-test-filter | pass / test frac (wave 6, 33/arm) | 0.455 / 0.858 | 0.485 / 0.878 (p=1.0 / 0.70); 85% of raw alarms suppressed; $0.0067/run vs $0.0169 raw | kept as mechanism, **not** as a win | — |
| N-version, alarm subgroup (wave 7) | experiment/nversion-test-filter | test frac | 0.787 | 0.922 (p=0.017) | **rejected by adversarial check** (no-alarm runs improved more) | — |
| Benchmark variant: half the tests visible | main | pass | 25% | 91% (21/23) | kept as finding | isolates convention-guessing from reasoning |
| N-version with a *different-family* independent implementer (offline) | experiment/nversion-test-filter | alarm recall / precision | 52% / 88% (same family) | 25% / 90% | rejected (lowers coverage) | tests whether implementer diversity raises the alarm rate — it does not |
| Loop "attractor erasure" | — | exact-repeat rate | — | repeats are 3.4% of commands | rejected before running | not worth the budget |

## Waves (chronological; every attempt logged, pass or fail)
| wave | what | outcome |
|---|---|---|
| 0 | model calibration (4 models × 14 tasks) | glm-5.3-flash chosen (57% pass); gpt-oss-120b hangs, qwen3-coder 7% |
| 1 | first 5-arm A/B | inconclusive, stopped on budget; found the hidden web_search spend + answer leak |
| 2 | re-run with web search off + A/A | inconclusive; **A/A noise floor 6 wins / 1 loss on 26 tasks**; blind arm invalid (aux call timeouts) |
| 3 | probe/mutation re-run | killed externally after 7 runs; jobs now launched fully detached |
| split calib | half-visible-tests variant | 91% pass — ceiling, unusable for A/B, but a strong benchmark-validity finding |
| split1 calib | first-test-visible variant, 2 seeds × 56 | 34% pass — the sensitive regime; 16 sensitive tasks selected |
| 5 | 5 arms × 16 tasks × 3 seeds (185 runs) | all four ideas reverted; offline autopsy produced the N-version idea |
| 6 | N-version live (99 runs) | mechanism works (85% suppression), no end-to-end effect |
| 7 | N-version on the alarm subgroup (38 runs) | apparent win rejected by adversarial check |

## Reproducing
`README.md` has the commands; every wave has `experiments/<wave>/{plan.md,result.md,runs_final.jsonl,analysis.txt}`.
Tools: `scripts/analyze_multiseed.py` (validated on synthetic data), `scripts/nversion_*_sim.py` (offline, near-zero cost).

## A/B fairness audit (static)
Every lab code path in Codex is behind an env flag (`registry.rs` probe hooks, `turn.rs` stop gates, `LAB_USAGE_LOG`,
`LAB_EXTRA_BODY`, `LAB_ALLOW_READ_METADATA`), so the baseline arm runs the *same binary* with the features off.
The one unconditional call is `lab::snapshot_starter_once()` (reads the workspace's text files once, before the first
tool call); it is identical in every arm and does not change what the model sees.

## Honest limitations
- One agent model (glm-5.3-flash), one task family (Exercism). A cross-model check of the N-version mechanism
  (minimax-m3) is inconclusive at n=4 runs.
- Wave 5's blind-tester and mutation arms had their Rust half invalidated by a harness sandbox bug (found post-hoc,
  fixed); those verdicts rest on the Python half.
- These nulls bound effects for a *cheap* model on *small* tasks; they do not rule out gains on long-horizon work,
  where these mechanisms have more room — that is the first follow-up I would run.
