use crate::server::{
    lsp::{
        base_types::LSPAny,
        diagnostic::{Diagnostic, DiagnosticCode, DiagnosticSeverity},
        textdocument::{Range, TextDocumentItem},
    },
    Server,
};
use ll_sparql_parser::ast::{AstNode, PrefixedName, QueryUnit};
use std::{collections::HashSet, sync::LazyLock};

pub static CODE: LazyLock<DiagnosticCode> =
    LazyLock::new(|| DiagnosticCode::String("undeclared-prefix".to_string()));

pub(super) fn diagnostics(
    document: &TextDocumentItem,
    query_unit: &QueryUnit,
    _server: &Server,
) -> Option<Vec<Diagnostic>> {
    let prefixed_names = query_unit
        .select_query()?
        .collect_decendants(&PrefixedName::can_cast)
        .into_iter()
        .map(|node| PrefixedName::cast(node).unwrap());

    let declared_prefixes: HashSet<String> = HashSet::from_iter(
        query_unit
            .prologue()
            .map_or(Vec::new(), |prologue| prologue.prefix_declarations())
            .iter()
            .filter_map(|prefix_decl| prefix_decl.prefix()),
    );

    Some(
        prefixed_names
            .into_iter()
            .filter_map(|prefixed_name| {
                (!declared_prefixes.contains(&prefixed_name.prefix())).then(|| Diagnostic {
                    range: Range::from_byte_offset_range(
                        prefixed_name.syntax().text_range(),
                        &document.text,
                    )
                    .expect("prefix declaration text range should be in text"),
                    severity: DiagnosticSeverity::Error,
                    source: Some("qlue-ls".to_string()),
                    code: Some((*CODE).clone()),
                    message: format!(
                        "'{}' is used here, but was never declared\n",
                        prefixed_name.prefix()
                    ),
                    data: Some(LSPAny::String(prefixed_name.prefix())),
                })
            })
            .collect(),
    )
}
