use std::collections::HashMap;

use serde::{Deserialize, Serialize};
use serde_repr::{Deserialize_repr, Serialize_repr};

use crate::server::lsp::{
    rpc::{RequestId, RequestMessageBase, ResponseMessageBase},
    textdocument::{DocumentUri, Range, TextDocumentIdentifier, TextEdit},
    LspMessage, RequestMarker, ResponseMarker,
};

use super::{diagnostic::Diagnostic, workspace::WorkspaceEdit};

#[derive(Debug, Deserialize)]
pub struct CodeActionRequest {
    #[serde(flatten)]
    pub base: RequestMessageBase,
    pub params: CodeActionParams,
}
impl CodeActionRequest {
    pub(crate) fn get_id(&self) -> &RequestId {
        &self.base.id
    }
}

impl LspMessage for CodeActionRequest {
    type Kind = RequestMarker;

    fn method(&self) -> Option<&str> {
        Some("textDocument/codeAction")
    }

    fn id(&self) -> Option<&RequestId> {
        Some(&self.base.id)
    }
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CodeActionParams {
    pub text_document: TextDocumentIdentifier,
    pub range: Range,
    pub context: CodeActionContext,
}

#[derive(Debug, Serialize, Deserialize, Hash, Eq, PartialEq)]
#[serde(rename_all = "lowercase")]
pub enum CodeActionKind {
    #[serde(rename = "")]
    Empty,
    QuickFix,
    Refactor,
    #[serde(rename = "refactor.extract")]
    RefactorExtract,
    #[serde(rename = "refactor.inline")]
    RefactorInline,
    #[serde(rename = "refactor.rewrite")]
    RefactorRewrite,
    Source,
    #[serde(rename = "source.shortenUris")]
    SourceShortenURIs,
    #[serde(rename = "source.organizeImports")]
    SourceOrganizeImports,
    #[serde(rename = "source.fixAll")]
    SourceFixAll,
}

#[derive(Debug, Deserialize)]
pub struct CodeActionContext {
    pub diagnostics: Vec<Diagnostic>,
    // pub only: Option<Vec<CodeActionKind>>,
    // trigger_kind: Option<CodeActionTriggerKind>,
}

#[derive(Debug, Serialize_repr, Deserialize_repr)]
#[repr(u8)]
pub enum CodeActionTriggerKind {
    Invoked = 1,
    Automatic = 2,
}

#[derive(Debug, Serialize)]
pub struct CodeActionResponse {
    #[serde(flatten)]
    base: ResponseMessageBase,
    result: Vec<CodeAction>,
}

impl LspMessage for CodeActionResponse {
    type Kind = ResponseMarker;

    fn method(&self) -> Option<&str> {
        None
    }

    fn id(&self) -> Option<&RequestId> {
        self.base.request_id()
    }
}

impl CodeActionResponse {
    pub fn new(id: &RequestId) -> Self {
        Self {
            base: ResponseMessageBase::success(id),
            result: vec![],
        }
    }

    #[cfg(test)]
    pub(crate) fn add_code_action(&mut self, code_action: CodeAction) {
        self.result.push(code_action);
    }

    pub(crate) fn add_code_actions(&mut self, code_actions: Vec<CodeAction>) {
        self.result.extend(code_actions);
    }
}

#[derive(Debug, Serialize)]
pub struct CodeAction {
    pub title: String,
    pub edit: WorkspaceEdit,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub kind: Option<CodeActionKind>,
    #[serde(skip_serializing_if = "Vec::is_empty")]
    pub diagnostics: Vec<Diagnostic>,
    // NOTE: there are more optional options:
    // isPreferred: boolean
    // disabled: { reason }
    // command: Command
    // data: LSPAny
}

impl CodeAction {
    pub fn new(title: &str, kind: Option<CodeActionKind>) -> Self {
        Self {
            title: title.to_string(),
            kind,
            edit: WorkspaceEdit {
                changes: Some(HashMap::new()),
            },
            diagnostics: vec![],
        }
    }

    pub(crate) fn add_edit(&mut self, document_uri: &DocumentUri, change: TextEdit) {
        if let Some(changes) = self.edit.changes.as_mut() {
            changes
                .entry(document_uri.to_string())
                .and_modify(|e| e.push(change.clone()))
                .or_insert(vec![change]);
        }
    }
}

#[cfg(test)]
mod test {
    use crate::server::lsp::{
        rpc::RequestId,
        textdocument::{Range, TextEdit},
        CodeAction, CodeActionResponse, WorkspaceEdit,
    };
    use std::collections::HashMap;

    #[test]
    fn serialize() {
        let mut code_action_response = CodeActionResponse::new(&RequestId::Integer(42));
        let changes = Some(HashMap::from([(
            "file:///test.rq".to_string(),
            vec![TextEdit::new(Range::new(0, 0, 0, 0), "test")],
        )]));
        let code_action = CodeAction {
            title: "test-action".to_string(),
            kind: None,
            diagnostics: vec![],
            edit: WorkspaceEdit { changes },
        };
        code_action_response.add_code_action(code_action);
        let serialized_response = serde_json::to_string(&code_action_response).unwrap();
        assert_eq!(
            serialized_response,
            r#"{"jsonrpc":"2.0","id":42,"result":[{"title":"test-action","edit":{"changes":{"file:///test.rq":[{"range":{"start":{"line":0,"character":0},"end":{"line":0,"character":0}},"newText":"test"}]}}}]}"#
        )
    }
}
