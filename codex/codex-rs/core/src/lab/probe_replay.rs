//! Probe replay: every side-effect-free check the agent runs (e.g. `python3 -c ...`, `cargo test`)
//! becomes a regression probe. Whenever a later tool call changes workspace files, the harness
//! re-runs the recorded probes (sandboxed) and tells the model which observable behaviors changed.
//!
//! Enabled with `LAB_PROBE_REPLAY=1`.

use std::collections::hash_map::DefaultHasher;
use std::hash::Hash;
use std::hash::Hasher;
use std::path::Path;
use std::path::PathBuf;
use std::sync::Mutex;
use std::time::Duration;
use std::time::Instant;

use codex_protocol::parse_command::ParsedCommand;
use codex_shell_command::parse_command::parse_shell_script;
use serde_json::json;

const MAX_PROBES: usize = 8;
const PROBE_TIMEOUT: Duration = Duration::from_secs(20);
const REPLAY_BUDGET: Duration = Duration::from_secs(60);
const MAX_DIFF_LINES: usize = 30;

struct Probe {
    cmd: String,
    workdir: PathBuf,
    output: String,
    exit: i32,
}

static PROBES: Mutex<Vec<Probe>> = Mutex::new(Vec::new());

pub(crate) fn enabled() -> bool {
    super::env_flag("LAB_PROBE_REPLAY")
}

fn root() -> PathBuf {
    super::workspace_root()
}

/// Cheap fingerprint of the workspace: paths, sizes and mtimes (build/cache dirs skipped).
pub(crate) fn fingerprint() -> u64 {
    fn walk(dir: &Path, hasher: &mut DefaultHasher, budget: &mut usize) {
        let Ok(read) = std::fs::read_dir(dir) else {
            return;
        };
        let mut entries: Vec<_> = read.filter_map(Result::ok).collect();
        entries.sort_by_key(std::fs::DirEntry::file_name);
        for entry in entries {
            if *budget == 0 {
                return;
            }
            let Ok(ft) = entry.file_type() else { continue };
            let name = entry.file_name();
            if ft.is_dir() {
                if !matches!(
                    name.to_string_lossy().as_ref(),
                    "target" | ".git" | "__pycache__" | "node_modules" | ".pytest_cache"
                ) {
                    walk(&entry.path(), hasher, budget);
                }
            } else if ft.is_file() {
                *budget -= 1;
                entry.path().hash(hasher);
                if let Ok(meta) = entry.metadata() {
                    meta.len().hash(hasher);
                    if let Ok(modified) = meta.modified() {
                        modified.hash(hasher);
                    }
                }
            }
        }
    }
    let mut hasher = DefaultHasher::new();
    let mut budget = 5000usize;
    walk(&root(), &mut hasher, &mut budget);
    hasher.finish()
}

fn parse_exec_output(text: &str) -> Option<(i32, String)> {
    let code_line = text
        .lines()
        .find_map(|line| line.strip_prefix("Process exited with code "))?;
    let exit = code_line.trim().parse().ok()?;
    let output = text
        .split_once("\nOutput:\n")
        .map(|(_, out)| out.to_string())
        .unwrap_or_default();
    Some((exit, output))
}

fn normalize(output: &str) -> String {
    let duration = regex_lite::Regex::new(r"\d+(\.\d+)?\s?(ms|s)\b").expect("valid regex");
    output
        .lines()
        .filter(|line| {
            let t = line.trim_start();
            !(t.starts_with("Compiling ")
                || t.starts_with("Finished ")
                || t.starts_with("Running ")
                || t.starts_with("Blocking ")
                || t.starts_with("Fresh "))
        })
        .map(|line| duration.replace_all(line.trim_end(), "#").into_owned())
        .collect::<Vec<_>>()
        .join("\n")
        .trim()
        .to_string()
}

fn is_pure_read(cmd: &str) -> bool {
    let parsed = parse_shell_script(cmd);
    !parsed.is_empty()
        && parsed
            .iter()
            .all(|p| !matches!(p, ParsedCommand::Unknown { .. }))
}

/// Called after an `exec_command` that did NOT change the workspace: remember it as a probe.
pub(crate) fn record_probe(arguments: &str, output_text: &str) {
    let Ok(args) = serde_json::from_str::<serde_json::Value>(arguments) else {
        return;
    };
    let Some(cmd) = args.get("cmd").and_then(|c| c.as_str()) else {
        return;
    };
    if is_pure_read(cmd) {
        return;
    }
    // Never replay edits, network, VCS or package-manager commands.
    let lowered = cmd.to_lowercase();
    if ["apply_patch", "curl ", "wget ", "git ", "pip ", "pip3 ", "cargo add", "npm ", "rm ", "mv ", "cp ", "> ", ">>", "tee "]
        .iter()
        .any(|needle| lowered.contains(needle))
    {
        return;
    }
    let Some((exit, output)) = parse_exec_output(output_text) else {
        return; // still running / not a completed process
    };
    let workdir = match args.get("workdir").and_then(|w| w.as_str()) {
        Some(w) if !w.is_empty() => root().join(w),
        _ => root(),
    };
    let mut probes = PROBES.lock().unwrap_or_else(std::sync::PoisonError::into_inner);
    probes.retain(|p| !(p.cmd == cmd && p.workdir == workdir));
    probes.push(Probe {
        cmd: cmd.to_string(),
        workdir,
        output: normalize(&output),
        exit,
    });
    if probes.len() > MAX_PROBES {
        probes.remove(0);
    }
    super::log_event("probe_recorded", json!({ "cmd": cmd, "exit": exit }));
}

