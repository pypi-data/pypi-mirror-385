/*
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

use lsp_server::Message;
use lsp_server::Notification;
use lsp_server::Request;
use lsp_server::RequestId;
use lsp_server::Response;
use lsp_types::Url;

use crate::test::lsp::lsp_interaction::object_model::InitializeSettings;
use crate::test::lsp::lsp_interaction::object_model::LspInteraction;
use crate::test::lsp::lsp_interaction::util::get_test_files_root;

#[test]
fn test_completion_basic() {
    let root = get_test_files_root();
    let mut interaction = LspInteraction::new();
    interaction.set_root(root.path().to_path_buf());
    interaction.initialize(InitializeSettings::default());

    interaction.server.did_open("foo.py");

    let foo_path = root.path().join("foo.py");
    interaction
        .server
        .send_message(Message::Notification(Notification {
            method: "textDocument/didChange".to_owned(),
            params: serde_json::json!({
                "textDocument": {
                    "uri": Url::from_file_path(&foo_path).unwrap().to_string(),
                    "languageId": "python",
                    "version": 2
                },
                "contentChanges": [{
                    "range": {
                        "start": {"line": 10, "character": 0},
                        "end": {"line": 12, "character": 0}
                    },
                    "text": format!("\n{}\n", "Ba")
                }],
            }),
        }));

    interaction.server.completion("foo.py", 11, 1);

    interaction.client.expect_response_with(
        |response| {
            if response.id != RequestId::from(2) {
                return false;
            }
            if let Some(result) = &response.result
                && let Some(items) = result.get("items")
                && let Some(items_array) = items.as_array()
            {
                return items_array.iter().any(|item| {
                    if let Some(label) = item.get("label")
                        && let Some(label_str) = label.as_str()
                    {
                        label_str == "Bar"
                    } else {
                        false
                    }
                });
            }
            false
        },
        "Expected completion response with 'Bar' in items",
    );

    interaction.shutdown();
}

#[test]
fn test_completion_sorted_in_sorttext_order() {
    let root = get_test_files_root();
    let mut interaction = LspInteraction::new();
    interaction.set_root(root.path().to_path_buf());
    interaction.initialize(InitializeSettings::default());

    interaction.server.did_open("foo.py");

    let foo_path = root.path().join("foo.py");
    interaction
        .server
        .send_message(Message::Notification(Notification {
            method: "textDocument/didChange".to_owned(),
            params: serde_json::json!({
                "textDocument": {
                    "uri": Url::from_file_path(&foo_path).unwrap().to_string(),
                    "languageId": "python",
                    "version": 2
                },
                "contentChanges": [{
                    "range": {
                        "start": {"line": 10, "character": 0},
                        "end": {"line": 12, "character": 0}
                    },
                    "text": format!("\n{}\n", "Ba")
                }],
            }),
        }));

    interaction.server.completion("foo.py", 11, 1);

    interaction.client.expect_response_with(
        |response| {
            if response.id != RequestId::from(2) {
                return false;
            }
            if let Some(result) = &response.result
                && let Some(items) = result.get("items")
                && let Some(items_array) = items.as_array()
            {
                let mut prev_sort_text: Option<String> = None;
                let mut prev_label: Option<String> = None;

                for item in items_array {
                    let sort_text = item.get("sortText").and_then(|v| v.as_str()).unwrap_or("");
                    let label = item.get("label").and_then(|v| v.as_str()).unwrap_or("");

                    if let Some(prev_st) = &prev_sort_text {
                        if sort_text < prev_st.as_str() {
                            return false;
                        }
                        if sort_text == prev_st.as_str()
                            && let Some(prev_l) = &prev_label
                            && label < prev_l.as_str()
                        {
                            return false;
                        }
                    }

                    prev_sort_text = Some(sort_text.to_owned());
                    prev_label = Some(label.to_owned());
                }

                return true;
            }
            false
        },
        "Expected completion items to be sorted by sortText then label",
    );

    interaction.shutdown();
}

#[test]
fn test_completion_keywords() {
    let root = get_test_files_root();
    let mut interaction = LspInteraction::new();
    interaction.set_root(root.path().to_path_buf());
    interaction.initialize(InitializeSettings::default());

    interaction.server.did_open("foo.py");

    let foo_path = root.path().join("foo.py");
    interaction
        .server
        .send_message(Message::Notification(Notification {
            method: "textDocument/didChange".to_owned(),
            params: serde_json::json!({
                "textDocument": {
                    "uri": Url::from_file_path(&foo_path).unwrap().to_string(),
                    "languageId": "python",
                    "version": 2
                },
                "contentChanges": [{
                    "range": {
                        "start": {"line": 10, "character": 0},
                        "end": {"line": 12, "character": 0}
                    },
                    "text": format!("\n{}\n", "i")
                }],
            }),
        }));

    interaction.server.completion("foo.py", 11, 1);

    interaction.client.expect_response_with(
        |response| {
            if response.id != RequestId::from(2) {
                return false;
            }
            if let Some(result) = &response.result
                && let Some(items) = result.get("items")
                && let Some(items_array) = items.as_array()
            {
                // Verify that common Python keywords are present
                let has_if = items_array.iter().any(|item| {
                    item.get("label").and_then(|v| v.as_str()) == Some("if")
                        && item.get("kind").and_then(|v| v.as_u64()) == Some(14) // KEYWORD kind
                });
                let has_import = items_array.iter().any(|item| {
                    item.get("label").and_then(|v| v.as_str()) == Some("import")
                        && item.get("kind").and_then(|v| v.as_u64()) == Some(14)
                });
                let has_def = items_array.iter().any(|item| {
                    item.get("label").and_then(|v| v.as_str()) == Some("def")
                        && item.get("kind").and_then(|v| v.as_u64()) == Some(14)
                });

                return has_if && has_import && has_def;
            }
            false
        },
        "Expected completion response to include Python keywords like 'if', 'import', 'def'",
    );

    interaction.shutdown();
}

#[test]
fn test_completion_with_autoimport() {
    let root = get_test_files_root();
    let root_path = root.path().join("tests_requiring_config");

    let mut interaction =
        LspInteraction::new_with_indexing_mode(crate::commands::lsp::IndexingMode::LazyBlocking);

    interaction.set_root(root_path.clone());
    interaction.initialize(InitializeSettings::default());

    let file = root_path.join("foo.py");
    interaction.server.did_open("foo.py");

    interaction
        .server
        .send_message(Message::Notification(Notification {
            method: "textDocument/didChange".to_owned(),
            params: serde_json::json!({
                "textDocument": {
                    "uri": Url::from_file_path(&file).unwrap().to_string(),
                    "languageId": "python",
                    "version": 2
                },
                "contentChanges": [{
                    "text": "this_is_a_very_long_function_name_so_we_can".to_owned()
                }],
            }),
        }));

    interaction.server.completion("foo.py", 0, 43);

    interaction.client.expect_response_with(
        |response| {
            if response.id != RequestId::from(2) {
                return false;
            }
            if let Some(result) = &response.result
                && let Some(items) = result.get("items")
                && let Some(items_array) = items.as_array()
            {
                return items_array.iter().any(|item| {
                    if let Some(label) = item.get("label")
                        && let Some(label_str) = label.as_str()
                        && let Some(detail) = item.get("detail")
                        && let Some(detail_str) = detail.as_str()
                        && let Some(additional_text_edits) = item.get("additionalTextEdits")
                        && let Some(edits_array) = additional_text_edits.as_array()
                    {
                        label_str == "this_is_a_very_long_function_name_so_we_can_deterministically_test_autoimport_with_fuzzy_search"
                            && detail_str.contains("from autoimport_provider import")
                            && !edits_array.is_empty()
                    } else {
                        false
                    }
                });
            }
            false
        },
        "Expected completion response with autoimport suggestion",
    );

    interaction.shutdown();
}

#[test]
fn test_completion_with_autoimport_without_config() {
    let root = get_test_files_root();
    let mut interaction = LspInteraction::new();
    let root_path = root.path();
    let scope_uri = Url::from_file_path(root_path).unwrap();

    interaction.set_root(root_path.to_path_buf());
    interaction.initialize(InitializeSettings {
        workspace_folders: Some(vec![("test".to_owned(), scope_uri)]),
        ..Default::default()
    });

    let foo_path = root_path.join("foo.py");
    interaction.server.did_open("foo.py");

    interaction
        .server
        .send_message(Message::Notification(Notification {
            method: "textDocument/didChange".to_owned(),
            params: serde_json::json!({
                "textDocument": {
                    "uri": Url::from_file_path(&foo_path).unwrap().to_string(),
                    "languageId": "python",
                    "version": 2
                },
                "contentChanges": [{
                    "text": "Bar".to_owned()
                }],
            }),
        }));

    interaction.server.completion("foo.py", 0, 3);

    interaction.client.expect_response_with(
        |response| {
            if response.id != RequestId::from(2) {
                return false;
            }
            if let Some(result) = &response.result
                && let Some(items) = result.get("items")
                && let Some(items_array) = items.as_array()
            {
                return !items_array.is_empty();
            }
            false
        },
        "Expected completion response with items",
    );

    interaction.shutdown();
}

#[test]
fn test_completion_with_autoimport_in_defined_module() {
    let root = get_test_files_root();
    let mut interaction = LspInteraction::new();
    let root_path = root.path().join("tests_requiring_config");
    let scope_uri = Url::from_file_path(&root_path).unwrap();

    interaction.set_root(root_path.clone());
    interaction.initialize(InitializeSettings {
        workspace_folders: Some(vec![("test".to_owned(), scope_uri)]),
        ..Default::default()
    });

    let file = root_path.join("autoimport_provider.py");
    interaction.server.did_open("autoimport_provider.py");

    let file_content = std::fs::read_to_string(&file).unwrap();
    interaction
        .server
        .send_message(Message::Notification(Notification {
            method: "textDocument/didChange".to_owned(),
            params: serde_json::json!({
                "textDocument": {
                    "uri": Url::from_file_path(&file).unwrap().to_string(),
                    "languageId": "python",
                    "version": 2
                },
                "contentChanges": [{
                    "text": format!("{}\n{}", file_content, "this_is_a_very_long_function_name_so_we_can")
                }],
            }),
        }));

    interaction.server.send_message(Message::Request(Request {
        id: RequestId::from(2),
        method: "textDocument/completion".to_owned(),
        params: serde_json::json!({
            "textDocument": {
                "uri": Url::from_file_path(&file).unwrap().to_string()
            },
            "position": {
                "line": 12,
                "character": 95
            }
        }),
    }));

    interaction.client.expect_response_with(
        |response| {
            if response.id != RequestId::from(2) {
                return false;
            }
            if let Some(result) = &response.result
                && let Some(items) = result.get("items")
                && let Some(items_array) = items.as_array()
            {
                return items_array.iter().any(|item| {
                    if let Some(label) = item.get("label")
                        && let Some(label_str) = label.as_str()
                        && let Some(detail) = item.get("detail")
                        && let Some(detail_str) = detail.as_str()
                    {
                        label_str == "this_is_a_very_long_function_name_so_we_can_deterministically_test_autoimport_with_fuzzy_search"
                            && detail_str == "() -> None"
                    } else {
                        false
                    }
                });
            }
            false
        },
        "Expected completion response with local function",
    );

    interaction.shutdown();
}

#[test]
fn test_completion_with_autoimport_duplicates() {
    let root = get_test_files_root();
    let mut interaction = LspInteraction::new();
    let root_path = root.path().join("duplicate_export_test");
    let scope_uri = Url::from_file_path(&root_path).unwrap();

    interaction.set_root(root_path.clone());
    interaction.initialize(InitializeSettings {
        workspace_folders: Some(vec![("test".to_owned(), scope_uri)]),
        ..Default::default()
    });

    interaction.server.did_open("foo.py");

    interaction.server.completion("foo.py", 5, 14);

    interaction.client.expect_response_with(
        |response| {
            if response.id != RequestId::from(2) {
                return false;
            }
            if let Some(result) = &response.result
                && let Some(items) = result.get("items")
                && let Some(items_array) = items.as_array()
            {
                return !items_array.is_empty();
            }
            false
        },
        "Expected completion response with items",
    );

    interaction.shutdown();
}

#[test]
fn test_module_completion() {
    let root = get_test_files_root();
    let mut interaction = LspInteraction::new();
    interaction.set_root(root.path().join("tests_requiring_config"));
    interaction.initialize(InitializeSettings::default());

    interaction.server.did_open("foo.py");

    interaction.server.completion("foo.py", 5, 10);

    interaction.client.expect_response(Response {
        id: RequestId::from(2),
        result: Some(serde_json::json!({
            "isIncomplete": false,
            "items": [{
                "label": "bar",
                "detail": "bar",
                "kind": 9,
                "sortText": "0"
            }],
        })),
        error: None,
    });

    interaction.shutdown();
}

#[test]
fn test_module_completion_reexports_sorted_lower() {
    let root = get_test_files_root();
    let mut interaction = LspInteraction::new();
    interaction.set_root(root.path().join("reexport_test"));
    interaction.initialize(InitializeSettings::default());

    interaction.server.did_open("test.py");

    let test_path = root.path().join("reexport_test/test.py");
    interaction
        .server
        .send_message(Message::Notification(Notification {
            method: "textDocument/didChange".to_owned(),
            params: serde_json::json!({
                "textDocument": {
                    "uri": Url::from_file_path(&test_path).unwrap().to_string(),
                    "languageId": "python",
                    "version": 2
                },
                "contentChanges": [{
                    "text": "import module_with_reexports\n\nmodule_with_reexports.".to_owned()
                }],
            }),
        }));

    interaction.server.completion("test.py", 2, 23);

    interaction.client.expect_response_with(
        |response| {
            if response.id != RequestId::from(2) {
                return false;
            }
            if let Some(result) = &response.result
                && let Some(items) = result.get("items")
                && let Some(items_array) = items.as_array()
            {
                let mut direct_definitions = vec![];
                let mut reexports = vec![];

                for item in items_array {
                    let label = item.get("label").and_then(|v| v.as_str()).unwrap_or("");
                    let sort_text = item.get("sortText").and_then(|v| v.as_str()).unwrap_or("");

                    if label == "another_direct_function" || label == "AnotherDirectClass" {
                        direct_definitions.push((label.to_owned(), sort_text.to_owned()));
                    } else if label == "reexported_function" || label == "ReexportedClass" {
                        reexports.push((label.to_owned(), sort_text.to_owned()));
                    }
                }

                if direct_definitions.is_empty() || reexports.is_empty() {
                    return false;
                }

                for (direct_label, direct_sort) in &direct_definitions {
                    for (reexport_label, reexport_sort) in &reexports {
                        if reexport_sort <= direct_sort {
                            eprintln!(
                                "Re-export '{}' (sortText: {}) should be sorted lower than direct definition '{}' (sortText: {})",
                                reexport_label, reexport_sort, direct_label, direct_sort
                            );
                            return false;
                        }
                    }
                }

                return true;
            }
            false
        },
        "Expected re-exports to be sorted lower than direct definitions in module completions",
    );

    interaction.shutdown();
}

#[test]
fn test_relative_module_completion() {
    let root = get_test_files_root();
    let mut interaction = LspInteraction::new();
    interaction.set_root(root.path().to_path_buf());
    interaction.initialize(InitializeSettings::default());

    interaction
        .server
        .did_open("relative_test/relative_import.py");

    interaction
        .server
        .completion("relative_test/relative_import.py", 5, 10);

    interaction.client.expect_response(Response {
        id: RequestId::from(2),
        result: Some(serde_json::json!({
            "isIncomplete": false,
            "items": [],
        })),
        error: None,
    });

    interaction.shutdown();
}
