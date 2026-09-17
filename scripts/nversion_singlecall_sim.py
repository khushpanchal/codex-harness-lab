#!/usr/bin/env python3
"""Same alarm-precision simulation, but the independent implementation is ONE blind model call
(glm-5.3-flash, reasoning effort low) given only the task text + starter files — the cheap harness version.
Implementations are cached in the sandbox; API key read from the sandbox key file, never written."""
import os, sys, glob, json, pathlib, shutil, tempfile, collections, itertools, urllib.request, re
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from nversion_filter_sim import per_test, S, P, R
KEY = (S / ".openrouter_key").read_text().strip()
IMPL_MODEL = os.environ.get("LAB_IMPL_MODEL", "z-ai/glm-5.3-flash")
CACHE = S / ("nversion_impls" if IMPL_MODEL == "z-ai/glm-5.3-flash" else "nversion_impls_" + IMPL_MODEL.replace("/", "_")); CACHE.mkdir(exist_ok=True)
cost = 0.0

def blind_impl(lang, name, sample):
    global cost
    out = CACHE / f"{lang}-{name}-{sample}.txt"
    if out.exists(): return out.read_text()
    ws = R / lang / name / "workspace"; task = json.loads((R / lang / name / "task.json").read_text())
    starter = "\n".join(f"--- {p.relative_to(ws)} ---\n{p.read_text()}" for p in sorted(ws.rglob("*")) if p.is_file())
    target = task["solution_files"][0] if lang == "python" else "src/lib.rs"
    body = {"model": IMPL_MODEL, "reasoning": {"effort": "low"}, "max_tokens": 8000, "usage": {"include": True},
            "messages": [{"role": "system", "content": f"You are an expert programmer. Write the complete contents of {target} implementing the task. Standard library only. Reply with a single fenced code block and nothing else."},
                         {"role": "user", "content": f"# Task\n{(R / lang / name / 'instructions.md').read_text()}\n\n# Starter files\n{starter}"}]}
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    d = json.load(urllib.request.urlopen(req, timeout=200))
    cost += d.get("usage", {}).get("cost", 0) or 0
    text = d["choices"][0]["message"]["content"] or ""
    m = re.search(r"```[^\n]*\n(.*?)```", text, re.S); code = m.group(1) if m else text
    out.write_text(code); return code

tot = collections.Counter(); run = collections.Counter(); suites = {}
for d in sorted(glob.glob(str(S / "runs/wave5/blind/*"))):
    d = pathlib.Path(d); lang, rest = d.name.split("-", 1); name = rest.rsplit("-s", 1)[0]
    tf = d / "labtmp/blind-run-0" / ("test_blind_spec.py" if lang == "python" else "tests/blind_spec.rs")
    if tf.exists() and (lang, name) not in suites: suites[(lang, name)] = tf
for (lang, name), tf in suites.items():
    bases = sorted(glob.glob(str(S / f"runs/wave5/base/{lang}-{name}-s*/work")))
    if not bases: continue
    task = json.loads((R / lang / name / "task.json").read_text()); target = task["solution_files"][0] if lang == "python" else "src/lib.rs"
    ref = pathlib.Path(tempfile.mkdtemp()) / "ref"; shutil.copytree(R / lang / name / "workspace", ref)
    ex = P / lang / "exercises/practice" / name / ".meta"
    shutil.copy(ex / ("example.py" if lang == "python" else "example.rs"), ref / target)
    truth = per_test(lang, ref, tf)
    if not truth: continue
    ind = pathlib.Path(tempfile.mkdtemp()) / "ind"; shutil.copytree(R / lang / name / "workspace", ind)
    (ind / target).write_text(blind_impl(lang, name, 0))
    indep = per_test(lang, ind, tf)
    for a in bases:
        oa = per_test(lang, pathlib.Path(a), tf); c = collections.Counter()
        for t, ok_ref in truth.items():
            if oa.get(t, False): continue
            c["raw_true" if ok_ref else "raw_false"] += 1
            if indep.get(t, False): c["nv_true" if ok_ref else "nv_false"] += 1
        tot.update(c); run["runs"] += 1
        run["raw_only_false"] += int(c["raw_false"] > 0 and c["raw_true"] == 0); run["nv_only_false"] += int(c["nv_false"] > 0 and c["nv_true"] == 0)
        run["true_bug_detectable"] += int(c["raw_true"] > 0); run["nv_catches_true_bug"] += int(c["nv_true"] > 0)
    print(lang, name, "indep impl passes", sum(indep.values()), "/", len(truth), flush=True)
rt, rf, nt, nf = tot["raw_true"], tot["raw_false"], tot["nv_true"], tot["nv_false"]
print(f"raw precision {rt}/{rt+rf}={rt/max(1,rt+rf):.0%}; single-call N-version precision {nt}/{nt+nf}={nt/max(1,nt+nf):.0%}; recall {nt}/{rt}={nt/max(1,rt):.0%}")
print("RUN-LEVEL", dict(run), f"aux cost ${cost:.4f}")
