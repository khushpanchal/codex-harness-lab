#!/usr/bin/env python3
"""Offline: N-version filter with k=3 independent one-call implementations. Policies:
any (>=1 impl passes), majority (>=2), all (3). Same alarm precision/recall accounting as nversion_singlecall_sim."""
import sys, glob, json, pathlib, shutil, tempfile, collections
sys.argv = [sys.argv[0]]
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import importlib.util
spec = importlib.util.spec_from_file_location("sc", pathlib.Path(__file__).parent / "nversion_singlecall_sim.py")
# reuse helpers without running the module's main loop: copy the function definitions we need
src = (pathlib.Path(__file__).parent / "nversion_singlecall_sim.py").read_text().split("tot = collections.Counter(); run")[0]
ns = {"__file__": str(pathlib.Path(__file__).parent / "nversion_singlecall_sim.py"), "__name__": "sc"}; exec(compile(src, "sc", "exec"), ns)
per_test, blind_impl, S, R, P = ns["per_test"], ns["blind_impl"], ns["S"], ns["R"], ns["P"]
suites = {}
for d in sorted(glob.glob(str(S / "runs/wave5/blind/*"))):
    d = pathlib.Path(d); lang, rest = d.name.split("-", 1); name = rest.rsplit("-s", 1)[0]
    tf = d / "labtmp/blind-run-0" / ("test_blind_spec.py" if lang == "python" else "tests/blind_spec.rs")
    if tf.exists() and (lang, name) not in suites: suites[(lang, name)] = tf
tot = collections.Counter()
for (lang, name), tf in suites.items():
    bases = sorted(glob.glob(str(S / f"runs/wave5/base/{lang}-{name}-s*/work")))
    if not bases: continue
    task = json.loads((R / lang / name / "task.json").read_text()); target = task["solution_files"][0] if lang == "python" else "src/lib.rs"
    ref = pathlib.Path(tempfile.mkdtemp()) / "ref"; shutil.copytree(R / lang / name / "workspace", ref)
    ex = P / lang / "exercises/practice" / name / ".meta"
    shutil.copy(ex / ("example.py" if lang == "python" else "example.rs"), ref / target)
    truth = per_test(lang, ref, tf)
    if not truth: continue
    indeps = []
    for k in range(3):
        ind = pathlib.Path(tempfile.mkdtemp()) / "ind"; shutil.copytree(R / lang / name / "workspace", ind)
        (ind / target).write_text(blind_impl(lang, name, k)); indeps.append(per_test(lang, ind, tf))
    for a in bases:
        oa = per_test(lang, pathlib.Path(a), tf)
        for t, ok_ref in truth.items():
            if oa.get(t, False): continue
            votes = sum(1 for i in indeps if i.get(t, False))
            tag = "true" if ok_ref else "false"
            tot["raw_" + tag] += 1
            for pol, need in [("k1", 1), ("any3", 1), ("maj3", 2), ("all3", 3)]:
                v = int(indeps[0].get(t, False)) if pol == "k1" else votes
                if v >= need: tot[pol + "_" + tag] += 1
    print(lang, name, flush=True)
for pol in ["raw", "k1", "any3", "maj3", "all3"]:
    t, f = tot[pol + "_true"], tot[pol + "_false"]
    print(f"{pol}: precision {t}/{t+f} = {t/max(1,t+f):.0%}  recall {t}/{tot['raw_true']} = {t/max(1,tot['raw_true']):.0%}")
print("aux cost this run $%.4f" % ns["cost"])
