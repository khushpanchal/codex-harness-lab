import json, shutil, subprocess, sys, pathlib, tempfile
R=pathlib.Path("/Users/khush/Experiments/codex-harness"); P=pathlib.Path("/Users/khush/Experiments/codex-harness-sandboxes/polyglot")
sys.path.insert(0,str(R/"bench")); from grade import grade
bad=[]
import os
ROOT=os.environ.get("TASKS_ROOT","bench/tasks/polyglot")
for t in sorted((R/ROOT).glob("*/*")):
    task=json.loads((t/"task.json").read_text()); lang,name=task["lang"],t.name
    stub=grade(t,t/"workspace")
    w=pathlib.Path(tempfile.mkdtemp()); shutil.copytree(t/"workspace",w/"w"); ex=P/lang/"exercises/practice"/name/".meta"
    if lang=="python": shutil.copy(ex/"example.py", w/"w"/task["solution_files"][0])
    else: shutil.copy(ex/"example.rs", w/"w/src/lib.rs")
    sol=grade(t,w/"w")
    flag = "" if (sol["passed"] and not stub["passed"]) else "  <-- BAD"
    if flag: bad.append(task["id"])
    print(task["id"], "stub:",stub["passed"],stub["tests_passed"],"/",stub["tests_total"], "example:",sol["passed"],sol["tests_passed"],"/",sol["tests_total"], flag, flush=True)
print("BAD:",bad)