fn run_probe(cmd: &str, workdir: &Path, timeout: Duration) -> Option<(i32, String)> {
    let mut writable = vec![root(), workdir.to_path_buf()];
    if let Ok(extra) = std::env::var("LAB_EXTRA_WRITABLE") {
        writable.push(PathBuf::from(extra));
    }
    super::run_sandboxed(cmd, workdir, &writable, &[], timeout)
}

fn short(cmd: &str) -> String {
    let one_line = cmd.replace('\n', " ⏎ ");
    if one_line.chars().count() > 160 {
        format!("{}…", one_line.chars().take(160).collect::<String>())
    } else {
        one_line
    }
}

/// Called after a tool call that changed the workspace. Returns text to append to its output.
pub(crate) fn replay_after_change() -> Option<String> {
    let snapshot: Vec<(String, PathBuf, String, i32)> = {
        let probes = PROBES.lock().unwrap_or_else(std::sync::PoisonError::into_inner);
        probes
            .iter()
            .map(|p| (p.cmd.clone(), p.workdir.clone(), p.output.clone(), p.exit))
            .collect()
    };
    if snapshot.is_empty() {
        return None;
    }
    let start = Instant::now();
    let mut changed = Vec::new();
    let mut unchanged = 0usize;
    let mut drop_cmds = Vec::new();
    let mut updates = Vec::new();
    for (cmd, workdir, old_out, old_exit) in snapshot.iter().rev() {
        if start.elapsed() > REPLAY_BUDGET {
            break;
        }
        let Some((exit, out)) = run_probe(cmd, workdir, PROBE_TIMEOUT) else {
            drop_cmds.push(cmd.clone());
            continue;
        };
        let out = normalize(&out);
        if exit == *old_exit && out == *old_out {
            unchanged += 1;
            continue;
        }
        // Determinism check: a probe whose output differs between two runs on the same code is noise.
        match run_probe(cmd, workdir, PROBE_TIMEOUT) {
            Some((exit2, out2)) if exit2 == exit && normalize(&out2) == out => {}
            _ => {
                drop_cmds.push(cmd.clone());
                continue;
            }
        }
        let diff = similar::TextDiff::from_lines(old_out.as_str(), out.as_str());
        let mut lines = Vec::new();
        for change in diff.iter_all_changes() {
            let sign = match change.tag() {
                similar::ChangeTag::Delete => "-",
                similar::ChangeTag::Insert => "+",
                similar::ChangeTag::Equal => continue,
            };
            lines.push(format!("    {sign} {}", change.value().trim_end()));
        }
        let extra = lines.len().saturating_sub(MAX_DIFF_LINES);
        lines.truncate(MAX_DIFF_LINES);
        if extra > 0 {
            lines.push(format!("    … {extra} more changed lines"));
        }
        changed.push(format!(
            "• `{}` (exit {} -> {}):\n{}",
            short(cmd),
            old_exit,
            exit,
            lines.join("\n")
        ));
        updates.push((cmd.clone(), workdir.clone(), out, exit));
    }
    {
        let mut probes = PROBES.lock().unwrap_or_else(std::sync::PoisonError::into_inner);
        probes.retain(|p| !drop_cmds.contains(&p.cmd));
        for (cmd, workdir, out, exit) in updates {
            if let Some(p) = probes.iter_mut().find(|p| p.cmd == cmd && p.workdir == workdir) {
                p.output = out;
                p.exit = exit;
            }
        }
    }
    super::log_event(
        "probe_replay",
        json!({ "changed": changed.len(), "unchanged": unchanged, "dropped": drop_cmds.len(), "ms": start.elapsed().as_millis() as u64 }),
    );
    if changed.is_empty() && unchanged == 0 {
        return None;
    }
    let mut msg = String::from("[harness probe-replay] ");
    if changed.is_empty() {
        msg.push_str(&format!(
            "Re-ran {unchanged} earlier check(s) you had run against the new code: all results unchanged."
        ));
    } else {
        msg.push_str(&format!(
            "This change altered the results of {} earlier check(s) you had run (re-executed automatically against the new code; {unchanged} other check(s) unchanged):\n{}\nConfirm each change is intended — an unintended change is a regression.",
            changed.len(),
            changed.join("\n")
        ));
    }
    Some(msg)
}
