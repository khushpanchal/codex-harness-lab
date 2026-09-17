#!/usr/bin/env python3
"""Lab runner: real Codex binary + real model (OpenRouter/ollama) on frozen bench tasks.

Each run gets a standalone dir OUTSIDE the repo: work/ (copied workspace, no .git, no links),
home/ (CODEX_HOME + HOME). Transcript (codex --json stream), stderr, grade, metrics are saved.
One JSON line per run is appended to experiments/<exp>/runs.jsonl in the repo.

usage: run.py --exp SLUG --arm NAME --binary PATH --tasks FILE|all --seeds 1 [--env K=V ...] [-c key=val ...]
"""
import argparse, concurrent.futures as cf, hashlib, json, os, pathlib, shutil, signal, subprocess, sys, time

REPO = pathlib.Path(__file__).resolve().parent.parent
SANDBOX = REPO.parent / (REPO.name + "-sandboxes")
TASKS = REPO / "bench" / "tasks"
sys.path.insert(0, str(REPO / "bench"))
from grade import grade  # frozen grader

PRICES = {  # USD per token: (prompt, cached_read, completion) from OpenRouter /models on 2026-09-17
    "deepseek/deepseek-v4-flash": (0.088606e-6, 0.0177212e-6, 0.177212e-6),
    "qwen/qwen3-coder-30b-a3b-instruct": (0.07e-6, 0.07e-6, 0.28e-6),
    "openai/gpt-oss-120b": (0.037e-6, 0.037e-6, 0.17e-6),
    "z-ai/glm-5.3-flash": (0.09e-6, 0.018e-6, 0.3e-6),
    "deepseek/deepseek-v4-pro-0813": (1.32e-6, 0.044e-6, 3.96e-6),  # peak-hour price (upper bound)
    "minimax/minimax-m3": (0.3e-6, 0.06e-6, 1.2e-6),
    "qwen2.5:7b-instruct": (0, 0, 0),
}
SUFFIX = ("\n\n---\nYou are working in the current directory, which contains the starter files. "
          "Implement the solution in: {files}. Hidden unit tests will be run against your code after you finish "
          "(tests for this exercise are not provided). Use only the standard library.")


def tree_hash(p):
    h = hashlib.sha256()
    for f in sorted(p.rglob("*")):
        if f.is_file():
            h.update(f.relative_to(p).as_posix().encode()); h.update(f.read_bytes())
    return h.hexdigest()[:16]


def tree_hash_file(f):
    return hashlib.sha256(f.read_bytes()).hexdigest()[:16]


def config_toml(model, provider, rdir):
    if provider == "ollama":
        prov = '[model_providers.lab]\nname = "ollama"\nbase_url = "http://localhost:11434/v1"\nwire_api = "responses"\n'
    else:
        prov = ('[model_providers.lab]\nname = "OpenRouter"\nbase_url = "https://openrouter.ai/api/v1"\n'
                'env_key = "OPENROUTER_API_KEY"\nwire_api = "responses"\n')
    # Read lockdown: everything under the user's home is unreadable except this run dir and the toolchain
    # (requires LAB_ALLOW_READ_METADATA=1 so toolchains can canonicalize paths; see sandboxing/src/seatbelt.rs).
    home_root = "/" + "/".join(REPO.parts[1:3])
    return (f'model = "{model}"\nmodel_provider = "lab"\napproval_policy = "never"\n'
            f'model_catalog_json = "{REPO / "bench/config/model_catalog.json"}"\n'
            'check_for_update_on_startup = false\nweb_search = "disabled"\ndefault_permissions = "lab"\n\n'
            f'[permissions.lab]\nextends = ":workspace"\n\n[permissions.lab.filesystem]\n'
            f'"{home_root}" = "deny"\n"{rdir}" = "write"\n"{SANDBOX / "toolchain"}" = "read"\n\n' + prov)


def scan_escape(transcript_text, rdir):
    """Flag commands touching absolute paths outside this run's dir under the user's tree, or answer-ish names."""
    import re
    hits = []
    for line in transcript_text.splitlines():
        try:
            d = json.loads(line)
        except Exception:
            continue
        item = d.get("item") or {}
        if item.get("type") == "command_execution" and d.get("type") == "item.completed":
            cmd = item.get("command", "")
            paths = re.findall(r"(/Users/[^\s'\"]*)", cmd)
            bad = [x for x in paths if not x.startswith(str(rdir))]
            if bad or any(b in cmd for b in (".meta", "example.py", "example.rs", "exercism", "hidden/", "../..")):
                hits.append(cmd[:200])
    return hits


