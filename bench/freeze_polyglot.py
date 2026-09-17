#!/usr/bin/env python3
"""One-time import of Aider polyglot-benchmark exercises (Exercism, MIT) into bench/tasks.
Layout per task: workspace/ (what the agent sees), hidden/ (tests, never copied to runs), task.json."""
import json, shutil, sys, pathlib
SRC = pathlib.Path(sys.argv[1])  # polyglot-benchmark clone
DST = pathlib.Path(__file__).parent / "tasks" / "polyglot"
for lang in ["python", "rust"]:
    for ex in sorted((SRC / lang / "exercises" / "practice").iterdir()):
        cfg = json.loads((ex / ".meta" / "config.json").read_text())
        files = cfg["files"]
        if lang == "rust" and "[dependencies]" in (ex / "Cargo.toml").read_text() and \
           any("=" in l for l in (ex / "Cargo.toml").read_text().split("[dependencies]")[1].splitlines()):
            continue  # needs crates.io; agent sandbox has no network
        if lang == "rust" and ex.name in {"alphametics","decimal","pig-latin","poker","robot-name"}:
            continue  # reference solution not gradable offline (verified by bench/check_grader.py)
        out = DST / lang / ex.name
        if out.exists(): shutil.rmtree(out)
        (out / "workspace").mkdir(parents=True)
        for f in files["solution"] + [p.relative_to(ex).as_posix() for p in ex.rglob("*") if p.is_file() and not p.relative_to(ex).as_posix().startswith((".meta", ".docs")) and p.relative_to(ex).as_posix() not in files["test"] + files["solution"]]:
            (out / "workspace" / f).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(ex / f, out / "workspace" / f)
        for f in files["test"]:
            (out / "hidden" / f).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(ex / f, out / "hidden" / f)
        docs = (ex / ".docs" / "instructions.md").read_text()
        app = ex / ".docs" / "instructions.append.md"
        if app.exists(): docs += "\n\n" + app.read_text()
        (out / "instructions.md").write_text(docs)
        (out / "task.json").write_text(json.dumps({"id": f"{lang}/{ex.name}", "lang": lang,
            "solution_files": files["solution"], "test_files": files["test"]}, indent=1))
        print(lang, ex.name)
