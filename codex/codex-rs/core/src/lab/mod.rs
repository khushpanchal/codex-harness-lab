//! Harness-lab experiments. Every experiment is gated by an environment variable so the
//! baseline arm runs the identical binary with the feature off.



pub(crate) mod probe_replay;

use crate::tools::context::ToolOutput;
use crate::tools::context::ToolPayload;
use codex_protocol::models::FunctionCallOutputBody;
use codex_protocol::models::FunctionCallOutputContentItem;
use codex_protocol::models::ResponseInputItem;
use serde_json::Value;

pub(crate) fn env_flag(name: &str) -> bool {
    std::env::var(name).is_ok_and(|v| v == "1")
}

/// Append a single JSON line to `$LAB_EVENTS` (if set) so experiments can prove the feature fired.
pub(crate) fn log_event(kind: &str, data: Value) {
    let Ok(path) = std::env::var("LAB_EVENTS") else {
        return;
    };
    let line = serde_json::json!({ "kind": kind, "data": data }).to_string();
    if let Ok(mut f) = std::fs::OpenOptions::new().create(true).append(true).open(path) {
        use std::io::Write;
        let _ = writeln!(f, "{line}");
    }
}

/// Text body of a tool's model-visible output, if it is textual.
pub(crate) fn response_text(item: &ResponseInputItem) -> Option<String> {
    match item {
        ResponseInputItem::FunctionCallOutput { output, .. }
        | ResponseInputItem::CustomToolCallOutput { output, .. } => match &output.body {
            FunctionCallOutputBody::Text(text) => Some(text.clone()),
            FunctionCallOutputBody::ContentItems(items) => Some(
                items
                    .iter()
                    .filter_map(|item| match item {
                        FunctionCallOutputContentItem::InputText { text } => Some(text.as_str()),
                        _ => None,
                    })
                    .collect::<Vec<_>>()
                    .join("\n"),
            ),
        },
        _ => None,
    }
}

/// Wraps a tool output and appends harness-generated text to what the model sees.
pub(crate) struct SuffixedOutput {
    pub(crate) original: Box<dyn ToolOutput>,
    pub(crate) suffix: String,
}

impl ToolOutput for SuffixedOutput {
    fn log_output(&self) -> String {
        format!("{}\n{}", self.original.log_output(), self.suffix)
    }

    fn success_for_logging(&self) -> bool {
        self.original.success_for_logging()
    }

    fn fallback_token_limit_override(&self) -> Option<usize> {
        self.original.fallback_token_limit_override()
    }

    fn to_response_item(&self, call_id: &str, payload: &ToolPayload) -> ResponseInputItem {
        let mut item = self.original.to_response_item(call_id, payload);
        match &mut item {
            ResponseInputItem::FunctionCallOutput { output, .. }
            | ResponseInputItem::CustomToolCallOutput { output, .. } => match &mut output.body {
                FunctionCallOutputBody::Text(text) => {
                    text.push_str("\n\n");
                    text.push_str(&self.suffix);
                }
                FunctionCallOutputBody::ContentItems(items) => {
                    items.push(FunctionCallOutputContentItem::InputText {
                        text: self.suffix.clone(),
                    });
                }
            },
            _ => {}
        }
        item
    }

    fn code_mode_result(&self, payload: &ToolPayload) -> Value {
        self.original.code_mode_result(payload)
    }

    fn tool_result_metadata(&self) -> Option<&Value> {
        self.original.tool_result_metadata()
    }
}

/// Workspace root of the agent (process cwd, or `LAB_WORKSPACE`).
pub(crate) fn workspace_root() -> std::path::PathBuf {
    std::env::var("LAB_WORKSPACE")
        .map(std::path::PathBuf::from)
        .or_else(|_| std::env::current_dir())
        .unwrap_or_else(|_| std::path::PathBuf::from("."))
}

/// Scratch dir for harness-side work (outside the agent workspace when `LAB_SCRATCH` is set).
pub(crate) fn scratch_dir() -> std::path::PathBuf {
    std::env::var("LAB_SCRATCH")
        .map(std::path::PathBuf::from)
        .unwrap_or_else(|_| std::env::temp_dir().join("codex-lab"))
}

