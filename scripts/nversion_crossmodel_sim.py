#!/usr/bin/env python3
"""Cross-model check of N-version test validation (offline).
A stronger model writes BOTH the spec-only test suite and the independent one-call implementation; alarms are evaluated
against real glm-5.3-flash agent implementations (wave5/wave6 base runs), truth = Exercism reference solution.
usage: nversion_crossmodel_sim.py <model>"""
import sys, glob, json, pathlib, shutil, tempfile, collections, urllib.request, re
sys.path.insert(0, str(pathlib.Path(__file__).parent))
src = (pathlib.Path(__file__).parent / "nversion_singlecall_sim.py").read_text().split("tot = collections.Counter(); run")[0]
ns = {"__file__": str(pathlib.Path(__file__).parent / "nversion_singlecall_sim.py"), "__name__": "sc"}
exec(compile(src, "sc", "exec"), ns)
per_test, S, R, P, KEY = ns["per_test"], ns["S"], ns["R"], ns["P"], ns["KEY"]
MODEL = sys.argv[1]; CACHE = S / f"crossmodel-{MODEL.replace('/', '_')}"; CACHE.mkdir(exist_ok=True)
cost = 0.0

def call(system, user, tag, lang, name):
    global cost
    f = CACHE / f"{lang}-{name}-{tag}.txt"
    if f.exists(): return f.read_text()
    body = {"model": MODEL, "max_tokens": 9000, "usage": {"include": True},
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    d = json.load(urllib.request.urlopen(req, timeout=600))
    cost += d.get("usage", {}).get("cost", 0) or 0
    text = d["choices"][0]["message"]["content"] or ""
    m = re.search(r"```[^\n]*\n(.*?)```", text, re.S)
    f.write_text(m.group(1) if m else text); return f.read_text()

tot = collections.Counter(); run = collections.Counter()
tasks = sorted({(p.parent.parent.name, p.parent.name) for p in R.glob("*/*/task.json")})
targets = [(l, n) for l, n in tasks if glob.glob(str(S / f"runs/wave*/base/{l}-{n}-s*/work"))][:12]
for lang, name in targets:
    task = json.loads((R / lang / name / "task.json").read_text()); target = task["solution_files"][0] if lang == "python" else "src/lib.rs"
    ws = R / lang / name / "workspace"
    starter = "\n".join(f"--- {p.relative_to(ws)} ---\n{p.read_text()}" for p in sorted(ws.rglob("*")) if p.is_file())
    spec = (R / lang / name / "instructions.md").read_text()
    rules = ("Write a Python `unittest` module (saved as test_blind_spec.py next to the solution, run with `python3 -m unittest test_blind_spec`). Standard library only."
             if lang == "python" else f"Write a Rust integration test file (saved as tests/blind_spec.rs, run with `cargo test --test blind_spec`). Import with `use {name.replace('-', '_')}::*;`. No external crates.")
    tests = call("You are a meticulous test engineer. You never see the implementation. Write a thorough unit test suite for the behavior the description requires, including edge cases and stated error rules. Do not invent unstated requirements. Reply with a single fenced code block.",
                 f"{rules}\n\n# Task description\n{spec}\n\n# Starter files\n{starter}", "tests", lang, name)
    impl = call(f"You are an expert programmer. Write the complete contents of {target} implementing the task. Standard library only. Reply with a single fenced code block and nothing else.",
                f"# Task\n{spec}\n\n# Starter files\n{starter}", "impl", lang, name)
    tmp = pathlib.Path(tempfile.mkdtemp()); tf = tmp / ("test_blind_spec.py" if lang == "python" else "blind_spec.rs"); tf.write_text(tests)
    ref = tmp / "ref"; shutil.copytree(ws, ref); shutil.copy(P / lang / "exercises/practice" / name / ".meta" / ("example.py" if lang == "python" else "example.rs"), ref / target)
    truth = per_test(lang, ref, tf)
    if not truth: print(lang, name, "suite does not run against reference -> skipped"); continue
    ind = tmp / "ind"; shutil.copytree(ws, ind); (ind / target).write_text(impl)
    indep = per_test(lang, ind, tf)
    for a in sorted(glob.glob(str(S / f"runs/wave*/base/{lang}-{name}-s*/work")))[:3]:
        oa = per_test(lang, pathlib.Path(a), tf); c = collections.Counter()
        for t, ok_ref in truth.items():
            if oa.get(t, False): continue
            c["raw_true" if ok_ref else "raw_false"] += 1
            if indep.get(t, False): c["nv_true" if ok_ref else "nv_false"] += 1
        tot.update(c); run["runs"] += 1
        run["raw_only_false"] += int(c["raw_false"] > 0 and c["raw_true"] == 0); run["nv_only_false"] += int(c["nv_false"] > 0 and c["nv_true"] == 0)
    wrong = sum(1 for v in truth.values() if not v)
    print(lang, name, f"tests={len(truth)} wrong_vs_reference={wrong} indep_passes={sum(indep.values())}", flush=True)
rt, rf, nt, nf = tot["raw_true"], tot["raw_false"], tot["nv_true"], tot["nv_false"]
print(f"MODEL {MODEL}: raw precision {rt}/{rt+rf}={rt/max(1,rt+rf):.0%} | N-version precision {nt}/{nt+nf}={nt/max(1,nt+nf):.0%} | recall {nt}/{rt}={nt/max(1,rt):.0%}")
print("RUN-LEVEL", dict(run), f"aux cost ${cost:.4f}")
