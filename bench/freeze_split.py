#!/usr/bin/env python3
"""Build bench/tasks_split from bench/tasks/polyglot: HELD-OUT TEST variant.
Why (see RESULTS.md): on the original variant most failures are unguessable hidden-API conventions, so harness
verification ideas cannot show an effect. Here the agent SEES every other test (conveying API conventions) and
the grader runs the FULL suite (success = all tests pass, same grade.py). Original benchmark left untouched."""
import ast, json, re, shutil, pathlib
SRC = pathlib.Path(__file__).parent / "tasks" / "polyglot"
DST = pathlib.Path(__file__).parent / "tasks_split" / "polyglot"

def split_python(text):
    tree = ast.parse(text)
    lines = text.splitlines(keepends=True)
    drop = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            tests = [n for n in node.body if isinstance(n, ast.FunctionDef) and n.name.startswith("test")]
            for i, fn in enumerate(tests):
                if i % 2 == 1:
                    start = min([fn.lineno] + [d.lineno for d in fn.decorator_list]) - 1
                    drop.append((start, fn.end_lineno))
    keep = [l for i, l in enumerate(lines) if not any(s <= i < e for s, e in drop)]
    return "".join(keep), len(drop)

def split_rust(text):
    parts = re.split(r"(?m)^(?=#\[test\])", text)
    head, tests = parts[0], parts[1:]
    visible = [t for i, t in enumerate(tests) if i % 2 == 0]
    visible = [re.sub(r"(?m)^#\[ignore\]\n", "", t) for t in visible]
    return head + "".join(visible), len(tests) - len(visible)

if DST.exists():
    shutil.rmtree(DST)
for task_json in sorted(SRC.rglob("task.json")):
    t = task_json.parent; task = json.loads(task_json.read_text())
    out = DST / task["lang"] / t.name
    shutil.copytree(t, out)
    hidden_only = 0
    for f in task["test_files"]:
        full = (t / "hidden" / f).read_text()
        vis, n = split_python(full) if task["lang"] == "python" else split_rust(full)
        hidden_only += n
        (out / "workspace" / f).parent.mkdir(parents=True, exist_ok=True)
        (out / "workspace" / f).write_text(vis)
    task["id"] = "split/" + task["id"]; task["visible_tests"] = task["test_files"]; task["hidden_only_tests"] = hidden_only
    (out / "task.json").write_text(json.dumps(task, indent=1))
    print(task["id"], "hidden-only tests:", hidden_only)
