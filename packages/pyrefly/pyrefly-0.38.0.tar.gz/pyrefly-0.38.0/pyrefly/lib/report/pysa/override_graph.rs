/*
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

use std::collections::HashMap;
use std::collections::HashSet;

use pyrefly_build::handle::Handle;
use pyrefly_types::class::Class;
use pyrefly_util::thread_pool::ThreadPool;
use rayon::prelude::*;
use ruff_python_ast::name::Name;

use crate::alt::types::decorated_function::DecoratedFunction;
use crate::binding::binding::Binding;
use crate::binding::binding::ClassFieldDefinition;
use crate::binding::binding::KeyDecoratedFunction;
use crate::graph::index::Idx;
use crate::report::pysa::class::ClassRef;
use crate::report::pysa::class::get_class_field_declaration;
use crate::report::pysa::class::get_context_from_class;
use crate::report::pysa::context::ModuleContext;
use crate::report::pysa::function::FunctionBaseDefinition;
use crate::report::pysa::function::FunctionRef;
use crate::report::pysa::function::WholeProgramFunctionDefinitions;
use crate::report::pysa::function::get_all_functions;
use crate::report::pysa::module::ModuleIds;
use crate::report::pysa::slow_fun_monitor::slow_fun_monitor_scope;
use crate::report::pysa::step_logger::StepLogger;
use crate::state::state::Transaction;

/// A map from a (base) method to classes that directly override it
#[derive(Debug)]
pub(crate) struct OverrideGraph {
    edges: HashMap<FunctionRef, HashSet<ClassRef>>,
}

pub struct ModuleReversedOverrideGraph(HashMap<FunctionRef, FunctionRef>);

pub struct WholeProgramReversedOverrideGraph(dashmap::ReadOnlyView<FunctionRef, FunctionRef>);

impl OverrideGraph {
    pub fn new() -> Self {
        OverrideGraph {
            edges: HashMap::new(),
        }
    }

    fn add_edge(&mut self, base_method: FunctionRef, overriding_class: ClassRef) {
        self.edges
            .entry(base_method)
            .or_default()
            .insert(overriding_class);
    }

    pub fn from_reversed(
        reversed_override_graph: &WholeProgramReversedOverrideGraph,
        function_base_definitions: &WholeProgramFunctionDefinitions<FunctionBaseDefinition>,
    ) -> Self {
        let step = StepLogger::start("Building override graph", "Built override graph");

        let mut graph = OverrideGraph::new();
        for (overriding_method, base_method) in reversed_override_graph.0.iter() {
            let overriding_class = function_base_definitions
                .get(overriding_method.module_id, &overriding_method.function_id)
                .and_then(|definition| definition.defining_class.clone())
                .unwrap();
            graph.add_edge(base_method.clone(), overriding_class);
        }

        step.finish();
        graph
    }

    pub fn overrides_exist(&self, method: &FunctionRef) -> bool {
        self.edges.contains_key(method)
    }

    pub fn get_overriding_classes(&self, method: &FunctionRef) -> Option<&HashSet<ClassRef>> {
        self.edges.get(method)
    }
}

impl WholeProgramReversedOverrideGraph {
    #[cfg(test)]
    pub fn new() -> WholeProgramReversedOverrideGraph {
        WholeProgramReversedOverrideGraph(dashmap::DashMap::new().into_read_only())
    }

    pub fn get<'a>(&'a self, method: &FunctionRef) -> Option<&'a FunctionRef> {
        self.0.get(method)
    }
}

// Requires `context` to be the module context of the decorated function.
pub fn get_last_definition(
    key_decorated_function: Idx<KeyDecoratedFunction>,
    context: &ModuleContext,
) -> DecoratedFunction {
    // Follow the successor chain to find the last function
    let mut last_decorated_function = key_decorated_function;
    loop {
        let successor = context.bindings.get(last_decorated_function).successor;
        if let Some(successor) = successor {
            last_decorated_function = successor;
        } else {
            break;
        }
    }
    DecoratedFunction::from_bindings_answers(
        last_decorated_function,
        &context.bindings,
        &context.answers,
    )
}

fn get_super_class_member(
    class: &Class,
    field: &Name,
    context: &ModuleContext,
) -> Option<FunctionRef> {
    assert_eq!(class.module(), &context.module_info);
    let super_class_member = context
        .transaction
        .ad_hoc_solve(&context.handle, |solver| {
            solver.get_super_class_member(class, None, field)
        })
        .flatten()?;

    // Important: we need to use the module context of the class.
    let context = get_context_from_class(&super_class_member.defining_class, context);

    // TODO(T225700656): handle class fields.
    get_class_field_declaration(&super_class_member.defining_class, field, &context)
        .and_then(|binding_class_field| {
            if let ClassFieldDefinition::MethodLike { definition, .. } =
                binding_class_field.definition
            {
                let binding = context.bindings.get(definition);
                if let Binding::Function(key_decorated_function, _pred, _class_meta) = binding {
                    Some(*key_decorated_function)
                } else {
                    None
                }
            } else {
                None
            }
        })
        .map(|key_decorated_function| {
            let last_function = get_last_definition(key_decorated_function, &context);
            FunctionRef::from_decorated_function(&last_function, &context)
        })
}

pub fn create_reversed_override_graph_for_module(
    context: &ModuleContext,
) -> ModuleReversedOverrideGraph {
    let mut graph = ModuleReversedOverrideGraph(HashMap::new());
    for function in get_all_functions(context) {
        if !function.should_export(context) {
            continue;
        }
        let name = function.name();
        let overridden_base_method = function
            .defining_cls()
            .and_then(|class| get_super_class_member(class, &name, context));
        match overridden_base_method {
            Some(overridden_base_method) => {
                let current_function = function.as_function_ref(context);
                assert!(
                    graph
                        .0
                        .insert(current_function, overridden_base_method)
                        .is_none(),
                    "Found function definitions with the same location"
                );
            }
            _ => (),
        }
    }

    graph
}

pub fn build_reversed_override_graph(
    handles: &Vec<Handle>,
    transaction: &Transaction,
    module_ids: &ModuleIds,
) -> WholeProgramReversedOverrideGraph {
    let step = StepLogger::start(
        "Building reverse override graph",
        "Built reverse override graph",
    );

    let reversed_override_graph = dashmap::DashMap::new();

    ThreadPool::new().install(|| {
        slow_fun_monitor_scope(|slow_function_monitor| {
            handles.par_iter().for_each(|handle| {
                let context =
                    ModuleContext::create(handle.clone(), transaction, module_ids).unwrap();
                slow_function_monitor.monitor_function(
                    || {
                        for (key, value) in create_reversed_override_graph_for_module(&context).0 {
                            reversed_override_graph.insert(key, value);
                        }
                    },
                    format!(
                        "Building reverse override graph for `{}`",
                        handle.module().as_str(),
                    ),
                    /* max_time_in_seconds */ 4,
                );
            });
        })
    });

    step.finish();
    WholeProgramReversedOverrideGraph(reversed_override_graph.into_read_only())
}
