#!/usr/bin/env python3
"""Corpus-level stats over every graded run in experiments/*/runs.jsonl (no API cost)."""
import json, glob, collections, math, re
rows = []
for f in glob.glob("experiments/*/runs*.jsonl"):
    if "runs_final" in f: continue
    for l in open(f):
        r = json.loads(l)
        if "error" not in r and r.get("tests_total"): rows.append(r)
y = [int(r["passed"]) for r in rows]
def corr(xs):
    n = len(xs); mx = sum(xs)/n; my = sum(y)/n
    sx = math.sqrt(sum((x-mx)**2 for x in xs)/n); sy = math.sqrt(sum((v-my)**2 for v in y)/n)
    return sum((x-mx)*(v-my) for x, v in zip(xs, y))/(n*sx*sy) if sx and sy else 0
print("runs", len(rows))
for k in ["n_commands", "n_command_fail", "output_tokens", "input_tokens", "wall_s", "n_agent_msgs", "cost_usd"]:
    print(f"{k:16s} corr(pass) {corr([r.get(k, 0) or 0 for r in rows]):+.3f}")
g = collections.Counter()
for r in rows:
    try: tx = open(r["run_dir"] + "/transcript.jsonl").read()
    except Exception: continue
    g[(bool(re.search(r"python3? -|pytest|cargo test|unittest", tx)), bool(r["passed"]))] += 1
print("self-check x pass:", dict(g))
