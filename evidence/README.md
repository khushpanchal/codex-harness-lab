# evidence/ — raw artifacts behind every number in RESULTS.md
`lab_evidence.tgz` (23 MB) contains, for all ~700 live runs:
- `runs/<wave>/<arm>/<task>-s<seed>/transcript.jsonl` — the full streamed Codex session (every tool call and output)
- `.../usage.jsonl` — provider-reported tokens **and cost per request** (the basis of all $ figures)
- `.../lab_events.jsonl` — proof each lab feature fired (probe_recorded, probe_replay, blind_tests_run, nversion_filter, mutation_check)
- `.../grade.json` — frozen-grader output, and `.../work/` — the agent's final code
- generated blind-spec test suites, the independent one-call implementations (glm / deepseek / minimax), and runner logs

Redaction: one transcript (`wave2/blind/python-wordy-s0`) contained the OpenRouter key because the agent ran `env` —
Codex passes `OPENROUTER_API_KEY` into the model's shell. It is replaced with `sk-or-v1-<REDACTED-BY-LAB>`; the archive
is verified key-free. **Lesson for harness design: the agent's shell inherits the harness's provider credentials.**
Network egress was blocked in every run, so nothing could be exfiltrated, but a harness should scrub provider secrets
from the tool environment (Codex has `shell_environment_policy` for this; the lab did not set it).

Not included (regenerable / bulky): cargo target dirs, the per-run CODEX_HOME dirs (~88 MB each — Codex extracts its
bundled plugins per home), the Rust toolchain, and the upstream polyglot clone (re-clone from Aider-AI/polyglot-benchmark
to re-run the offline sims, which need its reference solutions).
