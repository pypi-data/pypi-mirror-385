/*
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

use std::collections::HashSet;
use std::path::PathBuf;
use std::sync::Arc;

use dupe::Dupe;
use lsp_types::Url;
use lsp_types::WorkspaceFoldersChangeEvent;
use pyrefly_util::arc_id::ArcId;
use pyrefly_util::arc_id::WeakArcId;
use pyrefly_util::lock::Mutex;
use pyrefly_util::lock::RwLock;
use serde::Deserialize;
use serde_json::Value;
use starlark_map::small_map::SmallMap;
use starlark_map::small_set::SmallSet;
use tracing::error;

use crate::commands::config_finder::ConfigConfigurer;
use crate::commands::config_finder::standard_config_finder;
use crate::config::config::ConfigFile;
use crate::config::environment::environment::PythonEnvironment;
use crate::config::finder::ConfigFinder;
use crate::state::lsp::DisplayTypeErrors;
use crate::state::lsp::ImportFormat;
use crate::state::lsp::InlayHintConfig;

/// Information about the Python environment provided by this workspace.
#[derive(Debug, Clone)]
pub struct PythonInfo {
    /// The path to the interpreter used to query this `PythonInfo`'s [`PythonEnvironment`].
    interpreter: PathBuf,
    /// The [`PythonEnvironment`] values all [`ConfigFile`]s in a given workspace should
    /// use if no explicit [`ConfigFile::python_interpreter`] is provided, or any
    /// `PythonEnvironment` values in that `ConfigFile` are unfiled. If the `interpreter
    /// provided fails to execute or is invalid, this `PythonEnvironment` might instead
    /// be a system interpreter or [`PythonEnvironment::pyrefly_default()`].
    env: PythonEnvironment,
}

impl PythonInfo {
    pub fn new(interpreter: PathBuf) -> Self {
        let (env, query_error) = PythonEnvironment::get_interpreter_env(&interpreter);
        if let Some(error) = query_error {
            error!("{error}");
        }
        Self { interpreter, env }
    }
}

/// LSP workspace settings: this is all that is necessary to run an LSP at a given root.
#[derive(Debug, Clone, Default)]
pub struct Workspace {
    python_info: Option<PythonInfo>,
    search_path: Option<Vec<PathBuf>>,
    pub disable_language_services: bool,
    pub display_type_errors: Option<DisplayTypeErrors>,
    pub lsp_analysis_config: Option<LspAnalysisConfig>,
}

impl Workspace {
    pub fn new() -> Self {
        Self::default()
    }
}

struct WorkspaceConfigConfigurer(Arc<Workspaces>);

impl ConfigConfigurer for WorkspaceConfigConfigurer {
    fn configure(
        &self,
        root: Option<&std::path::Path>,
        mut config: ConfigFile,
        mut errors: Vec<pyrefly_config::finder::ConfigError>,
    ) -> (ArcId<ConfigFile>, Vec<pyrefly_config::finder::ConfigError>) {
        if let Some(dir) = root {
            self.0.get_with(dir.to_owned(), |w| {
                if let Some(search_path) = w.search_path.clone() {
                    config.search_path_from_args = search_path;
                }
                if let Some(PythonInfo {
                    interpreter,
                    mut env,
                }) = w.python_info.clone()
                    && config.interpreters.is_empty()
                {
                    let site_package_path: Option<Vec<PathBuf>> =
                        config.python_environment.site_package_path.take();
                    env.site_package_path = site_package_path;
                    config.interpreters.set_lsp_python_interpreter(interpreter);
                    config.python_environment = env;
                    // skip interpreter query because we already have the interpreter from the workspace
                    config.interpreters.skip_interpreter_query = true;
                }
            })
        };

        // we print the errors here instead of returning them since
        // it gives the most immediate feedback for config loading errors
        for error in errors.drain(..).chain(config.configure()) {
            error.print();
        }
        let config = ArcId::new(config);

        self.0.loaded_configs.insert(config.downgrade());

        (config, errors)
    }
}

/// A cache of loaded configs from the LSP's [`standard_config_finder`]. These
/// values are [`WeakArcId`]s, so they will be dropped when no other references
/// point to them. We use this for determining the list of files we need to watch
/// when setting up the watcher.
pub struct WeakConfigCache(Mutex<HashSet<WeakArcId<ConfigFile>>>);

impl WeakConfigCache {
    pub fn new() -> Self {
        Self(Mutex::new(HashSet::new()))
    }

    pub fn insert(&self, config: WeakArcId<ConfigFile>) {
        self.0.lock().insert(config);
    }

    /// Purge any [`WeakArcId`]s that are [`WeakArcId::vacant`], and return
    /// the remaining configs, converted to [`ArcId`]s.
    pub fn clean_and_get_configs(&self) -> SmallSet<ArcId<ConfigFile>> {
        let mut configs = self.0.lock();
        let purged_config_count = configs.extract_if(|c| c.vacant()).count();
        if purged_config_count != 0 {
            eprintln!("Cleared {purged_config_count} dropped configs from config cache");
        }
        SmallSet::from_iter(configs.iter().filter_map(|c| c.upgrade()))
    }
}

#[derive(Debug, Default, Deserialize)]
#[serde(rename_all = "camelCase")]
struct PyreflyClientConfig {
    display_type_errors: Option<DisplayTypeErrors>,
    disable_language_services: Option<bool>,
    extra_paths: Option<Vec<PathBuf>>,
}

#[derive(Clone, Copy, Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub enum DiagnosticMode {
    #[serde(rename = "workspace")]
    Workspace,
    #[serde(rename = "openFilesOnly")]
    OpenFilesOnly,
}

/// https://code.visualstudio.com/docs/python/settings-reference#_pylance-language-server
#[derive(Clone, Copy, Debug, Default, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct LspAnalysisConfig {
    #[allow(dead_code)]
    pub diagnostic_mode: Option<DiagnosticMode>,
    pub import_format: Option<ImportFormat>,
    pub inlay_hints: Option<InlayHintConfig>,
}

fn deserialize_analysis<'de, D>(deserializer: D) -> Result<Option<LspAnalysisConfig>, D::Error>
where
    D: serde::Deserializer<'de>,
{
    match Option::<LspAnalysisConfig>::deserialize(deserializer) {
        Ok(value) => Ok(value),
        Err(e) => {
            eprintln!("Could not decode analysis config: {e}");
            Ok(None)
        }
    }
}

#[derive(Debug, Default, Deserialize)]
#[serde(rename_all = "camelCase")]
struct LspConfig {
    #[serde(default, deserialize_with = "deserialize_analysis")]
    analysis: Option<LspAnalysisConfig>,
    python_path: Option<String>,
    pyrefly: Option<PyreflyClientConfig>,
}

pub struct Workspaces {
    /// If a workspace is not found, this one is used. It contains every possible file on the system but is lowest priority.
    default: RwLock<Workspace>,
    pub workspaces: RwLock<SmallMap<PathBuf, Workspace>>,
    pub loaded_configs: Arc<WeakConfigCache>,
}

impl Workspaces {
    pub fn new(default: Workspace, folders: &[PathBuf]) -> Self {
        Self {
            default: RwLock::new(default),
            workspaces: RwLock::new(
                folders
                    .iter()
                    .map(|x| (x.clone(), Workspace::new()))
                    .collect(),
            ),
            loaded_configs: Arc::new(WeakConfigCache::new()),
        }
    }

    pub fn get_with<F, R>(&self, uri: PathBuf, f: F) -> R
    where
        F: FnOnce(&Workspace) -> R,
    {
        let workspaces = self.workspaces.read();
        let default_workspace = self.default.read();
        let workspace = workspaces
            .iter()
            .filter(|(key, _)| uri.starts_with(key))
            // select the LONGEST match (most specific workspace folder)
            .max_by(|(key1, _), (key2, _)| key1.ancestors().count().cmp(&key2.ancestors().count()))
            .map(|(_, workspace)| workspace);
        f(workspace.unwrap_or(&default_workspace))
    }

    pub fn config_finder(workspaces: &Arc<Workspaces>) -> ConfigFinder {
        standard_config_finder(Arc::new(WorkspaceConfigConfigurer(workspaces.dupe())))
    }

    pub fn roots(&self) -> Vec<PathBuf> {
        self.workspaces.read().keys().cloned().collect::<Vec<_>>()
    }

    pub fn changed(&self, event: WorkspaceFoldersChangeEvent) {
        let mut workspaces = self.workspaces.write();
        for x in event.removed {
            workspaces.shift_remove(&x.uri.to_file_path().unwrap());
        }
        for x in event.added {
            workspaces.insert(x.uri.to_file_path().unwrap(), Workspace::new());
        }
    }

    /// Applies the LSP client configuration to the `scope_uri` (workspace) given.
    ///
    /// The `modified` flag is changed to `true` when the configuration gets applied to the
    /// `scope_uri` matching a valid workspace
    pub fn apply_client_configuration(
        &self,
        modified: &mut bool,
        scope_uri: &Option<Url>,
        config: Value,
    ) {
        let config = match serde_json::from_value::<LspConfig>(config.clone()) {
            Err(e) => {
                eprintln!(
                    "Could not decode `LspConfig` from {config:?}, skipping client configuration request: {e}."
                );
                return;
            }
            Ok(x) => x,
        };

        if let Some(python_path) = config.python_path {
            self.update_pythonpath(modified, scope_uri, &python_path);
        }

        if let Some(pyrefly) = config.pyrefly {
            if let Some(extra_paths) = pyrefly.extra_paths {
                self.update_search_paths(modified, scope_uri, extra_paths);
            }
            if let Some(disable_language_services) = pyrefly.disable_language_services {
                self.update_disable_language_services(scope_uri, disable_language_services);
            }
            self.update_display_type_errors(modified, scope_uri, pyrefly.display_type_errors);
        }
        if let Some(analysis) = config.analysis {
            self.update_ide_settings(modified, scope_uri, analysis);
        }
    }

    /// Update disableLanguageServices setting for scope_uri, None if default workspace
    fn update_disable_language_services(
        &self,
        scope_uri: &Option<Url>,
        disable_language_services: bool,
    ) {
        let mut workspaces = self.workspaces.write();
        match scope_uri {
            Some(scope_uri) => {
                if let Some(workspace) = workspaces.get_mut(&scope_uri.to_file_path().unwrap()) {
                    workspace.disable_language_services = disable_language_services;
                }
            }
            None => self.default.write().disable_language_services = disable_language_services,
        }
    }

    /// Update typeCheckingMode setting for scope_uri, None if default workspace
    fn update_display_type_errors(
        &self,
        modified: &mut bool,
        scope_uri: &Option<Url>,
        display_type_errors: Option<DisplayTypeErrors>,
    ) {
        let mut workspaces = self.workspaces.write();
        match scope_uri {
            Some(scope_uri) => {
                if let Some(workspace) = workspaces.get_mut(&scope_uri.to_file_path().unwrap()) {
                    *modified = true;
                    workspace.display_type_errors = display_type_errors;
                }
            }
            None => {
                *modified = true;
                self.default.write().display_type_errors = display_type_errors
            }
        }
    }

    fn update_ide_settings(
        &self,
        modified: &mut bool,
        scope_uri: &Option<Url>,
        lsp_analysis_config: LspAnalysisConfig,
    ) {
        let mut workspaces = self.workspaces.write();
        match scope_uri {
            Some(scope_uri) => {
                if let Some(workspace) = workspaces.get_mut(&scope_uri.to_file_path().unwrap()) {
                    *modified = true;
                    workspace.lsp_analysis_config = Some(lsp_analysis_config);
                }
            }
            None => {
                *modified = true;
                self.default.write().lsp_analysis_config = Some(lsp_analysis_config);
            }
        }
    }

    /// Updates pythonpath with specified python path
    /// scope_uri = None for default workspace
    fn update_pythonpath(&self, modified: &mut bool, scope_uri: &Option<Url>, python_path: &str) {
        let mut workspaces = self.workspaces.write();
        let interpreter = PathBuf::from(python_path);
        let python_info = Some(PythonInfo::new(interpreter));
        match scope_uri {
            Some(scope_uri) => {
                let workspace_path = scope_uri.to_file_path().unwrap();
                if let Some(workspace) = workspaces.get_mut(&workspace_path) {
                    *modified = true;
                    workspace.python_info = python_info;
                }
            }
            None => {
                *modified = true;
                self.default.write().python_info = python_info;
            }
        }
    }

    // Updates search paths for scope uri.
    fn update_search_paths(
        &self,
        modified: &mut bool,
        scope_uri: &Option<Url>,
        search_paths: Vec<PathBuf>,
    ) {
        let mut workspaces = self.workspaces.write();
        match scope_uri {
            Some(scope_uri) => {
                let workspace_path = scope_uri.to_file_path().unwrap();
                if let Some(workspace) = workspaces.get_mut(&workspace_path) {
                    *modified = true;
                    workspace.search_path = Some(search_paths);
                }
            }
            None => {
                *modified = true;
                self.default.write().search_path = Some(search_paths);
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use serde_json::json;

    use super::*;

    #[test]
    fn test_get_with_selects_longest_match() {
        let workspace_root = PathBuf::from("/projects");
        let workspace_nested = PathBuf::from("/projects/my_project");

        let folders = vec![workspace_root.clone(), workspace_nested.clone()];

        let workspaces = Workspaces::new(Workspace::new(), &folders);
        {
            let mut workspaces_map = workspaces.workspaces.write();
            // Set root workspace to have a search_path
            workspaces_map.get_mut(&workspace_root).unwrap().search_path =
                Some(vec![PathBuf::from("/projects/search_root")]);
            // Set nested workspace to have a different search_path
            workspaces_map
                .get_mut(&workspace_nested)
                .unwrap()
                .search_path = Some(vec![PathBuf::from("/projects/my_project/search_nested")]);
        }

        let result = workspaces
            .get_with(PathBuf::from("/projects/my_project/nested_file.py"), |w| {
                w.search_path.clone()
            });
        assert_eq!(
            result,
            Some(vec![PathBuf::from("/projects/my_project/search_nested")]),
            "Nested file should match nested workspace (longest match), not root"
        );

        let result = workspaces.get_with(PathBuf::from("/projects/file.py"), |w| {
            w.search_path.clone()
        });
        assert_eq!(
            result,
            Some(vec![PathBuf::from("/projects/search_root")]),
            "Root file should match root workspace"
        );

        let result = workspaces.get_with(PathBuf::from("/other/path/file.py"), |w| {
            w.search_path.clone()
        });
        assert_eq!(
            result, None,
            "File outside workspaces should use default workspace"
        );
    }

    #[test]
    fn test_get_with_filters_prefixes() {
        let workspace_a = PathBuf::from("/workspace");
        let workspace_b = PathBuf::from("/workspace_other");

        let folders = vec![workspace_a.clone(), workspace_b.clone()];
        let workspaces = Workspaces::new(Workspace::new(), &folders);

        {
            let mut workspaces_map = workspaces.workspaces.write();
            workspaces_map.get_mut(&workspace_a).unwrap().search_path =
                Some(vec![PathBuf::from("/workspace/search_a")]);
            workspaces_map.get_mut(&workspace_b).unwrap().search_path =
                Some(vec![PathBuf::from("/workspace_other/search_b")]);
        }

        let file_a = PathBuf::from("/workspace/file.py");
        let result = workspaces.get_with(file_a, |w| w.search_path.clone());
        assert_eq!(
            result,
            Some(vec![PathBuf::from("/workspace/search_a")]),
            "File in /workspace should match /workspace workspace"
        );

        let file_b = PathBuf::from("/workspace_other/file.py");
        let result = workspaces.get_with(file_b, |w| w.search_path.clone());
        assert_eq!(
            result,
            Some(vec![PathBuf::from("/workspace_other/search_b")]),
            "File in /workspace_other should match /workspace_other workspace"
        );
    }

    #[test]
    fn test_broken_analysis_config_still_creates_lsp_config() {
        let broken_config = json!({
            "pythonPath": "/usr/bin/python3",
            "analysis": {
                "invalidField": true,
                "diagnosticMode": "invalidMode",
                "importFormat": "invalidFormat"
            },
            "pyrefly": {
                "disableLanguageServices": false,
                "extraPaths": ["/some/path"]
            }
        });

        let lsp_config: Result<LspConfig, _> = serde_json::from_value(broken_config);

        assert!(lsp_config.is_ok());
        let config = lsp_config.unwrap();
        assert!(config.analysis.is_none());
        assert_eq!(config.python_path, Some("/usr/bin/python3".to_owned()));
        assert!(config.pyrefly.is_some());
        let pyrefly = config.pyrefly.unwrap();
        assert_eq!(pyrefly.disable_language_services, Some(false));
        assert_eq!(pyrefly.extra_paths, Some(vec![PathBuf::from("/some/path")]));
    }

    #[test]
    fn test_valid_analysis_config_creates_lsp_config_with_analysis() {
        let valid_config = json!({
            "pythonPath": "/usr/bin/python3",
            "analysis": {
                "diagnosticMode": "workspace",
                "importFormat": "absolute"
            },
            "pyrefly": {
                "disableLanguageServices": false
            }
        });

        let lsp_config: Result<LspConfig, _> = serde_json::from_value(valid_config);
        assert!(lsp_config.is_ok());
        let config = lsp_config.unwrap();
        assert!(config.analysis.is_some());
        let analysis = config.analysis.unwrap();
        assert!(matches!(
            analysis.diagnostic_mode,
            Some(DiagnosticMode::Workspace)
        ));
        assert!(matches!(
            analysis.import_format,
            Some(ImportFormat::Absolute)
        ));
        assert_eq!(config.python_path, Some("/usr/bin/python3".to_owned()));
        assert!(config.pyrefly.is_some());
    }
}
