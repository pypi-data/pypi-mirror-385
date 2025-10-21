use serde::{Deserialize, Serialize};

use crate::server::lsp::{
    rpc::{RequestId, RequestMessageBase, ResponseMessageBase},
    textdocument::Position,
    LspMessage, RequestMarker, ResponseMarker,
};

use super::utils::TextDocumentPositionParams;

#[derive(Debug, Deserialize, PartialEq)]
pub struct HoverRequest {
    #[serde(flatten)]
    base: RequestMessageBase,
    params: HoverParams,
}

impl LspMessage for HoverRequest {
    type Kind = RequestMarker;

    fn method(&self) -> Option<&str> {
        Some("textDocument/hover")
    }

    fn id(&self) -> Option<&RequestId> {
        Some(&self.base.id)
    }
}

impl HoverRequest {
    pub fn get_position(&self) -> &Position {
        &self.params.text_document_position.position
    }

    pub fn get_document_uri(&self) -> &String {
        &self.params.text_document_position.text_document.uri
    }

    pub(crate) fn get_id(&self) -> &RequestId {
        &self.base.id
    }
}

#[derive(Debug, Deserialize, PartialEq)]
struct HoverParams {
    #[serde(flatten)]
    text_document_position: TextDocumentPositionParams,
}

#[derive(Debug, Serialize, PartialEq)]
pub struct HoverResponse {
    #[serde(flatten)]
    base: ResponseMessageBase,
    result: Option<Hover>,
}

impl LspMessage for HoverResponse {
    type Kind = ResponseMarker;

    fn method(&self) -> Option<&str> {
        Some("textDocument/hover")
    }

    fn id(&self) -> Option<&RequestId> {
        self.base.request_id()
    }
}

impl HoverResponse {
    pub fn new(id: &RequestId) -> Self {
        HoverResponse {
            base: ResponseMessageBase::success(id),
            result: None,
        }
    }

    pub fn set_markdown_content(&mut self, content: String) {
        self.result = Some(Hover {
            contents: HoverResultContents::MarkupContent(MarkupContent::Content {
                kind: Markupkind::Markdown,
                value: content,
            }),
        })
    }
}

#[derive(Debug, Serialize, PartialEq)]
struct Hover {
    contents: HoverResultContents,
}

#[derive(Debug, Serialize, PartialEq)]
#[serde(untagged)]
#[allow(dead_code)]
enum HoverResultContents {
    //SingleMarkedString(MarkedString),
    MultipleMarkedString(Vec<MarkedString>),
    MarkupContent(MarkupContent),
    //WARNING: This is not to spec, the hover.contents also support markup content
    //see: https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_hover
}

#[derive(Debug, Serialize, PartialEq)]
#[serde(untagged)]
#[allow(dead_code)]
enum MarkedString {
    Content { language: String, value: String },
}

#[derive(Debug, Serialize, PartialEq)]
#[serde(untagged)]
enum MarkupContent {
    Content { kind: Markupkind, value: String },
}

#[derive(Debug, Serialize, PartialEq)]
#[serde(rename_all = "camelCase")]
#[allow(dead_code)]
pub enum Markupkind {
    Plaintext,
    Markdown,
}

#[cfg(test)]
mod tests {

    use crate::server::lsp::{
        messages::{textdocument_hover::HoverParams, utils::TextDocumentPositionParams},
        rpc::{Message, RequestId, RequestMessageBase},
        textdocument::{Position, TextDocumentIdentifier},
    };

    use super::{HoverRequest, HoverResponse};

    #[test]
    fn deserialize() {
        let message = br#"{"params":{"textDocument":{"uri":"file:///dings"},"position":{"character":42,"line":3}},"method":"textDocument/hover","id":2,"jsonrpc":"2.0"}"#;
        let hover_request: HoverRequest = serde_json::from_slice(message).unwrap();

        assert_eq!(
            hover_request,
            HoverRequest {
                base: RequestMessageBase {
                    base: Message {
                        jsonrpc: "2.0".to_string(),
                    },
                    method: "textDocument/hover".to_string(),
                    id: RequestId::Integer(2)
                },
                params: HoverParams {
                    text_document_position: TextDocumentPositionParams {
                        text_document: TextDocumentIdentifier {
                            uri: "file:///dings".to_string()
                        },
                        position: Position::new(3, 42)
                    }
                }
            }
        )
    }

    #[test]
    fn serialize() {
        let mut hover_response = HoverResponse::new(&RequestId::Integer(42));
        hover_response.set_markdown_content("hover content".to_string());
        let expected_message = r#"{"jsonrpc":"2.0","id":42,"result":{"contents":{"kind":"markdown","value":"hover content"}}}"#;
        assert_eq!(
            serde_json::to_string(&hover_response).unwrap(),
            expected_message
        );
    }
}