fn sbpl_path(p: &std::path::Path) -> String {
    let canon = std::fs::canonicalize(p).unwrap_or_else(|_| p.to_path_buf());
    format!("(subpath {})", serde_json::to_string(&canon.to_string_lossy()).unwrap_or_default())
}

/// Run `/bin/zsh -c <script>` under a seatbelt profile: no network, writes only to `writable`,
/// and (if `LAB_DENY_READ_ROOT` is set) no reads under that root except `LAB_READ_ALLOW` + writable.
pub(crate) fn run_sandboxed(
    script: &str,
    cwd: &std::path::Path,
    writable: &[std::path::PathBuf],
    envs: &[(&str, String)],
    timeout: std::time::Duration,
) -> Option<(i32, String)> {
    use std::io::Read;
    let mut profile = String::from("(version 1)\n(allow default)\n(deny network*)\n(deny file-write*)\n(allow file-write* (literal \"/dev/null\") (subpath \"/private/tmp\") (subpath \"/private/var/folders\")");
    for w in writable {
        profile.push(' ');
        profile.push_str(&sbpl_path(w));
    }
    profile.push_str(")\n");
    if let Ok(root) = std::env::var("LAB_DENY_READ_ROOT") {
        profile.push_str(&format!("(deny file-read* {})\n(allow file-read-metadata)\n", sbpl_path(std::path::Path::new(&root))));
        let mut allow: Vec<std::path::PathBuf> = writable.to_vec();
        if let Ok(extra) = std::env::var("LAB_READ_ALLOW") {
            allow.extend(extra.split(':').filter(|s| !s.is_empty()).map(std::path::PathBuf::from));
        }
        for a in allow {
            profile.push_str(&format!("(allow file-read* {})\n", sbpl_path(&a)));
        }
    }
    let mut command = std::process::Command::new("/usr/bin/sandbox-exec");
    command
        .arg("-p")
        .arg(profile)
        .arg("/bin/zsh")
        .arg("-c")
        .arg(format!("exec 2>&1; {script}"))
        .current_dir(cwd)
        .stdin(std::process::Stdio::null())
        .stdout(std::process::Stdio::piped())
        .stderr(std::process::Stdio::null());
    for (k, v) in envs {
        command.env(k, v);
    }
    let mut child = command.spawn().ok()?;
    let mut stdout = child.stdout.take()?;
    let reader = std::thread::spawn(move || {
        let mut buf = Vec::new();
        let _ = stdout.read_to_end(&mut buf);
        buf
    });
    let start = std::time::Instant::now();
    let status = loop {
        match child.try_wait() {
            Ok(Some(status)) => break status,
            Ok(None) if start.elapsed() < timeout => {
                std::thread::sleep(std::time::Duration::from_millis(25))
            }
            _ => {
                let _ = child.kill();
                let _ = child.wait();
                return None;
            }
        }
    };
    let buf = reader.join().ok()?;
    Some((status.code().unwrap_or(-1), String::from_utf8_lossy(&buf).into_owned()))
}

