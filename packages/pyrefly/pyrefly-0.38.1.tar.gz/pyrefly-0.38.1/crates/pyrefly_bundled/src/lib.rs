/*
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

use std::env;
use std::io::Read;
use std::path::PathBuf;

use anyhow::Context as _;
use starlark_map::small_map::SmallMap;
use tar::Archive;
use zstd::stream::read::Decoder;

const BUNDLED_TYPESHED_BYTES: &[u8] = include_bytes!(concat!(env!("OUT_DIR"), "/typeshed.tar.zst"));

enum PathFilter {
    /// Filter for stdlib files (typeshed/stdlib/...)
    Stdlib,
    /// Filter for third-party stubs (typeshed/stubs/package-name/...)
    ThirdPartyStubs,
}

impl PathFilter {
    fn expected_first_component(&self) -> &str {
        match self {
            PathFilter::Stdlib => "stdlib",
            PathFilter::ThirdPartyStubs => "stubs",
        }
    }

    #[allow(dead_code)]
    fn should_skip_next_component(&self) -> bool {
        match self {
            PathFilter::Stdlib => false,
            PathFilter::ThirdPartyStubs => true, // Skip package directory
        }
    }
}

fn extract_pyi_files_from_archive(filter: PathFilter) -> anyhow::Result<SmallMap<PathBuf, String>> {
    let decoder = Decoder::new(BUNDLED_TYPESHED_BYTES)?;
    let mut archive = Archive::new(decoder);
    let entries = archive
        .entries()
        .context("Cannot query all entries in typeshed archive")?;

    let mut items = SmallMap::new();

    for maybe_entry in entries {
        let mut entry = maybe_entry.context("Cannot read individual entry in typeshed archive")?;

        if entry.header().entry_type().is_dir() {
            continue;
        }

        let relative_path_context = entry
            .path()
            .context("Cannot extract path from archive entry")?;

        let mut relative_path_components = relative_path_context.components();

        let first_component = relative_path_components.next();
        if first_component
            .is_none_or(|component| component.as_os_str() != filter.expected_first_component())
        {
            continue;
        }

        let relative_path = relative_path_components.collect::<PathBuf>();
        if relative_path.extension().is_none_or(|ext| ext != "pyi") {
            // typeshed/stdlib/ contains non-.pyi files like VERSIONS that we don't care about.
            continue;
        }

        let size = entry.size();
        let mut contents = String::with_capacity(size as usize);
        entry
            .read_to_string(&mut contents)
            .context("Cannot read content of archive entry")?;
        items.entry(relative_path).or_insert(contents);
    }

    Ok(items)
}

pub fn bundled_typeshed() -> anyhow::Result<SmallMap<PathBuf, String>> {
    extract_pyi_files_from_archive(PathFilter::Stdlib)
}

#[allow(dead_code)]
pub fn bundled_third_party_stubs() -> anyhow::Result<SmallMap<PathBuf, String>> {
    extract_pyi_files_from_archive(PathFilter::ThirdPartyStubs)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_bundled_typeshed_returns_stdlib_files() {
        let result = bundled_typeshed();
        assert!(result.is_ok(), "bundled_typeshed should succeed");

        let files = result.unwrap();
        assert!(!files.is_empty(), "Should contain stdlib .pyi files");

        // Verify all returned paths are .pyi files
        for (path, _) in files.iter() {
            assert_eq!(
                path.extension().and_then(|ext| ext.to_str()),
                Some("pyi"),
                "All files should have .pyi extension, found: {:?}",
                path
            );
        }
    }

    #[test]
    fn test_bundled_typeshed_paths_are_relative() {
        let result = bundled_typeshed().unwrap();

        // Verify paths don't start with "stdlib" (it should be stripped)
        for (path, _) in result.iter() {
            let first_component = path.components().next();
            assert_ne!(
                first_component.and_then(|c| c.as_os_str().to_str()),
                Some("stdlib"),
                "Path should not start with 'stdlib', found: {:?}",
                path
            );
        }
    }

    #[test]
    fn test_bundled_typeshed_contains_common_modules() {
        let files = bundled_typeshed().unwrap();

        // Check that at least some .pyi files exist that match common module patterns
        let has_builtins = files.iter().any(|(path, _)| {
            path.to_str()
                .map(|s| s.contains("builtins"))
                .unwrap_or(false)
        });
        let has_sys = files
            .iter()
            .any(|(path, _)| path.to_str().map(|s| s.contains("sys")).unwrap_or(false));
        let has_os = files
            .iter()
            .any(|(path, _)| path.to_str().map(|s| s.contains("os")).unwrap_or(false));

        assert!(
            has_builtins || has_sys || has_os,
            "Should contain at least one common stdlib module (builtins, sys, or os)"
        );
    }

    #[test]
    fn test_bundled_typeshed_file_contents_not_empty() {
        let files = bundled_typeshed().unwrap();

        let non_empty_count = files
            .iter()
            .filter(|(_, content)| !content.is_empty())
            .count();
        assert!(
            non_empty_count > 0,
            "Should have at least some files with content"
        );
    }

    #[test]
    fn test_extract_pyi_files_from_archive_stdlib_filter() {
        let result = extract_pyi_files_from_archive(PathFilter::Stdlib);
        assert!(result.is_ok(), "Should successfully extract stdlib files");

        let files = result.unwrap();
        assert!(
            !files.is_empty(),
            "Should extract at least some stdlib files"
        );

        let unique_count = files.len();
        assert_eq!(files.len(), unique_count, "Should not have duplicate paths");
    }

    #[test]
    fn test_path_filter_expected_first_component() {
        assert_eq!(
            PathFilter::Stdlib.expected_first_component(),
            "stdlib",
            "Stdlib filter should expect 'stdlib' component"
        );
        assert_eq!(
            PathFilter::ThirdPartyStubs.expected_first_component(),
            "stubs",
            "ThirdPartyStubs filter should expect 'stubs' component"
        );
    }

    #[test]
    fn test_bundled_typeshed_contains_valid_python_stubs() {
        let files = bundled_typeshed().unwrap();

        // Check that at least some files contain Python stub signatures
        let has_python_stub_content = files.iter().any(|(_, content)| {
            content.contains("def ") || content.contains("class ") || content.contains("import ")
        });

        assert!(
            has_python_stub_content,
            "At least some files should contain Python stub content"
        );
    }

    #[test]
    fn test_no_non_pyi_files_included() {
        let stdlib_files = bundled_typeshed().unwrap();
        let third_party_files = bundled_third_party_stubs().unwrap();

        for (path, _) in stdlib_files.iter().chain(third_party_files.iter()) {
            let ext = path.extension().and_then(|e| e.to_str());
            assert_eq!(
                ext,
                Some("pyi"),
                "Should only include .pyi files, found extension: {:?} in path: {:?}",
                ext,
                path
            );
        }
    }
}
