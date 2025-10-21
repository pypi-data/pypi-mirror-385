/*
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

use crate::testcase;

testcase!(
    test_double_name_match,
    r#"
match 42:
    case x:  # E: name capture `x` makes remaining patterns unreachable
        pass
    case y:
        pass
print(y)  # E: `y` may be uninitialized
    "#,
);

testcase!(
    test_guard_narrowing_in_match,
    r#"
from typing import assert_type
def test(x: int | bytes | str):
    match x:
        case int():
            assert_type(x, int)
        case _ if isinstance(x, str):
            assert_type(x, str)
    "#,
);

testcase!(
    test_pattern_crash,
    r#"
# Used to crash, see https://github.com/facebook/pyrefly/issues/490
match None:
    case {a: 1}: # E: # E: # E:
        pass
"#,
);

testcase!(
    test_pattern_dict_key_enum,
    r#"
from enum import StrEnum

class MyEnumType(StrEnum):
    A = "a"
    B = "b"

def my_func(x: dict[MyEnumType, int]) -> int:
    match x:
        case {MyEnumType.A: a, MyEnumType.B: b}:
            return a + b
        case _:
            return 0
"#,
);

testcase!(
    test_non_exhaustive_flow_merging,
    r#"
from typing import assert_type, Literal
def foo(x: Literal['A'] | Literal['B']):
    match x:
        case 'A':
            raise ValueError()
    assert_type(x, Literal['B'])
    "#,
);

testcase!(
    test_negation_of_guarded_pattern,
    r#"
from typing import assert_type, Literal
def condition() -> bool: ...
def foo(x: Literal['A'] | Literal['B']):
    match x:
        case 'A' if condition():
            raise ValueError()
    assert_type(x, Literal['A', 'B'])
    "#,
);

testcase!(
    bug = "We currently never negate class matches; ideally we would be smarter about when the match is exhaustive",
    test_negated_exhaustive_class_match,
    r#"
from typing import assert_type

def f0(x: int | str):
    match x:
        case int():
            pass
        case _:
            assert_type(x, str)  # E: assert_type(int | str, str)
"#,
);
