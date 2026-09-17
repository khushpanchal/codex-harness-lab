# Corpus analysis over all 635 graded runs (free, no API cost)
- **Agents already self-verify almost always.** In 608/633 runs the agent executed its own code before finishing
  (`python3 -c`, `cargo test`, `unittest`, ...). Those runs pass 44% vs 12% for the 25 runs with no self-check.
  This is observational (hard tasks differ), but it explains the four null results: the harness ideas tested here all add
  *more* verification on top of a loop that already verifies. The missing capability is not "verify more" — it is
  "know which observations to trust" (see the N-version finding).
- **Effort does not predict success.** Correlations with pass: commands −0.06, failed commands −0.03, wall time −0.04,
  cost −0.10, output tokens +0.05, input tokens +0.07. Longer/more expensive runs are, if anything, slightly worse:
  they are the ones that got stuck.
Script: this file's numbers come from `scripts/corpus_stats.py`.

## How good is the agent's informal verification? (from the mutation arm's own telemetry, 23 checks)
The harness mutated the agent's code 289 times and re-ran the agent's own recorded checks: **83% of single-line mutants
were detected** (mean survival 16.7%, median 0%). So a cheap model's ad-hoc `python3 -c` probing already behaves like a
decent test suite on tasks this size — there is little verification headroom, which is the third independent explanation
for the four null results (alongside: verification already happens in 96% of runs; the failures that remain are
convention/spec-ambiguity failures that no amount of self-verification can resolve).
Caveat: 12/41 mutation runs had no usable probes (the agent's checks were bundled with edits), so the checker was idle there.

## Two more free findings from the run corpus
- **Agents tamper with provided tests.** In the `tasks_split1` variant (agent is shown one test and told not to modify
  the test file), **11.6% of runs (50/430) had modified the provided test file** by the end. Harmless here only because
  the grader overwrites all test files with the full hidden suite before grading — which is exactly why a grader must
  never trust files left in the agent's workspace.
- **Each isolated CODEX_HOME costs ~88 MB**: Codex extracts its bundled plugins into `$CODEX_HOME/.tmp/plugins` per run
  (~40 GB across this lab's ~450 runs). Anyone running agent benchmarks at scale should share or pre-warm that directory.
