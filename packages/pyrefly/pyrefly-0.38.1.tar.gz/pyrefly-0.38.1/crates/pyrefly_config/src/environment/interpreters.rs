/*
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

use std::fmt::Display;
use std::path::Path;
use std::path::PathBuf;
use std::sync::LazyLock;

use serde::Deserialize;
use serde::Serialize;
#[cfg(not(target_arch = "wasm32"))]
use which::which;

use crate::environment::active_environment::ActiveEnvironment;
use crate::environment::conda;
use crate::environment::venv;
use crate::util::ConfigOrigin;

#[derive(Debug, PartialEq, Eq, Deserialize, Serialize, Clone, Default)]
#[serde(rename_all = "kebab-case")]
pub struct Interpreters {
    #[serde(
                default,
                skip_serializing_if = "ConfigOrigin::should_skip_serializing_option",
                // TODO(connernilsen): DON'T COPY THIS TO NEW FIELDS. This is a temporary
                // alias while we migrate existing fields from snake case to kebab case.
                alias = "python_interpreter",
                alias = "python-interpreter",
            )]
    pub(crate) python_interpreter_path: Option<ConfigOrigin<PathBuf>>,

    /// Should we turn a generic command into a `python_interpreter` path?
    #[serde(default)]
    pub(crate) fallback_python_interpreter_name: Option<ConfigOrigin<String>>,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub(crate) conda_environment: Option<ConfigOrigin<String>>,

    /// Should we do any querying of an interpreter?
    #[serde(default, skip_serializing_if = "crate::util::skip_default_false")]
    pub skip_interpreter_query: bool,
}

impl Display for Interpreters {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self {
                skip_interpreter_query: true,
                ..
            } => write!(f, "<interpreter query skipped>"),
            Self {
                python_interpreter_path: None,
                ..
            } => write!(f, "<none found successfully>"),
            Self {
                conda_environment: Some(conda),
                python_interpreter_path: Some(path),
                ..
            } => write!(
                f,
                "conda environment {conda} with interpreter at {}",
                path.display()
            ),
            Self {
                fallback_python_interpreter_name: Some(cmd),
                python_interpreter_path: Some(path),
                ..
            } => write!(
                f,
                "interpreter at path {} (from `which {cmd}`)",
                path.display(),
            ),
            Self {
                python_interpreter_path: Some(path),
                ..
            } => write!(f, "{}", path.display()),
        }
    }
}

impl Interpreters {
    const DEFAULT_INTERPRETERS: &[&str] = &["python3", "python"];

    /// Checks if any interpreter is currently set, typically used when determining
    /// if the config or CLI overrides explicitly specified a config to figure out
    /// if we should respect an IDE-supplied interpreter preference.
    pub fn is_empty(&self) -> bool {
        self.python_interpreter_path.is_none()
            && self.conda_environment.is_none()
            && self.fallback_python_interpreter_name.is_none()
    }

    pub fn set_lsp_python_interpreter(&mut self, interpreter: PathBuf) {
        self.python_interpreter_path = Some(ConfigOrigin::lsp(interpreter));
    }

    /// Finds interpreters by searching in prioritized locations for the given project
    /// and interpreter settings.
    ///
    /// The priorities are:
    /// 1. Check for an overridden `--python-interpreter` or `--conda-environment`
    /// 2. Check for an IDE / LSP provided `python-interpreter`.
    /// 3. Check for an active venv or Conda environment
    /// 4. Check for a configured `python-interpreter`
    /// 5. Check for a configured `conda-environment`
    /// 6. Check for a `venv` in the current project
    /// 7. Use an interpreter we can find on the `$PATH`
    /// 8. Give up and return an error
    pub(crate) fn find_interpreter(
        &self,
        path: Option<&Path>,
    ) -> anyhow::Result<ConfigOrigin<PathBuf>> {
        let python_interpreter = self.interpreter_path_or_cmd()?;
        if let Some(interpreter @ ConfigOrigin::CommandLine(_)) = python_interpreter {
            return Ok(interpreter);
        }

        if let Some(interpreter @ ConfigOrigin::Lsp(_)) = python_interpreter {
            return Ok(interpreter);
        }

        if let Some(conda_env @ ConfigOrigin::CommandLine(_)) = &self.conda_environment {
            return conda_env
                .as_deref()
                .map(conda::find_interpreter_from_env)
                .transpose_err();
        }

        if let Some(active_env) = ActiveEnvironment::find() {
            return Ok(ConfigOrigin::auto(active_env));
        }

        if let Some(interpreter) = python_interpreter {
            return Ok(interpreter);
        }

        if let Some(conda_env) = &self.conda_environment {
            return conda_env
                .as_deref()
                .map(conda::find_interpreter_from_env)
                .transpose_err();
        }

        if let Some(start_path) = path
            && let Some(venv) = venv::find(start_path)
        {
            return Ok(ConfigOrigin::auto(venv));
        }

        if let Some(interpreter) = Self::get_default_interpreter() {
            return Ok(ConfigOrigin::auto(interpreter.to_path_buf()));
        }

        Err(anyhow::anyhow!(
            "Python environment (version, platform, or site-package-path) has value unset, \
                but no Python interpreter could be found to query for values. Falling back to \
                Pyrefly defaults for missing values."
        ))
    }

    fn interpreter_path_or_cmd(&self) -> anyhow::Result<Option<ConfigOrigin<PathBuf>>> {
        if self.python_interpreter_path.is_some() {
            return Ok(self.python_interpreter_path.clone());
        }
        #[cfg(not(target_arch = "wasm32"))]
        if let Some(cmd) = &self.fallback_python_interpreter_name {
            fn which_to_anyhow_err(cmd: &String) -> anyhow::Result<PathBuf> {
                Ok(which(cmd)?)
            }
            return Ok(Some(cmd.as_ref().map(which_to_anyhow_err).transpose_err()?));
        }
        Ok(self.python_interpreter_path.clone())
    }

    /// Get the first interpreter available on the path by using `which`
    /// and querying for [`Self::DEFAULT_INTERPRETERS`] in order.
    pub(crate) fn get_default_interpreter() -> Option<&'static Path> {
        static SYSTEM_INTERP: LazyLock<Option<PathBuf>> = LazyLock::new(|| {
            // disable query with `which` on wasm
            #[cfg(not(target_arch = "wasm32"))]
            for binary_name in Interpreters::DEFAULT_INTERPRETERS {
                use std::process::Command;

                let Ok(binary_path) = which(binary_name) else {
                    continue;
                };
                let mut check = Command::new(&binary_path);
                check.arg("--version");
                if let Ok(output) = check.output()
                    && output.status.success()
                {
                    return Some(binary_path);
                }
            }
            None
        });
        SYSTEM_INTERP.as_deref()
    }
}

#[cfg(test)]
mod test {
    use pyrefly_util::test_path::TestPath;
    use tempfile::TempDir;
    use tempfile::tempdir;

    use super::*;

    fn setup_test_dir() -> TempDir {
        let tempdir = tempdir().unwrap();
        let root = tempdir.path();
        let interpreter_suffix = if cfg!(windows) { ".exe" } else { "" };
        TestPath::setup_test_directory(
            root,
            vec![TestPath::dir(
                "venv",
                vec![
                    TestPath::file(&format!("python3{interpreter_suffix}")),
                    TestPath::file("pyvenv.cfg"),
                ],
            )],
        );
        tempdir
    }

    #[test]
    fn test_find_interpreter_precedence_python_interpreter_cli_highest_priority() {
        let tempdir = setup_test_dir();

        let python_interpreter = ConfigOrigin::cli(PathBuf::from("asdf"));

        let interpreters = Interpreters {
            python_interpreter_path: Some(python_interpreter.clone()),
            ..Default::default()
        };

        assert_eq!(
            interpreters.find_interpreter(Some(tempdir.path())).unwrap(),
            python_interpreter
        );
    }

    #[test]
    fn test_find_interpreter_precedence_lsp_highest_priority() {
        let tempdir = setup_test_dir();

        let python_interpreter = ConfigOrigin::lsp(PathBuf::from("asdf"));

        let interpreters = Interpreters {
            python_interpreter_path: Some(python_interpreter.clone()),
            ..Default::default()
        };

        assert_eq!(
            interpreters.find_interpreter(Some(tempdir.path())).unwrap(),
            python_interpreter
        );
    }

    #[test]
    fn test_find_interpreter_precedence_conda_cli_highest_priority() {
        let tempdir = setup_test_dir();

        // this conda environment really shouldn't be able to exist
        let conda_environment = ConfigOrigin::cli("../././".to_owned());

        let interpreters = Interpreters {
            conda_environment: Some(conda_environment),
            ..Default::default()
        };

        assert!(interpreters.find_interpreter(Some(tempdir.path())).is_err());
    }

    #[test]
    fn test_find_interpreter_precedence_conda_config() {
        let tempdir = setup_test_dir();

        // this conda environment really shouldn't be able to exist
        let conda_environment = ConfigOrigin::config("../././".to_owned());

        let interpreters = Interpreters {
            conda_environment: Some(conda_environment),
            ..Default::default()
        };

        assert!(interpreters.find_interpreter(Some(tempdir.path())).is_err());
    }

    #[test]
    fn test_find_interpreter_precedence_venv() {
        let tempdir = setup_test_dir();

        let interpreters = Interpreters::default();
        let interpreter_suffix = if cfg!(windows) { ".exe" } else { "" };

        assert_eq!(
            interpreters.find_interpreter(Some(tempdir.path())).unwrap(),
            ConfigOrigin::auto(
                tempdir
                    .path()
                    .join(format!("venv/python3{interpreter_suffix}"))
            )
        );
    }
}