/// One-shot chat completion through an OpenAI-compatible endpoint (curl; key read from env, passed on stdin).
/// Returns (text, cost_usd_if_reported).
pub(crate) fn chat_completion(system: &str, user: &str) -> Option<(String, f64)> {
    use std::io::Write;
    let model = std::env::var("LAB_AUX_MODEL").ok()?;
    let url = std::env::var("LAB_AUX_URL")
        .unwrap_or_else(|_| "https://openrouter.ai/api/v1/chat/completions".to_string());
    let key = std::env::var("OPENROUTER_API_KEY").ok()?;
    let body = serde_json::json!({
        "model": model,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "usage": {"include": true},
    });
    let dir = scratch_dir();
    std::fs::create_dir_all(&dir).ok()?;
    let body_path = dir.join(format!("aux-body-{}.json", std::process::id()));
    std::fs::write(&body_path, body.to_string()).ok()?;
    let mut child = std::process::Command::new("curl")
        .args(["-sS", "-m", "300", "-X", "POST", &url, "-H", "Content-Type: application/json", "-H", "@-", "--data-binary"])
        .arg(format!("@{}", body_path.display()))
        .stdin(std::process::Stdio::piped())
        .stdout(std::process::Stdio::piped())
        .stderr(std::process::Stdio::null())
        .spawn()
        .ok()?;
    child
        .stdin
        .take()?
        .write_all(format!("Authorization: Bearer {key}\n").as_bytes())
        .ok()?;
    let out = child.wait_with_output().ok()?;
    let _ = std::fs::remove_file(&body_path);
    let Ok(v) = serde_json::from_slice::<Value>(&out.stdout) else {
        log_event("aux_call_failed", serde_json::json!({ "status": out.status.code(), "stdout_head": String::from_utf8_lossy(&out.stdout).chars().take(300).collect::<String>() }));
        return None;
    };
    let Some(text) = v["choices"][0]["message"]["content"].as_str().map(str::to_string) else {
        log_event("aux_call_failed", serde_json::json!({ "response_head": v.to_string().chars().take(300).collect::<String>() }));
        return None;
    };
    let cost = v["usage"]["cost"].as_f64().unwrap_or(0.0);
    Some((text, cost))
}

static STARTER_FILES: std::sync::OnceLock<Vec<(String, String)>> = std::sync::OnceLock::new();

/// Snapshot of the workspace text files as they were before the agent's first tool call.
pub(crate) fn snapshot_starter_once() {
    STARTER_FILES.get_or_init(|| {
        fn walk(dir: &std::path::Path, root: &std::path::Path, out: &mut Vec<(String, String)>) {
            let Ok(read) = std::fs::read_dir(dir) else { return };
            let mut entries: Vec<_> = read.filter_map(Result::ok).collect();
            entries.sort_by_key(std::fs::DirEntry::file_name);
            for e in entries {
                let name = e.file_name().to_string_lossy().to_string();
                let Ok(ft) = e.file_type() else { continue };
                if ft.is_dir() {
                    if !matches!(name.as_str(), "target" | ".git" | "__pycache__" | "node_modules") {
                        walk(&e.path(), root, out);
                    }
                } else if ft.is_file() && out.len() < 20 {
                    if let Ok(text) = std::fs::read_to_string(e.path())
                        && text.len() < 50_000
                    {
                        let rel = e.path().strip_prefix(root).map(|p| p.display().to_string()).unwrap_or(name);
                        out.push((rel, text));
                    }
                }
            }
        }
        let root = workspace_root();
        let mut out = Vec::new();
        walk(&root, &root, &mut out);
        out
    });
}

pub(crate) fn starter_files() -> &'static [(String, String)] {
    STARTER_FILES.get().map(Vec::as_slice).unwrap_or(&[])
}

/// The task statement: the longest plain-text user message in history (skips injected `<tag>` context).
pub(crate) async fn task_spec(sess: &crate::session::session::Session) -> String {
    let history = sess.clone_history().await;
    history
        .raw_items()
        .filter_map(|item| match item {
            codex_protocol::models::ResponseItem::Message { role, content, .. } if role == "user" => Some(
                content
                    .iter()
                    .filter_map(|c| match c {
                        codex_protocol::models::ContentItem::InputText { text } => Some(text.as_str()),
                        _ => None,
                    })
                    .collect::<Vec<_>>()
                    .join("\n"),
            ),
            _ => None,
        })
        .filter(|text| !text.trim_start().starts_with('<'))
        .max_by_key(String::len)
        .unwrap_or_default()
}

pub(crate) fn user_message(text: String) -> codex_protocol::models::ResponseItem {
    codex_protocol::models::ResponseItem::Message {
        id: Some(codex_protocol::ResponseItemId::new("msg")),
        role: "user".to_string(),
        content: vec![codex_protocol::models::ContentItem::InputText { text }],
        phase: None,
        internal_chat_message_metadata_passthrough: None,
    }
}
