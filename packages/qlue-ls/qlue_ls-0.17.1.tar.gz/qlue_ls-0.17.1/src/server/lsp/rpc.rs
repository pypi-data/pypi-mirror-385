use std::{any::type_name, collections::HashMap, fmt::Display};

use log::error;
use serde::{de::DeserializeOwned, Deserialize, Serialize};

use crate::server::lsp::{LspMessage, ResponseMarker};

use super::{
    base_types::LSPAny,
    errors::{ErrorCode, LSPError},
};

#[derive(Serialize, Deserialize, Debug, PartialEq)]
#[serde(untagged)]
pub enum RPCMessage {
    Request(RequestMessage),
    Response(ResponseMessage),
    Notification(NotificationMessage),
}

impl RPCMessage {
    // pub fn get_id(&self) -> Option<&RequestId> {
    //     match self {
    //         RPCMessage::Request(request_message) => Some(&request_message.id),
    //         RPCMessage::Response(response_message) => match &response_message.id {
    //             RequestIdOrNull::RequestId(request_id) => Some(&request_id),
    //             RequestIdOrNull::Null => None,
    //         },
    //         _ => None,
    //     }
    // }
    pub fn get_method(&self) -> Option<&str> {
        match self {
            RPCMessage::Notification(notification) => Some(&notification.method),
            RPCMessage::Request(request) => Some(&request.method),
            RPCMessage::Response(_) => None,
        }
    }

    pub fn parse<T>(&self) -> Result<T, LSPError>
    where
        T: DeserializeOwned,
    {
        match serde_json::to_string(self) {
            Ok(serialized_message) => serde_json::from_str(&serialized_message).map_err(|error| {
                LSPError::new(
                    ErrorCode::ParseError,
                    &format!(
                        "Could not deserialize RPC-message \"{}\"\n\n{}",
                        type_name::<T>(),
                        error
                    ),
                )
            }),
            Err(error) => Err(LSPError::new(
                ErrorCode::ParseError,
                &format!("Could not serialize RPC-message\n\n{}", error),
            )),
        }
    }
}

#[derive(Serialize, Deserialize, Debug, PartialEq)]
pub struct Message {
    pub jsonrpc: String,
}

impl Message {
    pub fn new() -> Self {
        Self {
            jsonrpc: "2.0".to_string(),
        }
    }
}

// NOTE: The only purpouse of this struct is to recover
// the id of a message in case a error occurs
#[derive(Serialize, Deserialize, Debug, PartialEq)]
pub struct RecoverId {
    pub id: RequestId,
}

#[derive(Serialize, Deserialize, Debug, PartialEq)]
pub struct RequestMessage {
    #[serde(flatten)]
    pub base: Message,
    /**
     * The request id.
     */
    pub id: RequestId,
    /**
     * The method to be invoked.
     */
    pub method: String,
    /**
     * The method's params.
     */
    pub params: Option<Params>,
}

#[derive(Deserialize, Serialize, Debug, PartialEq)]
pub struct RequestMessageBase {
    #[serde(flatten)]
    pub base: Message,
    /**
     * The request id.
     */
    pub id: RequestId,
    /**
     * The method to be invoked.
     */
    pub method: String,
}
impl RequestMessageBase {
    pub(crate) fn new(method: &str, id: u32) -> Self {
        Self {
            base: Message::new(),
            id: RequestId::Integer(id),
            method: method.to_string(),
        }
    }
}

#[derive(Serialize, Deserialize, Debug, PartialEq, Clone)]
#[serde(untagged)]
pub enum RequestId {
    String(String),
    Integer(u32),
}

impl Display for RequestId {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            RequestId::String(str) => write!(f, "{}", str),
            RequestId::Integer(int) => write!(f, "{}", int),
        }
    }
}

#[derive(Serialize, Deserialize, Debug, PartialEq)]
#[serde(untagged)]
pub enum Params {
    Array(Vec<serde_json::Value>),
    Object(HashMap<String, serde_json::Value>),
}

#[derive(Serialize, Deserialize, Debug, PartialEq)]
pub struct ResponseMessage {
    #[serde(flatten)]
    pub base: Message,
    /**
     * The request id.
     */
    pub id: RequestIdOrNull,
    /**
     * The result of a request. This member is REQUIRED on success.
     * This member MUST NOT exist if there was an error invoking the method.
     */
    pub result: Option<LSPAny>,
    /**
     * The error object in case a request fails.
     */
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error: Option<LSPError>,
}

impl LspMessage for ResponseMessage {
    type Kind = ResponseMarker;

    fn method(&self) -> Option<&str> {
        None
    }

    fn id(&self) -> Option<&RequestId> {
        self.id.request_id()
    }
}

impl ResponseMessage {
    pub fn error(id: RequestIdOrNull, error: LSPError) -> Self {
        Self {
            base: Message::new(),
            id,
            result: None,
            error: Some(error),
        }
    }
}

