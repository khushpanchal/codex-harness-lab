//! Mutation-guided blind spots: when the agent tries to finish, the harness applies small
//! single-line mutations to the code the agent wrote and re-runs the side-effect-free checks the
//! agent itself ran earlier (recorded by `probe_replay`). Mutants no check detects mark logic the
//! agent never verified; they are reported back once. Enabled with `LAB_MUTATION_BLINDSPOTS=1`.

use std::path::Path;
use std::path::PathBuf;
use std::sync::atomic::AtomicBool;
use std::sync::atomic::Ordering;
use std::time::Duration;
use std::time::Instant;

use serde_json::json;

static DONE: AtomicBool = AtomicBool::new(false);

pub(crate) fn enabled() -> bool {
    super::env_flag("LAB_MUTATION_BLINDSPOTS")
}

struct Mutant {
    file: String,
    line_no: usize,
    before: String,
    after: String,
}

fn candidate_files(root: &Path) -> Vec<String> {
    let starter = super::starter_files();
    let mut out = Vec::new();
    fn walk(dir: &Path, root: &Path, out: &mut Vec<String>) {
        let Ok(read) = std::fs::read_dir(dir) else { return };
        for e in read.filter_map(Result::ok) {
            let name = e.file_name().to_string_lossy().to_string();
            let Ok(ft) = e.file_type() else { continue };
            if ft.is_dir() {
                if !matches!(name.as_str(), "target" | ".git" | "__pycache__" | "tests" | "tmp") {
                    walk(&e.path(), root, out);
                }
            } else if (name.ends_with(".py") || name.ends_with(".rs")) && !name.contains("test") {
                if let Ok(rel) = e.path().strip_prefix(root) {
                    out.push(rel.display().to_string());
                }
            }
        }
    }
    walk(root, root, &mut out);
    // Only files the agent changed (or created) relative to the starter snapshot.
    out.retain(|rel| {
        let now = std::fs::read_to_string(root.join(rel)).unwrap_or_default();
        !starter.iter().any(|(p, text)| p == rel && *text == now)
    });
    out.sort();
    out
}

fn mutate_line(line: &str, rust: bool) -> Vec<String> {
    let trimmed = line.trim_start();
    if trimmed.is_empty() || trimmed.starts_with('#') || trimmed.starts_with("//") || trimmed.starts_with("use ")
        || trimmed.starts_with("import ") || trimmed.starts_with("from ") || trimmed.starts_with("\"\"\"")
    {
        return Vec::new();
    }
    let mut out = Vec::new();
    let swaps: &[(&str, &str)] = &[
        (" <= ", " < "),
        (" >= ", " > "),
        (" < ", " <= "),
        (" > ", " >= "),
        (" == ", " != "),
        (" != ", " == "),
        (" + 1", " - 1"),
        (" - 1", " + 1"),
    ];
    for (a, b) in swaps {
        if let Some(idx) = line.find(a) {
            out.push(format!("{}{}{}", &line[..idx], b, &line[idx + a.len()..]));
        }
    }
    let bool_swaps: &[(&str, &str)] = if rust {
        &[(" && ", " || "), (" || ", " && "), ("true", "false"), ("false", "true")]
    } else {
        &[(" and ", " or "), (" or ", " and "), ("True", "False"), ("False", "True")]
    };
    for (a, b) in bool_swaps {
        if let Some(idx) = line.find(a) {
            out.push(format!("{}{}{}", &line[..idx], b, &line[idx + a.len()..]));
        }
    }
    if !rust && trimmed.starts_with("raise ") {
        let indent = &line[..line.len() - trimmed.len()];
        out.push(format!("{indent}pass"));
    }
    if !rust && (trimmed.starts_with("if ") || trimmed.starts_with("elif ")) && trimmed.ends_with(':') {
        let kw = if trimmed.starts_with("if ") { "if " } else { "elif " };
        let indent = &line[..line.len() - trimmed.len()];
        let cond = &trimmed[kw.len()..trimmed.len() - 1];
        out.push(format!("{indent}{kw}not ({cond}):"));
    }
    out
}

fn generate_mutants(root: &Path, max: usize) -> Vec<Mutant> {
    let mut all = Vec::new();
    for rel in candidate_files(root) {
        let rust = rel.ends_with(".rs");
        let Ok(text) = std::fs::read_to_string(root.join(&rel)) else { continue };
        for (i, line) in text.lines().enumerate() {
            for after in mutate_line(line, rust) {
                all.push(Mutant { file: rel.clone(), line_no: i + 1, before: line.to_string(), after });
            }
        }
    }
    if all.len() <= max {
        return all;
    }
    // Deterministic even spread over the code.
    let step = all.len() as f64 / max as f64;
    let picks: Vec<usize> = (0..max).map(|k| (k as f64 * step) as usize).collect();
    all.into_iter().enumerate().filter(|(i, _)| picks.contains(i)).map(|(_, m)| m).collect()
}

fn copy_dir(src: &Path, dst: &Path) -> std::io::Result<()> {
    std::fs::create_dir_all(dst)?;
    for e in std::fs::read_dir(src)? {
        let e = e?;
        let name = e.file_name();
        if e.file_type()?.is_dir() {
            if matches!(name.to_string_lossy().as_ref(), "target" | ".git" | "__pycache__") {
                continue;
            }
            copy_dir(&e.path(), &dst.join(&name))?;
        } else {
            std::fs::copy(e.path(), dst.join(&name))?;
        }
    }
    Ok(())
}

