/*
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

use std::sync::Arc;

use dupe::Dupe;
use pyrefly_build::handle::Handle;

use crate::alt::types::class_metadata::ClassMro;
use crate::binding::binding::KeyClassMro;
use crate::state::state::State;
use crate::test::util::get_class;
use crate::test::util::mk_state;
use crate::testcase;

pub fn get_class_mro(name: &str, handle: &Handle, state: &State) -> Arc<ClassMro> {
    let solutions = state.transaction().get_solutions(handle).unwrap();

    let cls = get_class(name, handle, state);
    solutions.get(&KeyClassMro(cls.index())).dupe()
}

fn get_mro_names(name: &str, handle: &Handle, state: &State) -> Vec<String> {
    get_class_mro(name, handle, state)
        .ancestors_no_object()
        .iter()
        .map(|cls| cls.name().as_str().to_owned())
        .collect()
}

fn assert_no_errors(handle: &Handle, state: &State) {
    assert_eq!(
        state
            .transaction()
            .get_errors([handle])
            .collect_errors()
            .shown
            .len(),
        0,
        "Expected no errors"
    );
}

fn assert_has_error(handle: &Handle, state: &State, error_msg: &str, assertion_msg: &str) {
    state
        .transaction()
        .get_errors([handle])
        .collect_errors()
        .shown
        .iter()
        .find(|e| e.msg().contains(error_msg))
        .unwrap_or_else(|| panic!("{assertion_msg}"));
}

#[test]
fn test_mro_simple_chain() {
    let (handle, driver) = mk_state(
        r#"
class A: pass
class B(A): pass
class C(B): pass
"#,
    );
    let mro_a = get_mro_names("A", &handle, &driver);
    assert_eq!(mro_a.len(), 0);
    let mro_b = get_mro_names("B", &handle, &driver);
    assert_eq!(mro_b, vec!["A"]);
    let mro_c = get_mro_names("C", &handle, &driver);
    assert_eq!(mro_c, vec!["B", "A"]);
}

#[test]
fn test_mro_triangle() {
    let (handle, driver) = mk_state(
        r#"
class A: pass
class B(A): pass
class C(B, A): pass
"#,
    );
    assert_no_errors(&handle, &driver);
    let mro_a = get_mro_names("A", &handle, &driver);
    assert_eq!(mro_a.len(), 0);
    let mro_b = get_mro_names("B", &handle, &driver);
    assert_eq!(mro_b, vec!["A"]);
    let mro_c = get_mro_names("C", &handle, &driver);
    assert_eq!(mro_c, vec!["B", "A"]);
}

#[test]
fn test_mro_butterfly() {
    let (handle, driver) = mk_state(
        r#"
class A: pass
class B: pass
class C(A, B): pass
class D(B, A): pass
"#,
    );
    assert_no_errors(&handle, &driver);
    let mro_a = get_mro_names("A", &handle, &driver);
    assert_eq!(mro_a.len(), 0);
    let mro_b = get_mro_names("B", &handle, &driver);
    assert_eq!(mro_b.len(), 0);
    let mro_c = get_mro_names("C", &handle, &driver);
    assert_eq!(mro_c, vec!["A", "B"]);
    let mro_d = get_mro_names("D", &handle, &driver);
    assert_eq!(mro_d, vec!["B", "A"]);
}

// Test matching the example in
// https://en.wikipedia.org/wiki/C3_linearization
// This is a convenient test since the article walks through algorithm execution in detail.
#[test]
fn test_mro_wikipedia_example() {
    let (handle, driver) = mk_state(
        r#"
class O: pass
class A(O): pass
class B(O): pass
class C(O): pass
class D(O): pass
class E(O): pass
class K1(C, A, B): pass
class K3(A, D): pass
class K2(B, D, E): pass
class Z(K1, K3, K2): pass
"#,
    );
    assert_no_errors(&handle, &driver);
    // O has no ancestors
    let mro_o = get_mro_names("O", &handle, &driver);
    assert_eq!(mro_o.len(), 0);
    // A - E all have O as their only ancestor. Just check A and E for conciseness.
    let mro_a = get_mro_names("A", &handle, &driver);
    assert_eq!(mro_a, vec!["O"]);
    let mro_e = get_mro_names("E", &handle, &driver);
    assert_eq!(mro_e, vec!["O"]);
    // K1 - K3 have more complex MROs, check each.
    let mro_k1 = get_mro_names("K1", &handle, &driver);
    assert_eq!(mro_k1, vec!["C", "A", "B", "O"]);
    let mro_k2 = get_mro_names("K2", &handle, &driver);
    assert_eq!(mro_k2, vec!["B", "D", "E", "O"]);
    let mro_k3 = get_mro_names("K3", &handle, &driver);
    assert_eq!(mro_k3, vec!["A", "D", "O"]);
    // Finally, check Z
    let mro_z = get_mro_names("Z", &handle, &driver);
    assert_eq!(mro_z, vec!["K1", "C", "K3", "A", "K2", "B", "D", "E", "O"]);
}

#[test]
fn test_mro_nonlinearizable_simple() {
    let (handle, driver) = mk_state(
        r#"
class A: pass
class B(A): pass
class C(A, B): pass  # linearization fails here
class D(C): pass  # we will still record the MRO up until a linearization failure
"#,
    );
    // We give up on computing the ancestors of C and record an error.
    assert_has_error(
        &handle,
        &driver,
        "Class `C` has a nonlinearizable inheritance chain detected at `A`",
        "No error for nonlinearizable inheritance chain",
    );
    let mro_c = get_mro_names("C", &handle, &driver);
    assert_eq!(mro_c.len(), 0);
    let mro_d = get_mro_names("D", &handle, &driver);
    assert_eq!(mro_d, vec!["C"]);
}

#[test]
fn test_mro_cyclic() {
    let (handle, state) = mk_state(
        r#"
class A(C): pass
class B(A): pass
class C(B): pass
"#,
    );
    assert_has_error(
        &handle,
        &state,
        "Class `A` inheriting from `C` creates a cycle",
        "No error for cyclical inheritance chain at `A`",
    );
    assert_has_error(
        &handle,
        &state,
        "Class `B` inheriting from `A` creates a cycle",
        "No error for cyclical inheritance chain at `B`",
    );
    assert_has_error(
        &handle,
        &state,
        "Class `C` inheriting from `B` creates a cycle",
        "No error for cyclical inheritance chain at `C`",
    );
    // The current logic is essentially correct but has bad UX because we only actually
    // error where we detect the cycle, other classes silently produce an MRO right up
    // to the cycle (note that A even appears in the ancestors of A!).
    let mro_a = get_mro_names("A", &handle, &state);
    assert_eq!(mro_a.len(), 0);
    let mro_b = get_mro_names("B", &handle, &state);
    assert_eq!(mro_b.len(), 0);
    let mro_c = get_mro_names("C", &handle, &state);
    assert_eq!(mro_c.len(), 0);
}

#[test]
fn test_mro_generic_bound() {
    let (handle, driver) = mk_state(
        r#"
class A: pass
class Foo[T: A]: pass
class Bar(Foo['Baz']): pass
class Baz(Bar, A): pass
"#,
    );
    assert_no_errors(&handle, &driver);
    let mro_baz = get_mro_names("Baz", &handle, &driver);
    assert_eq!(mro_baz, vec!["Bar", "Foo", "A"]);
}

testcase!(
    test_class_is_object_instance,
    r#"
def f(x: object):
    pass
class A[T]:
    pass
f(A)
f(A[int])
    "#,
);
