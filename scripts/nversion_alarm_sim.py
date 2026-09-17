#!/usr/bin/env python3
"""Offline alarm-precision simulation (zero API cost). For each task with a wave5 blind suite and >=2 base-arm runs:
agent code = base run A, independent impl = base run B (different run), truth = Exercism reference.
An ALARM = blind test failing on agent code. True alarm = that test passes on the reference (a real bug in agent code).
Raw policy: report all alarms. N-version policy: report alarm only if the test passes on the independent impl."""
import sys, glob, json, pathlib, shutil, tempfile, collections, itertools
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from nversion_filter_sim import per_test, S, P, R
tot = collections.Counter(); runs_with_true_bug = collections.Counter()
suites = {}
for d in sorted(glob.glob(str(S / "runs/wave5/blind/*"))):
    d = pathlib.Path(d); lang, rest = d.name.split("-", 1); name = rest.rsplit("-s", 1)[0]
    tf = d / "labtmp/blind-run-0" / ("test_blind_spec.py" if lang == "python" else "tests/blind_spec.rs")
    if tf.exists() and (lang, name) not in suites: suites[(lang, name)] = tf
for (lang, name), tf in suites.items():
    bases = sorted(glob.glob(str(S / f"runs/wave5/base/{lang}-{name}-s*/work")))
    if len(bases) < 2: continue
    task = json.loads((R / lang / name / "task.json").read_text())
    ref = pathlib.Path(tempfile.mkdtemp()) / "ref"; shutil.copytree(R / lang / name / "workspace", ref)
    ex = P / lang / "exercises/practice" / name / ".meta"
    shutil.copy(ex / ("example.py" if lang == "python" else "example.rs"), ref / (task["solution_files"][0] if lang == "python" else "src/lib.rs"))
    truth = per_test(lang, ref, tf)
    if not truth: continue
    outcomes = {b: per_test(lang, pathlib.Path(b), tf) for b in bases}
    for a, b in itertools.permutations(bases, 2):
        c = collections.Counter()
        for t, ok_ref in truth.items():
            if outcomes[a].get(t, False): continue  # no alarm
            true_alarm = ok_ref
            c["raw_true" if true_alarm else "raw_false"] += 1
            if outcomes[b].get(t, False):
                c["nv_true" if true_alarm else "nv_false"] += 1
        tot.update(c)
        runs_with_true_bug["pairs"] += 1
        runs_with_true_bug["raw_any_alarm"] += int(c["raw_true"] + c["raw_false"] > 0)
        runs_with_true_bug["raw_only_false_alarms"] += int(c["raw_false"] > 0 and c["raw_true"] == 0)
        runs_with_true_bug["nv_any_alarm"] += int(c["nv_true"] + c["nv_false"] > 0)
        runs_with_true_bug["nv_only_false_alarms"] += int(c["nv_false"] > 0 and c["nv_true"] == 0)
        runs_with_true_bug["has_true_bug_detectable"] += int(c["raw_true"] > 0)
        runs_with_true_bug["nv_catches_true_bug"] += int(c["nv_true"] > 0)
    print(lang, name, "pairs", len(bases) * (len(bases) - 1), flush=True)
print("ALARMS", dict(tot))
rt, rf, nt, nf = tot["raw_true"], tot["raw_false"], tot["nv_true"], tot["nv_false"]
print(f"raw alarm precision {rt}/{rt+rf} = {rt/max(1,rt+rf):.0%}; N-version precision {nt}/{nt+nf} = {nt/max(1,nt+nf):.0%}; recall of true alarms {nt}/{rt} = {nt/max(1,rt):.0%}")
print("RUN-LEVEL", dict(runs_with_true_bug))
