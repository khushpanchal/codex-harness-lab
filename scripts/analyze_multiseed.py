#!/usr/bin/env python3
"""Multi-seed A/B analysis: per arm vs base, stratified by task.
Statistic: mean over tasks of (arm pass-rate - base pass-rate) and same for test fraction.
p-value: stratified permutation (within each task, arm/base labels of that task's runs are shuffled), 20k draws.
usage: analyze_multiseed.py <exp> [base_arm]"""
import json, sys, random, collections, pathlib
exp = sys.argv[1]; base = sys.argv[2] if len(sys.argv) > 2 else "base"
rows = [json.loads(l) for l in open(pathlib.Path(__file__).parent.parent / "experiments" / exp / "runs.jsonl")]
rows = [r for r in rows if "error" not in r]
by = collections.defaultdict(lambda: collections.defaultdict(list))
for r in rows:
    tf = r["tests_passed"] / r["tests_total"] if r["tests_total"] else 0.0
    by[r["arm"]][r["task"]].append((int(r["passed"]), tf, r.get("cost_usd", 0.0), r["wall_s"], r.get("lab_events", {})))

def stat(a, b, idx):
    tasks = [t for t in a if t in b and a[t] and b[t]]
    return sum(sum(x[idx] for x in a[t]) / len(a[t]) - sum(x[idx] for x in b[t]) / len(b[t]) for t in tasks) / max(1, len(tasks)), tasks

def perm_p(a, b, idx, tasks, obs, draws=20000):
    rng = random.Random(0); ge = 0
    for _ in range(draws):
        tot = 0.0
        for t in tasks:
            pool = [x[idx] for x in a[t]] + [x[idx] for x in b[t]]
            rng.shuffle(pool); na = len(a[t])
            tot += sum(pool[:na]) / na - sum(pool[na:]) / (len(pool) - na)
        if abs(tot / len(tasks)) >= abs(obs) - 1e-12: ge += 1
    return ge / draws

for arm in sorted(by):
    runs = [x for t in by[arm].values() for x in t]
    ev = sum((collections.Counter(x[4]) for x in runs), collections.Counter())
    print(f"{arm:10s} runs={len(runs):3d} pass={sum(x[0] for x in runs)/len(runs):.3f} test_frac={sum(x[1] for x in runs)/len(runs):.3f} "
          f"$/run={sum(x[2] for x in runs)/len(runs):.4f} wall={sum(x[3] for x in runs)/len(runs):.0f}s events={dict(ev)}")
for arm in sorted(by):
    if arm == base or base not in by: continue
    for idx, name in [(0, "pass"), (1, "test_frac")]:
        obs, tasks = stat(by[arm], by[base], idx)
        if tasks:
            print(f"  {arm} vs {base} [{name}] tasks={len(tasks)} mean diff={obs:+.3f} strat_perm_p={perm_p(by[arm], by[base], idx, tasks, obs):.4f}")
