//! Blind-spec tester: when the agent tries to finish, an information-firewalled model call writes
//! unit tests from the task description + starter interface ONLY (it never sees the agent's code).
//! The harness runs them against a scratch copy of the workspace; failures are handed back to the
//! agent as a continuation. Enabled with `LAB_BLIND_TESTER=1`.
//!
//! Control arm `LAB_SELF_TEST_NUDGE=1`: same stop gate, but instead of firewalled tests the agent is
//! simply asked to write and run spec-derived tests itself (isolates the firewall from the nudge).

use std::path::Path;
use std::path::PathBuf;
use std::sync::Mutex;
use std::sync::atomic::AtomicUsize;
use std::sync::atomic::Ordering;
use std::time::Duration;

use serde_json::json;

static ROUNDS: AtomicUsize = AtomicUsize::new(0);
static TESTS: Mutex<Option<GeneratedTests>> = Mutex::new(None);

#[derive(Clone)]
struct GeneratedTests {
    file_name: String,
    code: String,
}

enum Lang {
    Python,
    Rust { crate_name: String },
}

pub(crate) fn enabled() -> bool {
    super::env_flag("LAB_BLIND_TESTER") || super::env_flag("LAB_SELF_TEST_NUDGE")
}

fn max_rounds() -> usize {
    std::env::var("LAB_BLIND_TESTER_ROUNDS")
        .ok()
        .and_then(|v| v.parse().ok())
        .unwrap_or(2)
}

fn detect_lang(root: &Path) -> Lang {
    if let Ok(cargo) = std::fs::read_to_string(root.join("Cargo.toml")) {
        let name = cargo
            .lines()
            .find_map(|l| {
                let l = l.trim();
                l.strip_prefix("name")
                    .and_then(|rest| rest.trim_start().strip_prefix('='))
                    .map(|v| v.trim().trim_matches('"').replace('-', "_"))
            })
            .unwrap_or_else(|| "solution".to_string());
        Lang::Rust { crate_name: name }
    } else {
        Lang::Python
    }
}

fn extract_code_block(text: &str) -> String {
    if let Some(start) = text.find("```") {
        let after = &text[start + 3..];
        let body_start = after.find('\n').map(|i| i + 1).unwrap_or(0);
        let body = &after[body_start..];
        if let Some(end) = body.rfind("```") {
            return body[..end].to_string();
        }
        return body.to_string();
    }
    text.to_string()
}

fn generate_tests(spec: &str, lang: &Lang) -> Option<GeneratedTests> {
    let starter = super::starter_files()
        .iter()
        .map(|(path, text)| format!("--- {path} ---\n{text}"))
        .collect::<Vec<_>>()
        .join("\n");
    let (file_name, lang_rules) = match lang {
        Lang::Python => (
            "test_blind_spec.py".to_string(),
            "Write a Python `unittest` test module (it will be saved as test_blind_spec.py next to the solution files and run with `python3 -m unittest test_blind_spec`). Import the solution the same way the starter files are named (e.g. `from bowling import BowlingGame`). Use only the standard library.".to_string(),
        ),
        Lang::Rust { crate_name } => (
            "blind_spec.rs".to_string(),
            format!("Write a Rust integration test file (it will be saved as tests/blind_spec.rs and run with `cargo test --test blind_spec`). Import with `use {crate_name}::*;` and use only the public API shown in the starter files. No external crates."),
        ),
    };
    let system = "You are a meticulous test engineer. You will receive a programming task description and the starter files (interfaces only - you will never see the implementation). Write a thorough unit test suite checking the behavior the description requires: normal cases, edge cases, and every error/validation rule it states. Only assert behavior the description or starter interface clearly specifies; do not invent requirements (e.g. exact error message text) that it does not state. Reply with a single fenced code block and nothing else.";
    let user = format!("{lang_rules}\n\n# Task description\n{spec}\n\n# Starter files\n{starter}");
    let (text, cost) = super::chat_completion(system, &user)?;
    let code = extract_code_block(&text);
    super::log_event("blind_tests_generated", json!({ "bytes": code.len(), "cost_usd": cost }));
    Some(GeneratedTests { file_name, code })
}

