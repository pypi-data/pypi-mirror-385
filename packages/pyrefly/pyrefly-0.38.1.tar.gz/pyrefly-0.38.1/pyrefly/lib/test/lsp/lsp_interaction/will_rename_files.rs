/*
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

use lsp_server::RequestId;
use lsp_server::Response;
use lsp_types::Url;

use crate::commands::lsp::IndexingMode;
use crate::test::lsp::lsp_interaction::object_model::InitializeSettings;
use crate::test::lsp::lsp_interaction::object_model::LspInteraction;
use crate::test::lsp::lsp_interaction::util::get_test_files_root;

#[test]
fn test_will_rename_files_changes_open_files_when_indexing_disabled() {
    let root = get_test_files_root();
    let mut interaction = LspInteraction::new_with_indexing_mode(IndexingMode::None);
    interaction.set_root(root.path().to_path_buf());
    interaction.initialize(InitializeSettings::default());

    let foo = "tests_requiring_config/foo.py";
    let bar = "tests_requiring_config/bar.py";
    interaction.server.did_open(foo);
    interaction.server.did_open(bar);

    let foo_path = root.path().join(foo);

    // Send will_rename_files request to rename bar.py to baz.py
    interaction
        .server
        .will_rename_files(bar, "tests_requiring_config/baz.py");

    // Expect a response with edits to update imports in foo.py using "changes" format
    interaction.client.expect_response(Response {
        id: RequestId::from(2),
        result: Some(serde_json::json!({
            "changes": {
                Url::from_file_path(&foo_path).unwrap().to_string(): [
                    {
                        "newText": "baz",
                        "range": {
                            "start": {"line": 5, "character": 7},
                            "end": {"line": 5, "character": 10}
                        }
                    },
                    {
                        "newText": "baz",
                        "range": {
                            "start": {"line": 6, "character": 5},
                            "end": {"line": 6, "character": 8}
                        }
                    }
                ]
            }
        })),
        error: None,
    });

    interaction.shutdown();
}

#[test]
fn test_will_rename_files_with_marker_file_no_config() {
    let root = get_test_files_root();
    let mut interaction = LspInteraction::new_with_indexing_mode(IndexingMode::LazyBlocking);
    let root_path = root.path().join("marker_file_no_config");
    let scope_uri = Url::from_file_path(&root_path).unwrap();

    interaction.set_root(root_path.clone());
    interaction.initialize(InitializeSettings {
        workspace_folders: Some(vec![("test".to_owned(), scope_uri)]),
        ..Default::default()
    });

    let bar = "bar.py";
    let foo = "foo.py";
    interaction.server.did_open(bar);
    interaction.server.did_open(foo);

    let foo_path = root_path.join(foo);

    // Send will_rename_files request to rename bar.py to baz.py
    interaction.server.will_rename_files(bar, "baz.py");

    // Expect a response with edits to update imports in foo.py using "changes" format
    // since  there's a marker file (pyproject.toml), but no pyrefly config,
    // it should still work and provide rename edits
    interaction.client.expect_response(Response {
        id: RequestId::from(2),
        result: Some(serde_json::json!({
            "changes": {
                Url::from_file_path(&foo_path).unwrap().to_string(): [
                    {
                        "newText": "baz",
                        "range": {
                            "start": {"line": 5, "character": 7},
                            "end": {"line": 5, "character": 10}
                        }
                    },
                    {
                        "newText": "baz",
                        "range": {
                            "start": {"line": 6, "character": 5},
                            "end": {"line": 6, "character": 8}
                        }
                    },
                ]
            }
        })),
        error: None,
    });

    interaction.shutdown();
}

#[test]
fn test_will_rename_files_changes_folder() {
    let root = get_test_files_root();
    let mut interaction = LspInteraction::new_with_indexing_mode(IndexingMode::None);
    interaction.set_root(root.path().to_path_buf());
    interaction.initialize(InitializeSettings::default());

    let bar = "tests_requiring_config/bar.py";
    let foo = "tests_requiring_config/foo.py";
    interaction.server.did_open(bar);
    interaction.server.did_open(foo);

    let foo_path = root.path().join(foo);

    // Send will_rename_files request to rename bar.py to subfolder/bar.py
    interaction
        .server
        .will_rename_files(bar, "tests_requiring_config/subfolder/bar.py");

    // Expect a response with edits to update imports in foo.py using "changes" format
    interaction.client.expect_response(Response {
        id: RequestId::from(2),
        result: Some(serde_json::json!({
            "changes": {
                Url::from_file_path(&foo_path).unwrap().to_string(): [
                    {
                        "newText": "subfolder.bar",
                        "range": {
                            "start": {"line": 5, "character": 7},
                            "end": {"line": 5, "character": 10}
                        }
                    },
                    {
                        "newText": "subfolder.bar",
                        "range": {
                            "start": {"line": 6, "character": 5},
                            "end": {"line": 6, "character": 8}
                        }
                    }
                ]
            }
        })),
        error: None,
    });

    interaction.shutdown();
}

#[test]
fn test_will_rename_files_changes_nothing_when_no_files_open() {
    let root = get_test_files_root();
    let mut interaction = LspInteraction::new_with_indexing_mode(IndexingMode::LazyBlocking);
    interaction.set_root(root.path().to_path_buf());
    interaction.initialize(InitializeSettings::default());

    interaction.server.will_rename_files(
        "tests_requiring_config/bar.py",
        "tests_requiring_config/baz.py",
    );

    // Expect a response with no edits since indexing only happens once a file in a config is open
    interaction.client.expect_response(Response {
        id: RequestId::from(2),
        result: Some(serde_json::json!(null)),
        error: None,
    });

    interaction.shutdown();
}

#[test]
fn test_will_rename_files_changes_everything_when_indexed() {
    let root = get_test_files_root();
    let mut interaction = LspInteraction::new_with_indexing_mode(IndexingMode::LazyBlocking);
    interaction.set_root(root.path().to_path_buf());
    interaction.initialize(InitializeSettings::default());

    let bar = "tests_requiring_config/bar.py";
    interaction.server.did_open(bar);

    let foo_path = root.path().join("tests_requiring_config/foo.py");
    let with_synthetic_bindings_path = root
        .path()
        .join("tests_requiring_config/with_synthetic_bindings.py");
    let various_imports_path = root
        .path()
        .join("tests_requiring_config/various_imports.py");

    // Send will_rename_files request to rename bar.py to baz.py
    interaction
        .server
        .will_rename_files(bar, "tests_requiring_config/baz.py");

    // Expect a response with edits to update imports in foo.py, with_synthetic_bindings.py, and various_imports.py using "changes" format
    interaction.client.expect_response(Response {
        id: RequestId::from(2),
        result: Some(serde_json::json!({
            "changes": {
                Url::from_file_path(&foo_path).unwrap().to_string(): [
                    {
                        "newText": "baz",
                        "range": {
                            "start": {"line": 5, "character": 7},
                            "end": {"line": 5, "character": 10}
                        }
                    },
                    {
                        "newText": "baz",
                        "range": {
                            "start": {"line": 6, "character": 5},
                            "end": {"line": 6, "character": 8}
                        }
                    }
                ],
                Url::from_file_path(&various_imports_path).unwrap().to_string(): [
                    {
                        "newText": "baz",
                        "range": {
                            "start": {"line": 5, "character": 5},
                            "end": {"line": 5, "character": 8}
                        }
                    }
                ],
                Url::from_file_path(&with_synthetic_bindings_path).unwrap().to_string(): [
                    {
                        "newText": "baz",
                        "range": {
                            "start": {"line": 5, "character": 5},
                            "end": {"line": 5, "character": 8}
                        }
                    }
                ]
            }
        })),
        error: None,
    });

    interaction.shutdown();
}

#[test]
fn test_will_rename_files_without_config() {
    let root = get_test_files_root();
    let mut interaction = LspInteraction::new_with_indexing_mode(IndexingMode::None);
    interaction.set_root(root.path().to_path_buf());
    interaction.initialize(InitializeSettings::default());

    let foo = "foo.py";
    let bar = "bar.py";
    interaction.server.did_open(foo);
    interaction.server.did_open(bar);

    // Send will_rename_files request to rename bar.py to baz.py
    interaction.server.will_rename_files(bar, "baz.py");

    // Expect a response with edits to update imports in foo.py using "changes" format
    interaction.client.expect_response(Response {
        id: RequestId::from(2),
        result: Some(serde_json::json!(null)),
        error: None,
    });

    interaction.shutdown();
}

#[test]
fn test_will_rename_files_without_config_with_workspace_folder() {
    let root = get_test_files_root();
    let mut interaction = LspInteraction::new_with_indexing_mode(IndexingMode::None);
    let root_path = root.path();
    let scope_uri = Url::from_file_path(root_path).unwrap();

    interaction.set_root(root_path.to_path_buf());
    interaction.initialize(InitializeSettings {
        workspace_folders: Some(vec![("test".to_owned(), scope_uri)]),
        ..Default::default()
    });

    let foo = "foo.py";
    let bar = "bar.py";
    interaction.server.did_open(foo);

    // Send will_rename_files request to rename bar.py to baz.py
    interaction.server.will_rename_files(bar, "baz.py");

    // Expect a response with edits to update imports in foo.py using "changes" format
    interaction.client.expect_response(Response {
        id: RequestId::from(2),
        result: Some(serde_json::json!(null)),
        error: None,
    });

    interaction.shutdown();
}

#[test]
fn test_will_rename_files_document_changes() {
    let root = get_test_files_root();
    let mut interaction = LspInteraction::new_with_indexing_mode(IndexingMode::LazyBlocking);
    interaction.set_root(root.path().to_path_buf());

    let settings = InitializeSettings {
        capabilities: Some(serde_json::json!({
            "workspace": {
                "workspaceEdit": {
                    "documentChanges": true
                }
            }
        })),
        ..Default::default()
    };
    interaction.initialize(settings);

    let bar: &'static str = "tests_requiring_config/bar.py";
    interaction.server.did_open(bar);

    let foo_path = root.path().join("tests_requiring_config/foo.py");
    let with_synthetic_bindings_path = root
        .path()
        .join("tests_requiring_config/with_synthetic_bindings.py");
    let various_imports_path = root
        .path()
        .join("tests_requiring_config/various_imports.py");

    // Send will_rename_files request to rename bar.py to baz.py
    interaction
        .server
        .will_rename_files(bar, "tests_requiring_config/baz.py");

    // Expect a response with edits to update imports in foo.py, various_imports.py, and with_synthetic_bindings.py using "documentChanges" format
    // Files are returned in alphabetical order by URI
    interaction.client.expect_response(Response {
        id: RequestId::from(2),
        result: Some(serde_json::json!({
            "documentChanges": [
                {
                    "textDocument": {
                        "uri": Url::from_file_path(&foo_path).unwrap().to_string(),
                        "version": null
                    },
                    "edits": [
                        {
                            "newText": "baz",
                            "range": {
                                "start": {"line": 5, "character": 7},
                                "end": {"line": 5, "character": 10}
                            }
                        },
                        {
                            "newText": "baz",
                            "range": {
                                "start": {"line": 6, "character": 5},
                                "end": {"line": 6, "character": 8}
                            }
                        }
                    ]
                },
                {
                    "textDocument": {
                        "uri": Url::from_file_path(&various_imports_path).unwrap().to_string(),
                        "version": null
                    },
                    "edits": [
                        {
                            "newText": "baz",
                            "range": {
                                "start": {"line": 5, "character": 5},
                                "end": {"line": 5, "character": 8}
                            }
                        }
                    ]
                },
                {
                    "textDocument": {
                        "uri": Url::from_file_path(&with_synthetic_bindings_path).unwrap().to_string(),
                        "version": null
                    },
                    "edits": [
                        {
                            "newText": "baz",
                            "range": {
                                "start": {"line": 5, "character": 5},
                                "end": {"line": 5, "character": 8}
                            }
                        }
                    ]
                }
            ]
        })),
        error: None,
    });

    interaction.shutdown();
}
