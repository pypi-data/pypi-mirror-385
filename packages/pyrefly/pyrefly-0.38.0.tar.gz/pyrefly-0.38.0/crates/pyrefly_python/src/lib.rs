/*
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

#![warn(clippy::all)]
#![allow(clippy::match_like_matches_macro)]
#![allow(clippy::needless_lifetimes)]
#![allow(clippy::should_implement_trait)]
#![deny(clippy::cloned_instead_of_copied)]
#![deny(clippy::derive_partial_eq_without_eq)]
#![deny(clippy::inefficient_to_string)]
#![deny(clippy::mem_replace_option_with_some)]
#![deny(clippy::str_to_string)]
#![deny(clippy::string_to_string)]
#![deny(clippy::trivially_copy_pass_by_ref)]
#![feature(if_let_guard)]

pub mod ast;
pub mod display;
pub mod docstring;
pub mod dunder;
pub mod ignore;
pub mod keywords;
pub mod module;
pub mod module_name;
pub mod module_path;
pub mod nesting_context;
pub mod qname;
pub mod short_identifier;
pub mod symbol_kind;
pub mod sys_info;

/// Suffixes of python files that we can be processed.
pub const PYTHON_EXTENSIONS: &[&str] = &["py", "pyi"];

/// Suffixes of compiled python modules
pub const COMPILED_FILE_SUFFIXES: &[&str] = &["pyc", "pyx", "pyd"];
