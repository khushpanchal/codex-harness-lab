#!/usr/bin/env python3
"""FROZEN GRADER. Usage: grade.py <task_dir> <agent_workdir>  -> prints JSON.
success == every hidden test passes. Agent-written files with hidden-test names are overwritten."""
import json, os, re, shutil, subprocess, sys, tempfile, pathlib

def grade(task_dir, workdir):
    task_dir, workdir = pathlib.Path(task_dir), pathlib.Path(workdir)
    task = json.loads((task_dir / "task.json").read_text())
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="grade-"))
    g = tmp / "g"
    shutil.copytree(workdir, g, ignore=shutil.ignore_patterns("target", "__pycache__", ".git"))
    for f in task["test_files"]:
        (g / f).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(task_dir / "hidden" / f, g / f)
    res = {"task": task["id"], "passed": False, "tests_passed": 0, "tests_total": 0, "error": None}
    try:
        if task["lang"] == "python":
            p = subprocess.run([sys.executable, "-m", "unittest", "-v", *[f[:-3].replace("/", ".") for f in task["test_files"]]],
                               cwd=g, capture_output=True, text=True, timeout=180)
            out = p.stdout + p.stderr
            m = re.search(r"Ran (\d+) tests?", out)
            total = int(m.group(1)) if m else 0
            bad = sum(int(x) for x in re.findall(r"(?:failures|errors)=(\d+)", out.split("Ran ")[-1])) if m else total
            res.update(tests_total=total, tests_passed=max(total - bad, 0), passed=(p.returncode == 0 and total > 0))
        else:
            env = dict(os.environ, CARGO_TARGET_DIR=str(tmp / "target"))
            p = subprocess.run(["cargo", "test", "--offline", "--", "--include-ignored"], cwd=g, capture_output=True, text=True, timeout=300, env=env)
            out = p.stdout + p.stderr
            ok = sum(int(x) for x in re.findall(r"test result: \w+\. (\d+) passed", out))
            fail = sum(int(x) for x in re.findall(r"(\d+) failed", " ".join(re.findall(r"test result:.*", out))))
            res.update(tests_total=ok + fail, tests_passed=ok, passed=(p.returncode == 0 and ok > 0))
        res["output_tail"] = out[-1500:]
    except subprocess.TimeoutExpired:
        res["error"] = "timeout"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return res

if __name__ == "__main__":
    print(json.dumps(grade(sys.argv[1], sys.argv[2])))
