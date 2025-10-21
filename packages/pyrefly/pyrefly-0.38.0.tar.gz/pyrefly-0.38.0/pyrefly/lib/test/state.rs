/*
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

//! Tests of the `State` object.

use std::path::PathBuf;
use std::sync::Arc;
use std::thread::sleep;
use std::time::Duration;

use dupe::Dupe;
use pyrefly_build::handle::Handle;
use pyrefly_build::source_db::map_db::MapDatabase;
use pyrefly_python::module_name::ModuleName;
use pyrefly_python::module_path::ModulePath;
use pyrefly_python::sys_info::PythonPlatform;
use pyrefly_python::sys_info::PythonVersion;
use pyrefly_python::sys_info::SysInfo;
use pyrefly_util::arc_id::ArcId;
use pyrefly_util::lock::Mutex;
use pyrefly_util::prelude::SliceExt;

use crate::config::config::ConfigFile;
use crate::config::finder::ConfigFinder;
use crate::error::error::print_errors;
use crate::module::finder::find_import;
use crate::state::require::Require;
use crate::state::state::State;
use crate::test::util::TestEnv;

#[test]
fn test_multiple_config() {
    let linux = SysInfo::new(PythonVersion::default(), PythonPlatform::linux());
    let windows = SysInfo::new(PythonVersion::default(), PythonPlatform::windows());

    const LIB: &str = r#"
import sys
if sys.platform == "linux":
    value = 42
else:
    value = "hello"
"#;
    let mut test_env = TestEnv::new();
    test_env.add("lib", LIB);
    test_env.add("windows", "import lib; x: str = lib.value");
    test_env.add("linux", "import lib; x: int = lib.value");
    test_env.add(
        "main",
        "import lib; x: str = lib.value  # E: `Literal[42]` is not assignable to `str`",
    );
    let config_file = test_env.config();
    let state = State::new(test_env.config_finder());

    let f = |name: &str, sys_info: &SysInfo| {
        let name = ModuleName::from_str(name);
        let path = find_import(&config_file, name, None).unwrap();
        Handle::new(name, path, sys_info.dupe())
    };

    let handles = [
        f("linux", &linux),
        f("windows", &windows),
        f("main", &linux),
    ];
    let mut transaction = state.new_transaction(Require::Exports, None);
    transaction.set_memory(test_env.get_memory());
    transaction.run(&handles, Require::Everything);
    transaction
        .get_errors(&handles)
        .check_against_expectations()
        .unwrap();
}

#[test]
fn test_multiple_path() {
    const LIB_PYI: &str = "x: int";
    const LIB_PY: &str = "x: str = 1  # E: `Literal[1]` is not assignable to `str`";
    const MAIN_PYI: &str =
        "import lib; y: list[int] = lib.x  # E: `int` is not assignable to `list[int]`";
    const MAIN_PY: &str =
        "import lib; y: list[str] = lib.x  # E: `int` is not assignable to `list[str]`";

    const FILES: &[(&str, &str, &str)] = &[
        ("lib", "lib.pyi", LIB_PYI),
        ("lib", "lib.py", LIB_PY),
        ("main", "main.pyi", MAIN_PYI),
        ("main", "main.py", MAIN_PY),
    ];

    let mut config = ConfigFile::default();
    config.python_environment.set_empty_to_default();
    let sys_info = config.get_sys_info();
    let mut sourcedb = MapDatabase::new(sys_info.dupe());
    for (name, path, _) in FILES.iter().rev() {
        sourcedb.insert(
            ModuleName::from_str(name),
            ModulePath::memory(PathBuf::from(path)),
        );
    }
    config.source_db = Some(Arc::new(Box::new(sourcedb)));
    config.configure();
    let config = ArcId::new(config);

    let state = State::new(ConfigFinder::new_constant(config.clone()));
    let handles = config.source_db.as_ref().unwrap().modules_to_check();
    let mut transaction = state.new_transaction(Require::Exports, None);
    transaction.set_memory(
        FILES.map(|(_, path, contents)| {
            (PathBuf::from(path), Some(Arc::new((*contents).to_owned())))
        }),
    );
    transaction.run(&handles, Require::Everything);
    let loads = transaction.get_errors(handles.iter());
    let project_root = PathBuf::new();
    print_errors(project_root.as_path(), &loads.collect_errors().shown);
    loads.check_against_expectations().unwrap();
    assert_eq!(loads.collect_errors().shown.len(), 3);
}

#[test]
fn test_change_require() {
    let env = TestEnv::one("foo", "x: str = 1\ny: int = 'x'");
    let state = State::new(env.config_finder());
    let handle = Handle::new(
        ModuleName::from_str("foo"),
        ModulePath::memory(PathBuf::from("foo.py")),
        env.sys_info(),
    );

    let mut t = state.new_committable_transaction(Require::Exports, None);
    t.as_mut().set_memory(env.get_memory());
    t.as_mut().run(&[handle.dupe()], Require::Exports);
    state.commit_transaction(t);

    assert_eq!(
        state
            .transaction()
            .get_errors([&handle])
            .collect_errors()
            .shown
            .len(),
        0
    );
    assert!(state.transaction().get_bindings(&handle).is_none());
    state.run(&[handle.dupe()], Require::Errors, Require::Exports, None);
    assert_eq!(
        state
            .transaction()
            .get_errors([&handle])
            .collect_errors()
            .shown
            .len(),
        2
    );
    assert!(state.transaction().get_bindings(&handle).is_none());
    state.run(
        &[handle.dupe()],
        Require::Everything,
        Require::Exports,
        None,
    );
    assert_eq!(
        state
            .transaction()
            .get_errors([&handle])
            .collect_errors()
            .shown
            .len(),
        2
    );
    assert!(state.transaction().get_bindings(&handle).is_some());
}

#[test]
fn test_crash_on_search() {
    const REQUIRE: Require = Require::Everything; // Doesn't matter for the test

    let mut t = TestEnv::new();
    t.add("foo", "x = 1");
    let (state, _) = t.to_state();

    // Now we dirty the module `foo`
    let mut t = state.new_committable_transaction(REQUIRE, None);
    t.as_mut().set_memory(vec![(
        PathBuf::from("foo.py"),
        Some(Arc::new("x = 3".to_owned())),
    )]);
    t.as_mut().run(&[], Require::Everything); // This run breaks reproduction (but is now required)
    state.commit_transaction(t);

    // Now we need to increment the step counter.
    let mut t = state.new_committable_transaction(REQUIRE, None);
    t.as_mut().run(&[], Require::Everything);
    state.commit_transaction(t);

    // Now we run two searches, this used to crash
    let t = state.new_transaction(REQUIRE, None);
    eprintln!("First search");
    t.search_exports_exact("x");
    eprintln!("Second search");
    t.search_exports_exact("x");
}

const SEQUENTIAL_COMMITTABLE_TRANSACTIONS_SLEEP_TIME_MS: u64 = 100;

#[test]
fn test_sequential_committable_transactions() {
    let mut t = TestEnv::new();
    t.add("foo", "x = 1");
    let (state, _) = t.to_state();
    let state = Arc::new(state);
    let state1 = state.dupe();
    let state2 = state.dupe();
    let state3 = state.dupe();
    let state4 = state.dupe();
    let state5 = state.dupe();
    let counter = Arc::new(Mutex::new(0));
    let counter1 = counter.dupe();
    let counter2 = counter.dupe();
    let counter3 = counter.dupe();
    let counter4 = counter.dupe();
    let counter5 = counter.dupe();

    /// This function is called in many separate threads.
    /// We want to make sure that state only allow one committable transaction at a time.
    /// We will indirectly verify this by having each thread increment a shared counter twice
    /// during the transaction. Due to the exclusivity of the transaction, we should never be able
    /// to observe that the counter has an odd value.
    fn do_work_and_verify(state: Arc<State>, counter: Arc<Mutex<usize>>) {
        let t = state.new_committable_transaction(Require::Exports, None);
        let initial_value = {
            let mut lock = counter.lock();
            let v = *lock;
            assert!(v.is_multiple_of(2));
            *lock += 1;
            v
        };
        sleep(Duration::from_millis(
            SEQUENTIAL_COMMITTABLE_TRANSACTIONS_SLEEP_TIME_MS,
        ));
        {
            let mut lock = counter.lock();
            let v = *lock;
            *lock += 1;
            assert_eq!(initial_value + 1, v);
            v
        };
        state.commit_transaction(t);
    }

    // We rapidly spin up 5 threads, each of which will increment the counter twice.
    let t1 = std::thread::spawn(move || {
        do_work_and_verify(state1, counter1);
    });
    let t2 = std::thread::spawn(move || {
        do_work_and_verify(state2, counter2);
    });
    let t3 = std::thread::spawn(move || {
        do_work_and_verify(state3, counter3);
    });
    let t4 = std::thread::spawn(move || {
        do_work_and_verify(state4, counter4);
    });
    let t5 = std::thread::spawn(move || {
        do_work_and_verify(state5, counter5);
    });

    t1.join().unwrap();
    t2.join().unwrap();
    t3.join().unwrap();
    t4.join().unwrap();
    t5.join().unwrap();

    // When we are here, we are sure that there is no deadlock.
    let lock = counter.lock();
    assert_eq!(10, *lock);
}
