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
