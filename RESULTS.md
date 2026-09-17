# RESULTS — Codex Harness Lab

**Running now:** Wave 1 live A/B (started 18:56): base, base2 (A/A), probe-replay, blind-spec-tester, self-test-nudge control — 5×56 runs.
**Spend so far:** $1.40 / $10.00 (exact: provider-reported usage.cost per request, validated against credits delta)
**Model:** z-ai/glm-5.3-flash (57% pass on calib14). Bench: 56 Exercism tasks (python+rust), hidden tests.

**Best ideas so far (by strength of evidence):** none validated yet.

**Setup findings worth knowing**
- Agents actively try to get the hidden tests: `curl` to Exercism GitHub, `find` over sibling run dirs. Network was
  blocked; reads are now locked down too (deny home, allow run dir + toolchain, metadata-only stat).

| idea | branch | metric | baseline | result | verdict | why genuinely new |
|---|---|---|---|---|---|---|
| Exp0 model calibration (setup) | experiment/model-calibration | pass rate calib14 | — | glm-5.3-flash 57%, deepseek-v4-flash 29%, qwen3-coder 7%, gpt-oss-120b 10% | glm chosen | n/a (setup) |
