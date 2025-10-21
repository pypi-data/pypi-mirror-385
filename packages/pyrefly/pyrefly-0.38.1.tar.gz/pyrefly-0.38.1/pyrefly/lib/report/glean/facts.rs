/*
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

use serde::Serialize;
use serde_json::Value;

/// Represents a Glean JSON file containing Python indexer data
#[derive(Debug, Clone, Serialize)]
pub struct Glean {
    /// The schema entries in the Glean file
    #[serde(skip_serializing_if = "Vec::is_empty", default)]
    pub entries: Vec<GleanEntry>,
}

/// Represents an entry in a Glean file, which can be either a schema ID or a predicate
#[derive(Debug, Clone, Serialize)]
#[serde(untagged)]
pub enum GleanEntry {
    /// Schema ID entry
    SchemaId { schema_id: String },
    /// Predicate entry containing facts
    Predicate {
        predicate: String,
        facts: Vec<Value>,
    },
}

pub fn json(x: impl Serialize) -> Value {
    serde_json::to_value(x).unwrap()
}