fn copy_workspace(src: &Path, dst: &Path) -> std::io::Result<()> {
    std::fs::create_dir_all(dst)?;
    for entry in std::fs::read_dir(src)? {
        let entry = entry?;
        let name = entry.file_name();
        let ft = entry.file_type()?;
        if ft.is_dir() {
            if matches!(name.to_string_lossy().as_ref(), "target" | ".git" | "__pycache__") {
                continue;
            }
            copy_workspace(&entry.path(), &dst.join(&name))?;
        } else if ft.is_file() {
            std::fs::copy(entry.path(), dst.join(&name))?;
        }
    }
    Ok(())
}

/// Returns (all_passed, summary_output).
fn run_tests(tests: &GeneratedTests, lang: &Lang, round: usize) -> (bool, String) {
    let scratch = super::scratch_dir();
    let copy = scratch.join(format!("blind-run-{round}"));
    let _ = std::fs::remove_dir_all(&copy);
    if copy_workspace(&super::workspace_root(), &copy).is_err() {
        return (true, String::new());
    }
    let target: PathBuf = scratch.join("blind-target");
    let (script, timeout, envs) = match lang {
        Lang::Python => {
            let _ = std::fs::write(copy.join(&tests.file_name), &tests.code);
            ("python3 -m unittest test_blind_spec 2>&1".to_string(), Duration::from_secs(60), vec![])
        }
        Lang::Rust { .. } => {
            let _ = std::fs::create_dir_all(copy.join("tests"));
            let _ = std::fs::write(copy.join("tests").join(&tests.file_name), &tests.code);
            (
                "cargo test --offline --test blind_spec -- --include-ignored 2>&1".to_string(),
                Duration::from_secs(240),
                vec![("CARGO_TARGET_DIR", target.display().to_string())],
            )
        }
    };
    let writable = vec![copy.clone(), target];
    match super::run_sandboxed(&script, &copy, &writable, &envs, timeout) {
        Some((0, _)) => (true, String::new()),
        Some((_, out)) => (false, out),
        None => (false, "(test run timed out)".to_string()),
    }
}

fn tail_lines(text: &str, n: usize) -> String {
    let lines: Vec<&str> = text.lines().collect();
    let start = lines.len().saturating_sub(n);
    lines[start..].join("\n")
}

/// Called when the agent is about to end its turn. Returns a continuation prompt, or None to stop.
pub(crate) fn on_stop(spec: &str) -> Option<String> {
    let round = ROUNDS.load(Ordering::SeqCst);
    if round >= max_rounds() {
        return None;
    }
    ROUNDS.store(round + 1, Ordering::SeqCst);
    let root = super::workspace_root();
    let lang = detect_lang(&root);

    if super::env_flag("LAB_SELF_TEST_NUDGE") {
        if round > 0 {
            return None;
        }
        super::log_event("self_test_nudge", json!({ "round": round }));
        return Some("Before you finish: write a thorough set of unit tests derived ONLY from the task description above (normal cases, edge cases, and every error/validation rule it states), run them against your implementation, and fix any bugs they reveal. Then finish.".to_string());
    }

    let tests = {
        let cached = TESTS.lock().unwrap_or_else(std::sync::PoisonError::into_inner).clone();
        match cached {
            Some(t) => t,
            None => {
                let generated = generate_tests(spec, &lang)?;
                *TESTS.lock().unwrap_or_else(std::sync::PoisonError::into_inner) = Some(generated.clone());
                generated
            }
        }
    };
    let (passed, output) = run_tests(&tests, &lang, round);
    super::log_event("blind_tests_run", json!({ "round": round, "passed": passed }));
    if passed {
        ROUNDS.store(usize::MAX / 2, Ordering::SeqCst);
        return None;
    }
    let shown_path = match lang {
        Lang::Python => tests.file_name.clone(),
        Lang::Rust { .. } => format!("tests/{}", tests.file_name),
    };
    Some(format!(
        "[harness blind-spec check] Before you finish: an independent tester wrote the tests below using ONLY the task description and starter interface - they never saw your code. Running them against a scratch copy of your current code FAILS:\n\n```\n{}\n```\n\nTest file (`{shown_path}`; the harness runs it in a scratch copy, it is not in your workspace):\n```\n{}\n```\n\nThe tester can be wrong. For each failure, decide from the task description whether your code or the test is wrong, and fix your code wherever the description supports the test. Then finish.",
        tail_lines(&output, 60),
        tests.code
    ))
}
