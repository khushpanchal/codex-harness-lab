#!/usr/bin/env python3
"""Offline (zero API cost) simulation of the N-version test filter on wave5 blind-tester suites.
For each blind suite T (task, seed): per-test outcome on (a) the Exercism reference solution = truth,
(b) an independent implementation = final code of a base-arm run of the same task (different agent run).
Filter keeps test t iff it passes on (b). Reports how many wrong tests (fail on reference) are removed and
how many correct tests are kept."""
import json, glob, shutil, subprocess, tempfile, pathlib, re, os, collections
S = pathlib.Path("/Users/khush/Experiments/codex-harness-sandboxes")
P = S / "polyglot"; R = pathlib.Path("/Users/khush/Experiments/codex-harness/bench/tasks_split1/polyglot")

def per_test(lang, work, test_file):
    """Returns {test_name: passed}. A hanging suite (model-written infinite loop) yields {}."""
    try:
        return _per_test(lang, work, test_file)
    except subprocess.TimeoutExpired:
        return {}


def _per_test(lang, work, test_file):
    tmp = pathlib.Path(tempfile.mkdtemp()); w = tmp / "w"; shutil.copytree(work, w, ignore=shutil.ignore_patterns("target", "__pycache__"))
    try:
        if lang == "python":
            shutil.copy(test_file, w / "test_blind_spec.py")
            out = subprocess.run(["python3", "-m", "unittest", "-v", "test_blind_spec"], cwd=w, capture_output=True, text=True, timeout=120).stderr
            res = {m.group(1): m.group(2) == "ok" for m in re.finditer(r"^(test\w+) \(.*?\) \.\.\. (ok|FAIL|ERROR)", out, re.M)}
            # multi-line docstring variant: "test_x (...)\ndoc ... ok"
            for m in re.finditer(r"^(test\w+) \(.*?\)\n.*? \.\.\. (ok|FAIL|ERROR)", out, re.M):
                res.setdefault(m.group(1), m.group(2) == "ok")
        else:
            (w / "tests").mkdir(exist_ok=True); shutil.copy(test_file, w / "tests" / "blind_spec.rs")
            out = subprocess.run(["cargo", "test", "--offline", "--test", "blind_spec", "--", "--include-ignored"], cwd=w, capture_output=True, text=True, timeout=300,
                                 env=dict(os.environ, CARGO_TARGET_DIR=str(S / "target-sim"))).stdout
            res = {m.group(1): m.group(2) == "ok" for m in re.finditer(r"^test (\S+) \.\.\. (ok|FAILED)", out, re.M)}
        return res
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

tot = collections.Counter()
for d in sorted(glob.glob(str(S / "runs/wave5/blind/*"))):
    d = pathlib.Path(d); lang, rest = d.name.split("-", 1); name = rest.rsplit("-s", 1)[0]
    tf = d / "labtmp/blind-run-0" / ("test_blind_spec.py" if lang == "python" else "tests/blind_spec.rs")
    if not tf.exists(): continue
    task = json.loads((R / lang / name / "task.json").read_text())
    ref = pathlib.Path(tempfile.mkdtemp()) / "ref"; shutil.copytree(R / lang / name / "workspace", ref)
    ex = P / lang / "exercises/practice" / name / ".meta"
    shutil.copy(ex / ("example.py" if lang == "python" else "example.rs"), ref / (task["solution_files"][0] if lang == "python" else "src/lib.rs"))
    truth = per_test(lang, ref, tf)
    indep_dirs = sorted(glob.glob(str(S / f"runs/wave5/base/{lang}-{name}-s*/work")))
    if not truth or not indep_dirs:
        print(d.name, "skip (no compile vs reference or no independent impl)"); continue
    indep = per_test(lang, pathlib.Path(indep_dirs[0]), tf)
    c = collections.Counter()
    for t, ok in truth.items():
        kept = indep.get(t, False)
        c[("correct" if ok else "wrong") + ("_kept" if kept else "_removed")] += 1
    tot.update(c); print(d.name, dict(c))
print("TOTAL", dict(tot))
w = tot["wrong_kept"] + tot["wrong_removed"]; g = tot["correct_kept"] + tot["correct_removed"]
if w and g:
    print(f"wrong tests removed: {tot['wrong_removed']}/{w} = {tot['wrong_removed']/w:.0%}; correct tests kept: {tot['correct_kept']}/{g} = {tot['correct_kept']/g:.0%}")
