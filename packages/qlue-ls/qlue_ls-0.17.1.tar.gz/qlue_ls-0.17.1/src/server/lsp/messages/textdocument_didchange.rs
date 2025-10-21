use core::fmt;

use serde::{Deserialize, Serialize};

use crate::server::lsp::{
    rpc::NotificationMessage,
    textdocument::{Range, VersionedTextDocumentIdentifier},
    LspMessage, NotificationMarker,
};

#[derive(Debug, Serialize, Deserialize, PartialEq)]
pub struct DidChangeTextDocumentNotification {
    #[serde(flatten)]
    base: NotificationMessage,
    pub params: DidChangeTextDocumentParams,
}

impl LspMessage for DidChangeTextDocumentNotification {
    type Kind = NotificationMarker;

    fn method(&self) -> Option<&str> {
        Some("textDocument/didChange")
    }

    fn id(&self) -> Option<&crate::server::lsp::rpc::RequestId> {
        None
    }
}

#[derive(Debug, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "camelCase")]
pub struct DidChangeTextDocumentParams {
    pub text_document: VersionedTextDocumentIdentifier,
    pub content_changes: Vec<TextDocumentContentChangeEvent>,
}

// https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocumentContentChangeEvent
#[derive(Debug, Serialize, Deserialize, PartialEq)]
pub struct TextDocumentContentChangeEvent {
    pub range: Range,
    pub text: String,
}

impl fmt::Display for TextDocumentContentChangeEvent {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(
            f,
            "\"{}\"; [{}-{}]",
            self.text, self.range.start, self.range.end
        )
    }
}