#[derive(Serialize, Deserialize, Debug, PartialEq)]
#[serde(untagged)]
pub enum RequestIdOrNull {
    RequestId(RequestId),
    Null,
}

impl RequestIdOrNull {
    pub fn request_id(&self) -> Option<&RequestId> {
        match self {
            RequestIdOrNull::RequestId(request_id) => Some(request_id),
            RequestIdOrNull::Null => None,
        }
    }
}

#[derive(Serialize, Deserialize, Debug, PartialEq)]
pub struct ResponseMessageBase {
    #[serde(flatten)]
    pub base: Message,
    /**
     * The request id.
     */
    pub id: RequestIdOrNull,
    //The result of a request. This member is REQUIRED on success.
    // This member MUST NOT exist if there was an error invoking the method.
    // NOTE: This is omitted due to the flatten serde mechanism
    // pub result: Option<LSPAny>,
    /**
     * The error object in case a request fails.
     */

    #[serde(skip_serializing_if = "Option::is_none")]
    pub error: Option<LSPError>,
}

impl ResponseMessageBase {
    pub fn success(id: &RequestId) -> Self {
        Self {
            base: Message::new(),
            id: RequestIdOrNull::RequestId(id.clone()),
            error: None,
        }
    }
    pub fn request_id(&self) -> Option<&RequestId> {
        self.id.request_id()
    }
}

#[derive(Serialize, Deserialize, Debug, PartialEq)]
pub struct NotificationMessage {
    #[serde(flatten)]
    pub base: Message,
    /**
     * The method to be invoked.
     */
    pub method: String,
    /*
     * The notification's params.
     */
    pub params: Option<Params>,
}

#[derive(Serialize, Deserialize, Debug, PartialEq)]
pub struct NotificationMessageBase {
    #[serde(flatten)]
    pub base: Message,
    /**
     * The method to be invoked.
     */
    pub method: String,
}

impl NotificationMessageBase {
    pub(crate) fn new(method: &str) -> Self {
        Self {
            base: Message::new(),
            method: method.to_string(),
        }
    }
}

pub fn deserialize_message(message: &str) -> Result<RPCMessage, LSPError> {
    serde_json::from_str(message).map_err(|error| {
        error!(
            "Error while serializing message:\n{}-----------------------\n{}",
            error, message,
        );
        LSPError::new(
            ErrorCode::ParseError,
            &format!("Could not serialize RPC-Message:\n\n{}", error),
        )
    })
}

#[cfg(test)]
mod tests {

    use std::collections::HashMap;

    use serde_json::json;

    use crate::server::lsp::{
        base_types::LSPAny,
        rpc::{
            deserialize_message, Message, NotificationMessage, Params, RequestId, RequestIdOrNull,
            RequestMessage, ResponseMessage,
        },
    };

    use super::RPCMessage;

    #[test]
    fn serialize() {
        let message = RPCMessage::Request(RequestMessage {
            base: Message::new(),
            id: RequestId::Integer(1),
            method: "initialize".to_owned(),
            params: Some(Params::Array(vec![])),
        });
        let serialized = serde_json::to_string(&message).unwrap();
        assert_eq!(
            serialized,
            r#"{"jsonrpc":"2.0","id":1,"method":"initialize","params":[]}"#
        );
    }

    #[test]
    fn deserialize_notification() {
        let maybe_initialized =
            deserialize_message(r#"{"params":{"a":2},"jsonrpc":"2.0","method":"initialized"}"#)
                .unwrap();
        assert_eq!(
            maybe_initialized,
            RPCMessage::Notification(NotificationMessage {
                base: Message::new(),
                method: "initialized".to_owned(),
                params: Some(Params::Object(HashMap::from([("a".to_string(), json!(2))])))
            })
        );
    }

    #[test]
    fn deserialize_request() {
        let maybe_request = deserialize_message(
            r#"{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"a":[1,2,3]}}"#,
        );
        assert_eq!(
            maybe_request,
            Ok(RPCMessage::Request(RequestMessage {
                base: Message::new(),
                id: RequestId::Integer(1),
                method: "initialize".to_owned(),
                params: Some(Params::Object(HashMap::from([(
                    "a".to_string(),
                    json!([1, 2, 3])
                )])))
            }))
        );
    }

    #[test]
    fn deserialize_response() {
        let maybe_response = deserialize_message(r#"{"jsonrpc":"2.0","id":1,"result":{"a":1}}"#);
        assert_eq!(
            maybe_response,
            Ok(RPCMessage::Response(ResponseMessage {
                base: Message::new(),
                id: RequestIdOrNull::RequestId(RequestId::Integer(1)),
                error: None,
                result: Some(LSPAny::LSPObject(HashMap::from([(
                    "a".to_string(),
                    LSPAny::Uinteger(1)
                )])))
            }))
        );
    }
}
