#!/usr/bin/env python3
"""Summarize experiments/<exp>/runs.jsonl per arm, plus paired comparison vs a baseline arm.
usage: summarize.py <exp> [baseline_arm]"""
import json, sys, collections, math, pathlib
exp = sys.argv[1]; base = sys.argv[2] if len(sys.argv) > 2 else None
rows = [json.loads(l) for l in open(pathlib.Path(__file__).parent.parent / "experiments" / exp / "runs.jsonl")]
by = collections.defaultdict(dict)
for r in rows:
    if "error" in r: print("ERROR ROW", r["arm"], r["task"], r["error"][:80]); continue
    by[r["arm"]][(r["task"], r["seed"])] = r
def agg(rs):
    n = len(rs); p = sum(r["passed"] for r in rs)
    tf = sum(r["tests_passed"] / r["tests_total"] for r in rs if r["tests_total"]) / max(1, n)
    return dict(n=n, pass_rate=round(p / max(1, n), 3), passed=p, test_frac=round(tf, 3),
                cost=round(sum(r.get("cost_usd", r["cost_usd_est"]) for r in rs), 4), cost_per=round(sum(r.get("cost_usd", r["cost_usd_est"]) for r in rs) / max(1, n), 5),
                wall_avg=round(sum(r["wall_s"] for r in rs) / max(1, n), 1), in_tok_avg=int(sum(r["input_tokens"] for r in rs) / max(1, n)),
                out_tok_avg=int(sum(r["output_tokens"] for r in rs) / max(1, n)), cmds_avg=round(sum(r["n_commands"] for r in rs) / max(1, n), 1),
                timeouts=sum(r["timed_out"] for r in rs), escapes=sum(bool(r["escape_hits"]) for r in rs),
                lab_events=dict(sum((collections.Counter(r.get("lab_events", {})) for r in rs), collections.Counter())))
for arm, d in sorted(by.items()):
    print(arm, json.dumps(agg(list(d.values()))))
if base and base in by:
    for arm, d in sorted(by.items()):
        if arm == base: continue
        keys = sorted(set(d) & set(by[base]))
        b = sum(by[base][k]["passed"] for k in keys); t = sum(d[k]["passed"] for k in keys)
        win = sum(d[k]["passed"] and not by[base][k]["passed"] for k in keys)
        loss = sum(by[base][k]["passed"] and not d[k]["passed"] for k in keys)
        # exact two-sided sign test on discordant pairs
        nd = win + loss
        pval = min(1.0, 2 * sum(math.comb(nd, i) for i in range(0, min(win, loss) + 1)) / 2 ** nd) if nd else 1.0
        print(f"PAIRED {arm} vs {base}: n={len(keys)} base_pass={b} arm_pass={t} wins={win} losses={loss} sign_test_p={pval:.3f}")
        # secondary metric: fraction of hidden tests passed, paired difference + exact sign-flip permutation p (Monte Carlo)
        import random
        diffs = [(d[k]["tests_passed"] / d[k]["tests_total"] if d[k]["tests_total"] else 0) - (by[base][k]["tests_passed"] / by[base][k]["tests_total"] if by[base][k]["tests_total"] else 0) for k in keys]
        if diffs:
            obs = sum(diffs) / len(diffs); rng = random.Random(0); n_ge = 0
            for _ in range(20000):
                if abs(sum(x if rng.random() < 0.5 else -x for x in diffs) / len(diffs)) >= abs(obs) - 1e-12: n_ge += 1
            cb = sum(by[base][k].get("cost_usd", 0) for k in keys) / len(keys); ca = sum(d[k].get("cost_usd", 0) for k in keys) / len(keys)
            print(f"   test_frac mean diff={obs:+.3f} perm_p={n_ge/20000:.3f} | $/run base={cb:.4f} arm={ca:.4f}")
