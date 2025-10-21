/*
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

use std::sync::Arc;

use pyrefly_build::handle::Handle;
use pyrefly_python::module::Module;
use ruff_python_ast::ModModule;

use crate::alt::answers::Answers;
use crate::binding::bindings::Bindings;
use crate::report::pysa::module::ModuleId;
use crate::report::pysa::module::ModuleIds;
use crate::report::pysa::module::ModuleKey;
use crate::state::state::Transaction;
use crate::types::stdlib::Stdlib;

/// Pyrefly information about a module.
pub struct ModuleContext<'a> {
    pub handle: Handle,
    pub transaction: &'a Transaction<'a>,
    pub bindings: Bindings,
    pub answers: Arc<Answers>,
    pub stdlib: Arc<Stdlib>,
    pub ast: Arc<ModModule>,
    pub module_info: Module,
    pub module_id: ModuleId,
    pub module_ids: &'a ModuleIds,
}

impl ModuleContext<'_> {
    pub fn create<'a>(
        handle: Handle,
        transaction: &'a Transaction<'a>,
        module_ids: &'a ModuleIds,
    ) -> Option<ModuleContext<'a>> {
        let bindings = transaction.get_bindings(&handle)?;
        let answers = transaction.get_answers(&handle)?;
        let stdlib = transaction.get_stdlib(&handle);
        let ast = transaction.get_ast(&handle)?;
        let module_info = transaction.get_module_info(&handle)?;
        let module_id = module_ids.get(ModuleKey::from_handle(&handle))?;
        Some(ModuleContext {
            transaction,
            bindings,
            answers,
            stdlib,
            ast,
            module_info,
            module_id,
            module_ids,
            handle,
        })
    }
}
