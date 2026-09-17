# bench/ — FROZEN (do not modify tasks, grader, subsets, baselines once committed)
- `tasks/polyglot/{python,rust}/<exercise>/` — 56 Exercism exercises imported from Aider polyglot-benchmark
  via `freeze_polyglot.py`. `workspace/` is all the agent sees; `hidden/` tests are only used by the grader.
- `grade.py` — success = all hidden tests pass. Verified by `check_grader.py`: every reference solution
  passes and every stub fails (`check_grader_output.txt`; 5 rust tasks needing crates were excluded).
- `run.py` — runner (standalone run dirs in ../codex-harness-sandboxes/runs, 15-min kill, escape scan,
  bench integrity hash before/after). Instrumentation may be extended; success definition may not.
- `subsets/` — fixed task lists.
