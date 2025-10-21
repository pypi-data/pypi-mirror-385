use serde::{Deserialize, Serialize};
use serde_repr::{Deserialize_repr, Serialize_repr};

#[derive(Debug, Serialize, PartialEq, Clone)]
#[serde(rename_all = "camelCase")]
pub struct ServerCapabilities {
    pub text_document_sync: TextDocumentSyncKind,
    pub hover_provider: bool,
    pub completion_provider: CompletionOptions,
    pub document_formatting_provider: DocumentFormattingOptions,
    pub diagnostic_provider: DiagnosticOptions,
    pub code_action_provider: bool,
    pub execute_command_provider: ExecuteCommandOptions,
    pub folding_range_provider: bool,
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
pub struct ExecuteCommandOptions {
    #[serde(flatten)]
    pub work_done_progress_options: WorkDoneProgressOptions,
    pub commands: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
#[serde(rename_all = "camelCase")]
pub struct WorkDoneProgressOptions {
    pub work_done_progress: bool,
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
#[serde(rename_all = "camelCase")]
pub struct DiagnosticOptions {
    pub identifier: String,
    pub inter_file_dependencies: bool,
    pub workspace_diagnostics: bool,
}

#[derive(Debug, Serialize_repr, Deserialize_repr, PartialEq, Clone)]
#[repr(u8)]
pub enum TextDocumentSyncKind {
    None = 0,
    Full = 1,
    Incremental = 2,
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
#[serde(rename_all = "camelCase")]
pub struct CompletionOptions {
    // WARNING: This is not to spec, there are more optional options:
    // https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#completionOptions
    pub trigger_characters: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone)]
pub struct DocumentFormattingOptions {
    // WARNING: This could also inherit WorkDoneProgressOptions (not implemented yet).
}

// https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#clientCapabilities
#[derive(Debug, Deserialize, PartialEq, Clone)]
pub struct ClientCapabilities {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub workspace: Option<WorkspaceCapablities>,
}

#[derive(Debug, Deserialize, PartialEq, Clone)]
#[serde(rename_all = "camelCase")]
pub struct WorkspaceCapablities {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub apply_edit: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub workspace_edit: Option<WorkspaceEditClientCapabilities>,
}

#[derive(Debug, Deserialize, PartialEq, Clone)]
#[serde(rename_all = "camelCase")]
pub struct WorkspaceEditClientCapabilities {
    pub document_changes: Option<bool>,
}

#[cfg(test)]
mod tests {

    use crate::server::lsp::capabilities::{
        CompletionOptions, DiagnosticOptions, DocumentFormattingOptions, ExecuteCommandOptions,
        TextDocumentSyncKind, WorkDoneProgressOptions,
    };

    use super::ServerCapabilities;

    #[test]
    fn serialize() {
        let server_capabilities = ServerCapabilities {
            text_document_sync: TextDocumentSyncKind::Full,
            hover_provider: true,
            completion_provider: CompletionOptions {
                trigger_characters: vec!["?".to_string()],
            },
            document_formatting_provider: DocumentFormattingOptions {},
            diagnostic_provider: DiagnosticOptions {
                identifier: "my-ls".to_string(),
                inter_file_dependencies: false,
                workspace_diagnostics: false,
            },
            code_action_provider: true,
            execute_command_provider: ExecuteCommandOptions {
                work_done_progress_options: WorkDoneProgressOptions {
                    work_done_progress: true,
                },
                commands: vec!["foo".to_string()],
            },
            folding_range_provider: true,
        };

        let serialized = serde_json::to_string(&server_capabilities).unwrap();

        assert_eq!(
            serialized,
            r#"{"textDocumentSync":1,"hoverProvider":true,"completionProvider":{"triggerCharacters":["?"]},"documentFormattingProvider":{},"diagnosticProvider":{"identifier":"my-ls","interFileDependencies":false,"workspaceDiagnostics":false},"codeActionProvider":true,"executeCommandProvider":{"workDoneProgress":true,"commands":["foo"]},"foldingRangeProvider":true}"#
        );
    }
}