def usage_cost(rdir):
    """Exact spend for this run: sum of provider-reported usage.cost per request (LAB_USAGE_LOG)."""
    total = 0.0
    f = rdir / "usage.jsonl"
    if f.exists():
        for line in f.read_text().splitlines():
            try:
                total += float(json.loads(line).get("cost") or 0)
            except Exception:
                pass
    return total


def run_one(args, task_id, seed):
    tdir = TASKS / task_id
    task = json.loads((tdir / "task.json").read_text())
    rdir = SANDBOX / "runs" / args.exp / args.arm / f"{task_id.split('/')[-2]}-{task_id.split('/')[-1]}-s{seed}"
    if rdir.exists():
        shutil.rmtree(rdir)
    work, home = rdir / "work", rdir / "home"
    shutil.copytree(tdir / "workspace", work)
    home.mkdir(parents=True)
    (rdir / "tmp").mkdir()
    (home / "config.toml").write_text(config_toml(args.model, args.provider, rdir))
    prompt = (tdir / "instructions.md").read_text() + SUFFIX.format(files=", ".join(task["solution_files"]))
    env = {
        "PATH": f"{SANDBOX}/toolchain/shims:{SANDBOX}/toolchain/cargo/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin",
        "HOME": str(home), "CODEX_HOME": str(home),
        "RUSTUP_HOME": f"{SANDBOX}/toolchain/rustup", "CARGO_HOME": f"{SANDBOX}/toolchain/cargo",
        "CARGO_TARGET_DIR": str(rdir / "target"), "LANG": "en_US.UTF-8", "TERM": "dumb",
        "LAB_ALLOW_READ_METADATA": "1", "TMPDIR": str(rdir / "tmp"),
    }
    if args.provider != "ollama":
        env["OPENROUTER_API_KEY"] = (SANDBOX / ".openrouter_key").read_text().strip()
    env["LAB_EVENTS"] = str(rdir / "lab_events.jsonl")
    env["LAB_USAGE_LOG"] = str(rdir / "usage.jsonl")
    # harness-side sandboxed work (probe replays, blind tests) gets the same read lockdown as the agent
    env.update({"LAB_DENY_READ_ROOT": "/" + "/".join(REPO.parts[1:3]), "LAB_READ_ALLOW": f"{rdir}:{SANDBOX / 'toolchain'}",
                "LAB_SCRATCH": str(rdir / "labtmp"), "LAB_EXTRA_WRITABLE": str(rdir)})
    for kv in args.env:
        k, v = kv.split("=", 1); env[k] = v.replace("{rundir}", str(rdir))
    cmd = [args.binary, "exec", "--json", "--skip-git-repo-check", "-C", str(work)]
    for c in args.config:
        cmd += ["-c", c]
    cmd.append(prompt)
    t0 = time.time()
    timed_out = False
    with open(rdir / "transcript.jsonl", "w") as out, open(rdir / "stderr.log", "w") as err:
        p = subprocess.Popen(cmd, cwd=work, env=env, stdout=out, stderr=err, stdin=subprocess.DEVNULL, start_new_session=True)
        deadline = time.time() + args.timeout
        killed_reason = None
        while p.poll() is None:
            if time.time() > deadline:
                killed_reason = "timeout"
            elif args.max_commands and (rdir / "transcript.jsonl").read_text().count('"type":"item.started","item":{"id":') > args.max_commands:
                killed_reason = "max_commands"
            elif args.max_cost and usage_cost(rdir) > args.max_cost:
                killed_reason = "max_cost"
            if killed_reason:
                timed_out = True
                os.killpg(p.pid, signal.SIGKILL); p.wait()
                break
            time.sleep(2)
    wall = time.time() - t0
    tx = (rdir / "transcript.jsonl").read_text()
    usage = {"input_tokens": 0, "cached_input_tokens": 0, "output_tokens": 0, "reasoning_output_tokens": 0}
    n_cmd = n_cmd_fail = n_msgs = n_patch = n_patch_fail = 0
    for line in tx.splitlines():
        try:
            d = json.loads(line)
        except Exception:
            continue
        if d.get("type") == "turn.completed":
            for k in usage:
                usage[k] += d.get("usage", {}).get(k, 0) or 0
        it = d.get("item") or {}
        if d.get("type") == "item.completed":
            if it.get("type") == "command_execution":
                n_cmd += 1; n_cmd_fail += int((it.get("exit_code") or 0) != 0)
            elif it.get("type") == "file_change":
                n_patch += 1; n_patch_fail += int(it.get("status") not in ("completed", None))
            elif it.get("type") == "agent_message":
                n_msgs += 1
    pr = PRICES.get(args.model, (0, 0, 0))
    unc = usage["input_tokens"] - usage["cached_input_tokens"]
    cost = unc * pr[0] + usage["cached_input_tokens"] * pr[1] + usage["output_tokens"] * pr[2]
    lab_events = {}
    if (rdir / "lab_events.jsonl").exists():
        for line in (rdir / "lab_events.jsonl").read_text().splitlines():
            try:
                ev = json.loads(line); lab_events[ev["kind"]] = lab_events.get(ev["kind"], 0) + 1
            except Exception:
                pass
    lab_cost = 0.0
    if (rdir / "lab_events.jsonl").exists():
        for line in (rdir / "lab_events.jsonl").read_text().splitlines():
            try:
                lab_cost += float(json.loads(line)["data"].get("cost_usd") or 0)
            except Exception:
                pass
    g = grade(tdir, work)
    (rdir / "grade.json").write_text(json.dumps(g, indent=1))
    row = {
        "exp": args.exp, "arm": args.arm, "task": task_id, "seed": seed, "model": args.model,
        "passed": g["passed"], "tests_passed": g["tests_passed"], "tests_total": g["tests_total"],
        "wall_s": round(wall, 1), "timed_out": timed_out, "exit_code": p.returncode,
        "cost_usd_est": round(cost, 5), "cost_usd": round(usage_cost(rdir) + lab_cost, 5), "kill_reason": killed_reason, **usage, "n_commands": n_cmd, "n_command_fail": n_cmd_fail,
        "n_patches": n_patch, "n_patch_fail": n_patch_fail, "n_agent_msgs": n_msgs,
        "escape_hits": scan_escape(tx, rdir), "lab_events": lab_events, "run_dir": str(rdir), "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exp", required=True); ap.add_argument("--arm", required=True)
    ap.add_argument("--binary", required=True); ap.add_argument("--tasks", default="all")
    ap.add_argument("--seeds", type=int, default=1); ap.add_argument("--seed-offset", type=int, default=0)
    ap.add_argument("--model", default="deepseek/deepseek-v4-flash"); ap.add_argument("--provider", default="openrouter")
    ap.add_argument("--parallel", type=int, default=6); ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--max-commands", type=int, default=60); ap.add_argument("--max-cost", type=float, default=0.08)
    ap.add_argument("--env", action="append", default=[]); ap.add_argument("-c", "--config", action="append", default=[])
    args = ap.parse_args()
    args.binary = str(pathlib.Path(args.binary).resolve())
    args.timeout = min(args.timeout, 900)  # rule: kill any run after 15 minutes
    if args.tasks == "all":
        tasks = sorted(str(p.parent.relative_to(TASKS)) for p in TASKS.rglob("task.json"))
    else:
        tasks = [l.strip() for l in open(args.tasks) if l.strip() and not l.startswith("#")]
    outdir = REPO / "experiments" / args.exp
    outdir.mkdir(parents=True, exist_ok=True)
    bench_before = tree_hash(REPO / "bench" / "tasks") + tree_hash_file(REPO / "bench" / "grade.py")
    jobs = [(t, args.seed_offset + s) for s in range(args.seeds) for t in tasks]
    with cf.ThreadPoolExecutor(args.parallel) as ex, open(outdir / "runs.jsonl", "a") as log:
        futs = {ex.submit(run_one, args, t, s): (t, s) for t, s in jobs}
        for f in cf.as_completed(futs):
            try:
                row = f.result()
            except Exception as e:
                import traceback; traceback.print_exc()
                row = {"exp": args.exp, "arm": args.arm, "task": futs[f][0], "seed": futs[f][1], "error": repr(e)}
            log.write(json.dumps(row) + "\n"); log.flush()
            print(row.get("arm"), row.get("task"), row.get("passed"), row.get("cost_usd"), row.get("wall_s"), row.get("kill_reason"), flush=True)
    bench_after = tree_hash(REPO / "bench" / "tasks") + tree_hash_file(REPO / "bench" / "grade.py")
    print("BENCH_INTEGRITY", "OK" if bench_before == bench_after else "MODIFIED!", bench_before, bench_after)


if __name__ == "__main__":
    main()
