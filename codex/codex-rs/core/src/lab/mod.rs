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