fn run_probes_in(copy: &Path, root: &Path, probes: &[(String, PathBuf)], target: &Path) -> Vec<Option<(i32, String)>> {
    probes
        .iter()
        .map(|(cmd, workdir)| {
            let rel = workdir.strip_prefix(root).map(Path::to_path_buf).unwrap_or_default();
            let wd = copy.join(rel);
            let writable = vec![copy.to_path_buf(), target.to_path_buf(), super::scratch_dir()];
            super::run_sandboxed(
                cmd,
                &wd,
                &writable,
                &[("CARGO_TARGET_DIR", target.display().to_string())],
                Duration::from_secs(60),
            )
            .map(|(code, out)| {
                // Copies live at different paths; tracebacks must not make every mutant look "killed".
                let out = out.replace(&copy.display().to_string(), "<ws>");
                (code, super::probe_replay::normalize(&out))
            })
        })
        .collect()
}

/// Called at the stop gate. Returns a continuation prompt, or None.
pub(crate) fn on_stop() -> Option<String> {
    if DONE.swap(true, Ordering::SeqCst) {
        return None;
    }
    let root = super::workspace_root();
    let probes = super::probe_replay::probes_snapshot();
    if probes.is_empty() {
        super::log_event("mutation_skipped", json!({ "reason": "no_probes" }));
        return None;
    }
    let rust = root.join("Cargo.toml").exists();
    let mutants = generate_mutants(&root, if rust { 10 } else { 24 });
    if mutants.is_empty() {
        super::log_event("mutation_skipped", json!({ "reason": "no_mutants" }));
        return None;
    }
    let scratch = super::scratch_dir().join("mutation");
    let target = super::scratch_dir().join("mutation-target");
    let _ = std::fs::remove_dir_all(&scratch);
    let start = Instant::now();
    // Baseline on an unmutated copy (probe outputs must be deterministic to be usable).
    let base_copy = scratch.join("base");
    if copy_dir(&root, &base_copy).is_err() {
        return None;
    }
    let baseline = run_probes_in(&base_copy, &root, &probes, &target);
    let base_copy2 = scratch.join("base2");
    if copy_dir(&root, &base_copy2).is_err() {
        return None;
    }
    let baseline2 = run_probes_in(&base_copy2, &root, &probes, &target);
    // Usable probes: completed and deterministic across two unmutated runs at different paths.
    let usable: Vec<usize> = (0..probes.len())
        .filter(|&i| baseline[i].is_some() && baseline[i] == baseline2[i])
        .collect();
    if usable.is_empty() {
        return None;
    }
    let budget = Duration::from_secs(if rust { 240 } else { 120 });
    let mut survived = Vec::new();
    let mut tested = 0usize;
    for (k, m) in mutants.iter().enumerate() {
        if start.elapsed() > budget {
            break;
        }
        let copy = scratch.join(format!("m{k}"));
        if copy_dir(&root, &copy).is_err() {
            continue;
        }
        let path = copy.join(&m.file);
        let Ok(text) = std::fs::read_to_string(&path) else { continue };
        let mut lines: Vec<String> = text.lines().map(str::to_string).collect();
        if m.line_no == 0 || m.line_no > lines.len() {
            continue;
        }
        lines[m.line_no - 1] = m.after.clone();
        let _ = std::fs::write(&path, lines.join("\n") + "\n");
        let results = run_probes_in(&copy, &root, &probes, &target);
        tested += 1;
        let killed = usable.iter().any(|&i| results[i] != baseline[i]);
        if !killed {
            survived.push(m);
        }
        let _ = std::fs::remove_dir_all(&copy);
    }
    super::log_event(
        "mutation_check",
        json!({ "probes": usable.len(), "probes_recorded": probes.len(), "mutants_tested": tested, "survived": survived.len(), "ms": start.elapsed().as_millis() as u64 }),
    );
    if survived.is_empty() {
        return None;
    }
    let shown: Vec<String> = survived
        .iter()
        .take(12)
        .map(|m| format!("• {}:{}  `{}`  →  `{}`", m.file, m.line_no, m.before.trim(), m.after.trim()))
        .collect();
    Some(format!(
        "[harness mutation check] Before you finish: the harness made {tested} small single-line changes (mutants) to your code and re-ran the {} check(s) you ran earlier. {} mutant(s) changed NO check result, so the behavior of these lines is currently unverified:\n{}\n\nFor each line, decide from the task description whether the original code is right (some mutants may be equivalent). Add checks for the behaviors that matter and fix any bug you find. Then finish.",
        usable.len(),
        survived.len(),
        shown.join("\n")
    ))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn surviving_mutant_is_reported_and_killed_mutants_are_not() {
        let ws = tempfile::tempdir().expect("tempdir");
        let scratch = tempfile::tempdir().expect("tempdir");
        std::fs::write(
            ws.path().join("calc.py"),
            "def classify(n):\n    if n > 10:\n        return \"big\"\n    return \"small\"\n",
        )
        .expect("write");
        // SAFETY: test-only env mutation; this test owns these variables.
        unsafe {
            std::env::set_var("LAB_WORKSPACE", ws.path());
            std::env::set_var("LAB_SCRATCH", scratch.path());
            std::env::set_var("LAB_MUTATION_BLINDSPOTS", "1");
        }
        let args = serde_json::json!({ "cmd": "python3 -c 'from calc import classify; print(classify(20))'" }).to_string();
        super::super::probe_replay::record_probe(&args, "Process exited with code 0\nOutput:\nbig\n");
        let msg = on_stop().expect("a surviving mutant should be reported");
        println!("{msg}");
        // n > 10 -> n >= 10 is not detected by classify(20)
        assert!(msg.contains("calc.py:2"), "{msg}");
        assert!(msg.contains(">= 10"), "{msg}");
        // negating the condition flips classify(20) -> killed, must not be listed
        assert!(!msg.contains("not (n > 10)"), "{msg}");
    }
}
