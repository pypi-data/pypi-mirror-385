## Tree for jiggle_version
```
├── gitignore.py
├── pypi.py
├── utils/
│   ├── cli_suggestions.py
│   └── logging_config.py
├── update.py
├── auto.py
├── py.typed
├── parsers/
│   ├── config_parser.py
│   └── ast_parser.py
├── __about__.py
├── schemes.py
├── bump.py
├── __main__.py
├── git.py
├── discover.py
└── config.py
```

## File: gitignore.py
```python
# jiggle_version/gitignore.py
"""
Git-aware path ignoring built on `pathspec`'s `GitWildMatchPattern`.

Goals
-----
- Correctly honor .gitignore semantics (wildcards, directory suffix `/`,
  negation `!`, anchored vs unanchored patterns, etc.).
- Allow optional user-supplied ignore patterns to merge with repo rules.
- Provide a simple `is_path_gitignored` API usable by call sites.

Notes
-----
- We do **not** shell out to `git`.
- We merge patterns from, in order:
  1) `<project_root>/.gitignore` (if present)
  2) `<project_root>/.git/info/exclude` (if present)
  3) Global excludes file (~/.config/git/ignore or ~/.gitignore)
  4) `extra_patterns` provided by the caller
  Later rules can override earlier ones via negation (`!pattern`).

Dependency
----------
`pathspec>=0.12` (https://pypi.org/project/pathspec/)

Public functions
----------------
- `build_gitignore_spec(project_root: Path, extra_patterns: list[str] | None) -> PathSpec`
- `is_path_gitignored(path: Path, project_root: Path, spec_or_patterns: PathSpec | list[str] | None) -> bool`
- `is_path_explicitly_ignored(path: Path, ignored_paths: set[Path]) -> bool`
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern

# ----------------------------- helpers -----------------------------


def _read_lines(p: Path) -> list[str]:
    """Read a text file into a list of lines, stripping trailing newlines.

    Returns empty list if the file does not exist.
    """
    if not p.is_file():
        return []
    return [ln.rstrip("\n") for ln in p.read_text(encoding="utf-8").splitlines()]


def _candidate_global_ignores() -> list[Path]:
    """Return plausible global gitignore locations (best-effort, no git call)."""
    home = Path.home()
    # Common defaults used by Git when core.excludesFile is not set explicitly
    return [
        home / ".config" / "git" / "ignore",
        home / ".gitignore",
    ]


# ----------------------------- core build -----------------------------


def build_gitignore_spec(
    project_root: Path,
    *,
    extra_patterns: list[str] | None = None,
) -> PathSpec:
    """Construct a `PathSpec` with Git-style matching semantics.

    Parameters
    ----------
    project_root: Path
        Repository/work-tree root. Patterns are interpreted relative to this folder.
    extra_patterns: list[str] | None
        Additional patterns to append **after** repo/global sources.

    Returns
    -------
    PathSpec
        Compiled spec. Safe to reuse across many `is_path_gitignored` calls.
    """
    patterns: list[str] = []

    # Root .gitignore
    patterns += _read_lines(project_root / ".gitignore")

    # Repo local excludes
    patterns += _read_lines(project_root / ".git" / "info" / "exclude")

    # Global excludes (best-effort)
    for p in _candidate_global_ignores():
        patterns += _read_lines(p)

    # User-provided patterns last (can override via negation)
    if extra_patterns:
        patterns += list(extra_patterns)

    # Normalize: drop comments/blank lines here; pathspec handles the rest
    normalized: list[str] = []
    for raw in patterns:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        normalized.append(line)

    return PathSpec.from_lines(GitWildMatchPattern, normalized)


# ----------------------------- queries -----------------------------


def is_path_gitignored(
    path: Path,
    project_root: Path,
    spec_or_patterns: PathSpec | Iterable[str] | None,
) -> bool:
    """Return True if `path` is ignored by the given spec or patterns.

    - `path` may be file or directory (existing or hypothetical).
    - `project_root` anchors relative matching.
    - `spec_or_patterns` can be a pre-built `PathSpec`, an iterable of pattern
      strings (Git semantics), or `None` (treated as empty).

    Implementation detail: `pathspec` expects POSIX-style paths. We therefore
    convert `path.relative_to(project_root)` to a forward-slash string.
    """
    rel = path.resolve().relative_to(project_root.resolve())
    rel_str = rel.as_posix()

    if isinstance(spec_or_patterns, PathSpec):
        spec = spec_or_patterns
    else:
        patterns = list(spec_or_patterns or [])
        spec = PathSpec.from_lines(GitWildMatchPattern, patterns)

    # `match_file` applies directory-aware rules correctly
    return spec.match_file(rel_str)


def is_path_explicitly_ignored(path: Path, ignored_paths: set[Path]) -> bool:
    """Return True if `path` equals or is a descendant of any path in `ignored_paths`.

    This is an explicit, non-.gitignore override that callers can use for
    user-specified absolute directories/files.
    """
    abs_path = path.resolve()
    for ip in ignored_paths:
        ip = ip.resolve()
        if abs_path == ip or ip in abs_path.parents:
            return True
    return False


# ----------------------------- convenience -----------------------------


def collect_default_spec(
    project_root: Path, extra_patterns: list[str] | None = None
) -> PathSpec:
    """One-shot helper used by callers that don't need fine control."""
    return build_gitignore_spec(project_root, extra_patterns=extra_patterns)
```
## File: pypi.py
```python
# jiggle_version/pypi.py
"""
Implements a pre-flight check against PyPI to prevent bumping an unpublished version.
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
import tomlkit
from packaging.version import Version

# Handle Python < 3.11 needing tomli
if sys.version_info < (3, 11):
    import tomli as tomllib
else:
    import tomllib


# --- Custom Exception ---
class UnpublishedVersionError(Exception):
    """Raised when attempting to bump a version that is unpublished on PyPI."""


# --- Caching Configuration ---
CACHE_TTL = timedelta(days=1)


def get_package_name(project_root: Path) -> str | None:
    """
    Finds the package name from pyproject.toml [project].name.
    """
    pyproject_path = project_root / "pyproject.toml"
    if not pyproject_path.is_file():
        return None
    try:
        config = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
        return config.get("project", {}).get("name")
    except tomllib.TOMLDecodeError:
        return None


def get_latest_published_version(package_name: str, config_path: Path) -> str | None:
    """
    Fetches the latest published version of a package from PyPI, caching the
    result in the project's .jiggle_version.config file.
    """
    # --- Read from TOML cache ---
    doc = (
        tomlkit.parse(config_path.read_text(encoding="utf-8"))
        if config_path.is_file()
        else tomlkit.document()
    )
    jiggle_tool_config = doc.get("tool", {}).get("jiggle_version", {})
    pypi_cache = jiggle_tool_config.get("pypi_cache", {})
    last_checked_str = pypi_cache.get("timestamp")

    if last_checked_str:
        last_checked = datetime.fromisoformat(last_checked_str)
        if datetime.now(timezone.utc) - last_checked < CACHE_TTL:
            print(
                f"   (from cache created at {last_checked.strftime('%Y-%m-%d %H:%M')})"
            )
            return pypi_cache.get("latest_version")

    # --- Fetch from PyPI ---
    print("   (querying pypi.org...)")
    url = f"https://pypi.org/pypi/{package_name}/json"
    latest_version = None
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 404:
            latest_version = None  # Package not on PyPI at all
        elif response.status_code == 200:
            data = response.json()
            latest_version = data.get("info", {}).get("version")
        # On other errors, we return None to skip the check gracefully

        # --- Update TOML cache ---
        cache_table = tomlkit.table()
        cache_table.add("timestamp", datetime.now(timezone.utc).isoformat())
        cache_table.add("latest_version", latest_version)

        if "tool" not in doc:
            doc.add("tool", tomlkit.table())
        if "jiggle_version" not in doc.get("tool", {}):  # type: ignore
            doc["tool"].add("jiggle_version", tomlkit.table())  # type: ignore

        doc["tool"]["jiggle_version"]["pypi_cache"] = cache_table  # type: ignore
        config_path.write_text(tomlkit.dumps(doc), encoding="utf-8")

    except requests.RequestException:
        # Network error, skip the check
        pass

    return latest_version


def check_pypi_publication(
    package_name: str, current_version: str, new_version: str, config_path: Path
) -> None:
    """
    Checks if the current version is published and allows bumping under specific rules.
    """
    latest_published_str = get_latest_published_version(package_name, config_path)

    if not latest_published_str:
        # NEW BEHAVIOR: If the package has never been published, block the bump.
        raise UnpublishedVersionError(
            f"Package '{package_name}' is not on PyPI. Publish the initial version first."
        )

    current_v = Version(current_version)
    published_v = Version(latest_published_str)
    new_v = Version(new_version)

    if current_v > published_v:
        if new_v > current_v:
            print(
                f"🟡 Current version '{current_v}' is unpublished (PyPI has '{published_v}'). "
                f"Allowing bump to '{new_v}'."
            )
            return
        raise UnpublishedVersionError(
            f"Current version '{current_v}' is not published on PyPI (latest is '{published_v}').\n"
            "Cannot perform a redundant bump."
        )
    elif new_v > published_v:
        print(f"✅ PyPI version is '{published_v}'. Bump to '{new_v}' is allowed.")
        return
    else:
        raise UnpublishedVersionError(
            f"New version '{new_v}' is not greater than the latest published version on PyPI ('{published_v}')."
        )
```
## File: update.py
```python
# jiggle_version/update.py
"""
Logic for updating version strings in various source files.
"""
from __future__ import annotations

import re
from pathlib import Path

import tomlkit


def update_pyproject_toml(file_path: Path, new_version: str) -> None:
    """Updates the version in a pyproject.toml file using tomlkit to preserve formatting."""
    doc = tomlkit.parse(file_path.read_text(encoding="utf-8"))

    updated = False
    if "project" in doc and "version" in doc["project"]:  # type: ignore[operator]
        doc["project"]["version"] = new_version  # type: ignore[index]
        updated = True
    elif "tool" in doc and "setuptools" in doc["tool"] and "version" in doc["tool"]["setuptools"]:  # type: ignore[operator,index]
        doc["tool"]["setuptools"]["version"] = new_version  # type: ignore[index]
        updated = True

    if updated:
        file_path.write_text(tomlkit.dumps(doc), encoding="utf-8")


def update_setup_cfg(file_path: Path, new_version: str) -> None:
    """Updates the version in a setup.cfg file using regex."""
    content = file_path.read_text(encoding="utf-8")
    # Regex to find 'version = ...' under the [metadata] section
    new_content = re.sub(
        r"(?<=^\[metadata\]\s*\n(?:.*\n)*?version\s*=\s*).*",
        new_version,
        content,
        flags=re.MULTILINE,
    )
    file_path.write_text(new_content, encoding="utf-8")


def update_python_file(file_path: Path, new_version: str) -> None:
    """Updates the version in a Python file (`__version__` or `setup.py`) using regex."""
    content = file_path.read_text(encoding="utf-8")
    # Regex to find `__version__ = "..."` or `version="..."`
    # It captures the quote style to preserve it.
    pattern = re.compile(r"""(__version__\s*=\s*|version\s*=\s*)['"](.*?)['"]""")

    def replacer(match):
        # Reconstruct the line with the new version, keeping the original quote style
        # by simply replacing the content between the quotes.
        return f'{match.group(1)}"{new_version}"'

    new_content, count = pattern.subn(replacer, content)

    if count > 0:
        file_path.write_text(new_content, encoding="utf-8")
```
## File: auto.py
```python
# jiggle_version/auto.py
"""
Implements the logic for the 'auto' increment feature.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import tomlkit

from .gitignore import (
    collect_default_spec,
    is_path_explicitly_ignored,
    is_path_gitignored,
)
from .parsers.ast_parser import parse_dunder_all


def get_current_symbols(
    project_root: Path, ignore_paths: list[str] | None = None
) -> set[str]:
    """Discovers and parses all __all__ symbols in a project.

    Walks every *.py under project_root, honoring .gitignore and user-specified ignores.
    """
    symbols: set[str] = set()

    # Build ignore spec once; normalize explicit ignores to absolute paths.
    spec = collect_default_spec(project_root)
    explicit_ignores = {(project_root / p).resolve() for p in (ignore_paths or [])}

    for py_file in project_root.rglob("*.py"):
        # Respect .gitignore and explicit ignore paths.
        if is_path_gitignored(py_file, project_root, spec):
            continue
        if is_path_explicitly_ignored(py_file, explicit_ignores):
            continue

        symbols.update(parse_dunder_all(py_file))

    return symbols


def read_digest_data(digest_path: Path) -> dict[str, Any]:
    """Reads the stored digest data from the config file."""
    if not digest_path.is_file():
        return {}
    return tomlkit.parse(digest_path.read_text(encoding="utf-8"))


def write_digest_data(digest_path: Path, symbols: set[str]) -> None:
    """Writes the current symbols to the digest file."""
    sorted_symbols = sorted(list(symbols))

    # Per the PEP, we store the symbols themselves to allow for comparison.
    # A composite digest is also stored for quick checks.
    sha256 = hashlib.sha256("".join(sorted_symbols).encode("utf-8")).hexdigest()

    doc = tomlkit.document()
    doc.add("digest", f"sha256:{sha256}")  # type: ignore[arg-type]
    doc.add("symbols", sorted_symbols)  # type: ignore[arg-type]

    digest_path.write_text(tomlkit.dumps(doc), encoding="utf-8")


def determine_auto_increment(
    project_root: Path, digest_path: Path, ignore_paths: list[str] | None = None
) -> str:
    """
    Determines the increment by comparing current and stored __all__ symbols.
    """
    current_symbols = get_current_symbols(project_root, ignore_paths)
    digest_data = read_digest_data(digest_path)
    stored_symbols = set(digest_data.get("symbols", []))

    if not stored_symbols and not current_symbols:
        print("Auto-increment: No public API (`__all__`) found. Defaulting to 'patch'.")
        return "patch"

    removed_symbols = stored_symbols - current_symbols
    added_symbols = current_symbols - stored_symbols

    if removed_symbols:
        print(
            f"Auto-increment: Detected breaking change (removed: {', '.join(sorted(removed_symbols))}). Bumping 'major'."
        )
        return "major"

    if added_symbols:
        print(
            f"Auto-increment: Detected new features (added: {', '.join(sorted(added_symbols))}). Bumping 'minor'."
        )
        return "minor"

    print("Auto-increment: No public API changes detected. Bumping 'patch'.")
    return "patch"
```
## File: __about__.py
```python
"""Metadata for jiggle_version."""

__all__ = [
    "__title__",
    "__version__",
    "__description__",
    "__readme__",
    "__keywords__",
    "__license__",
    "__requires_python__",
    "__status__",
]

__title__ = "jiggle_version"
__version__ = "2.1.0"
__description__ = "Increment version number found in source code without regex"
__readme__ = "README.md"
__keywords__ = ["version", "version-numbers"]
__license__ = "MIT"
__requires_python__ = ">=3.8"
__status__ = "3 - Alpha"
```
## File: schemes.py
```python
# jiggle_version/schemes.py
"""
Implements the version bumping logic for different versioning schemes.
"""
from __future__ import annotations

from packaging.version import InvalidVersion, Version


def bump_pep440(version_string: str, increment: str) -> str:
    """
    Bumps a version string that follows PEP 440.

    Args:
        version_string: The current version string (e.g., "1.2.3.rc1").
        increment: The part to increment ('major', 'minor', 'patch').

    Returns:
        The new version string.
    """
    try:
        v = Version(version_string)
        major, minor, patch = (
            v.release[0],
            v.release[1] if len(v.release) > 1 else 0,
            v.release[2] if len(v.release) > 2 else 0,
        )

        if increment == "major":
            major += 1
            minor = 0
            patch = 0
        elif increment == "minor":
            minor += 1
            patch = 0
        elif increment == "patch":
            patch += 1

        # By default, pre-release, dev, and post-release tags are dropped on a standard bump.
        return f"{major}.{minor}.{patch}"

    except (InvalidVersion, IndexError):
        raise ValueError(f"'{version_string}' is not a valid PEP 440 version.")


def bump_semver(version_string: str, increment: str) -> str:
    """
    Bumps a version string that follows SemVer 2.0.0.

    Args:
        version_string: The current version string (e.g., "1.2.3-alpha.1").
        increment: The part to increment ('major', 'minor', 'patch').

    Returns:
        The new version string.
    """
    # SemVer can have pre-release tags, which we strip for a standard bump.
    main_version = version_string.split("-")[0].split("+")[0]

    try:
        parts = [int(p) for p in main_version.split(".")]
        if len(parts) != 3:
            raise ValueError("SemVer requires a MAJOR.MINOR.PATCH structure.")

        major, minor, patch = parts

        if increment == "major":
            major += 1
            minor = 0
            patch = 0
        elif increment == "minor":
            minor += 1
            patch = 0
        elif increment == "patch":
            patch += 1

        return f"{major}.{minor}.{patch}"

    except (ValueError, IndexError):
        raise ValueError(f"'{version_string}' is not a valid SemVer string.")
```
## File: bump.py
```python
# jiggle_version/bump.py
"""
Main controller for bumping a version string.
"""
from __future__ import annotations

from .schemes import bump_pep440, bump_semver


def bump_version(version_string: str, increment: str, scheme: str = "pep440") -> str:
    """
    Dispatches to the correct bumping function based on the scheme.

    Args:
        version_string: The current version string.
        increment: The part to increment ('major', 'minor', 'patch').
        scheme: The versioning scheme ('pep440' or 'semver').

    Returns:
        The new, bumped version string.
    """
    if scheme == "pep440":
        return bump_pep440(version_string, increment)
    if scheme == "semver":
        return bump_semver(version_string, increment)

    raise ValueError(f"Unknown versioning scheme: '{scheme}'")
```
## File: __main__.py
```python
"""
jiggle_version: deterministic CLI for discovering, checking, and bumping Python project versions.

This version is DEBUG-INSTRUMENTED. All original comments are preserved and
augmented with logging at DEBUG/INFO/WARNING/ERROR levels to trace execution,
argument parsing, config precedence, and failure points.

Key changes vs. your draft:
- SAFE two‑stage parsing: extract --config with a tiny pre‑parser ONLY.
  (Avoids early SystemExit from the full parser swallowing subparser state.)
- Subparsers now have dest="command" and required=True for explicit routing.
- Defaults application: hardcoded < config file < CLI — applied only to `bump`.
- Guard parse_known_args / parse_args with try/except SystemExit to log.
- Added verbose-driven logging setup ("-v" repeatable) and --log-level override.
- Handle `auto` increment exactly once; pass `ignore` consistently.
- More explicit warnings/errors around common edge cases.
- Keep ALL existing comments and behavior where not explicitly adjusted.
"""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from rich_argparse import RichHelpFormatter

# Project imports
from jiggle_version import __about__, git
from jiggle_version.auto import (
    determine_auto_increment,
    get_current_symbols,
    write_digest_data,
)
from jiggle_version.bump import bump_version
from jiggle_version.config import load_config_from_path
from jiggle_version.discover import find_source_files
from jiggle_version.parsers.ast_parser import parse_python_module, parse_setup_py
from jiggle_version.parsers.config_parser import parse_pyproject_toml, parse_setup_cfg
from jiggle_version.pypi import (
    UnpublishedVersionError,
    check_pypi_publication,
    get_package_name,
)
from jiggle_version.update import (
    update_pyproject_toml,
    update_python_file,
    update_setup_cfg,
)
from jiggle_version.utils.cli_suggestions import SmartParser
from jiggle_version.utils.logging_config import configure_logging


class CustomFormatter(RichHelpFormatter):
    """Custom help formatter to tweak the aesthetics."""

    RichHelpFormatter.styles["argparse.args"] = "cyan"
    RichHelpFormatter.styles["argparse.groups"] = "magenta"
    RichHelpFormatter.styles["argparse.help"] = "default"


# ----------------------------------------------------------------------------
# Logging utilities
# ----------------------------------------------------------------------------
LOGGER = logging.getLogger(__name__)

# ----------------------------------------------------------------------------
# Command handlers (augmented with logging)
# ----------------------------------------------------------------------------


# It's not you, it's me, probably
UNEXPECTED_ERROR = 1
DISCOVERY_ERROR = 2
AUTOINCREMENT_ERROR = 3
VERSION_BUMP_ERROR = 4
FILE_UPDATE_ERROR = 5
AUTOGIT_ERROR = 6
HASH_ERROR = 7
ARGPARSE_ERROR = 8

# It's not me, it's you, probably
NO_VERSION_FOUND = 100
VERSION_DISAGREEMENT = 102
DIRTY_GIT_REPO = 103
NO_CONFIG_FOUND = 104
PYPI_CHECK_FAILED = 105


def handle_check(args: argparse.Namespace) -> int:
    """Handler for the 'check' command."""
    LOGGER.info("Running check… project_root=%s", args.project_root)

    project_root = Path(args.project_root)
    found_versions = []

    # Map specific filenames to their specialized parsers.
    # Any other .py file will use the generic module parser.
    parser_map = {
        "pyproject.toml": parse_pyproject_toml,
        "setup.cfg": parse_setup_cfg,
        "setup.py": parse_setup_py,
    }

    # 1. Discover all potential source files
    try:
        source_files = find_source_files(project_root, args.ignore)
    except Exception as e:
        LOGGER.error("Discovery failed: %s", e, exc_info=args.verbose > 0)
        print(f"❌ Discovery failed: {e}", file=sys.stderr)
        return DISCOVERY_ERROR

    print(f"Found {len(source_files)} potential source file(s).")
    LOGGER.debug("Discovered files: %s", [str(p) for p in source_files])

    # 2. Parse each discovered file
    for file_path in source_files:
        relative_path = file_path.relative_to(project_root)
        print(f"-> Checking for version in '{relative_path}'…")

        # Choose the correct parser for the file
        parser_func = parser_map.get(file_path.name, parse_python_module)

        if file_path.suffix == ".py" and file_path.name not in parser_map:
            parser_func = parse_python_module
        elif file_path.name not in parser_map:
            # Skip unknown file types
            LOGGER.debug("Skipping non‑version file: %s", file_path)
            continue

        try:
            version = parser_func(file_path)
        except Exception as e:
            LOGGER.warning(
                "Failed to parse %s: %s", file_path, e, exc_info=args.verbose > 1
            )
            print(f"⚪ Parse failed for {relative_path}: {e}")
            continue

        if version:
            print(f"✅ Found version: {version}")
            found_versions.append({"source": str(relative_path), "version": version})
        else:
            print("⚪ No version found.")

    print("\n--- Discovery Summary ---")
    if not found_versions:
        print("❌ No version declarations were found.")
        LOGGER.error("No version declarations found in project.")
        return NO_VERSION_FOUND

    for item in found_versions:
        print(f"Source: {item['source']:<25} Version: {item['version']}")

    print("\n--- Agreement Check ---")

    # TODO: Add scheme-based normalization (PEP 440, SemVer) before comparison.
    unique_versions = set(item["version"] for item in found_versions)

    if len(unique_versions) > 1:
        print(
            f"❌ Version conflict detected! Found {len(unique_versions)} different versions:"
        )
        for v in sorted(list(unique_versions)):
            print(f"  - {v}")
        LOGGER.error("Version conflict: %s", sorted(unique_versions))
        return VERSION_DISAGREEMENT  # Exit code 2 for disagreement

    print("✅ All discovered versions are in agreement.")

    return 0


def handle_bump(args: argparse.Namespace) -> int:
    """Handler for the 'bump' command."""
    LOGGER.info(
        "Running bump… increment=%s scheme=%s dry_run=%s autogit=%s",
        args.increment,
        args.scheme,
        args.dry_run,
        args.autogit,
    )

    # --- 1. Discover and check for agreement (similar to 'check' command) ---
    project_root = Path(args.project_root)

    if args.autogit != "off":
        try:
            if git.is_repo_dirty(project_root) and not args.allow_dirty:
                LOGGER.error("Git repository dirty and --allow-dirty not set.")
                print(
                    "❌ Git repository is dirty. Use --allow-dirty to proceed.",
                    file=sys.stderr,
                )
                return DIRTY_GIT_REPO
        except Exception as e:
            LOGGER.warning(
                "Failed to check repo dirtiness: %s", e, exc_info=args.verbose > 1
            )

    # --- Determine increment (normalize once) ---
    increment = args.increment
    digest_path = Path(args.project_root) / ".jiggle_version.config"

    if increment == "auto":
        try:
            increment = determine_auto_increment(project_root, digest_path, args.ignore)
            LOGGER.debug("Auto increment resolved to: %s", increment)
        except Exception as e:
            LOGGER.error(
                "Auto-increment analysis failed: %s", e, exc_info=args.verbose > 0
            )
            print(f"❌ Error during auto-increment analysis: {e}", file=sys.stderr)
            return AUTOINCREMENT_ERROR

    found_versions: list[str] = []
    parser_map = {
        "pyproject.toml": parse_pyproject_toml,
        "setup.cfg": parse_setup_cfg,
        "setup.py": parse_setup_py,
    }

    try:
        source_files = find_source_files(project_root, args.ignore)
    except Exception as e:
        LOGGER.error("Discovery failed: %s", e, exc_info=args.verbose > 0)
        print(f"❌ Discovery failed: {e}", file=sys.stderr)
        return DISCOVERY_ERROR

    source_files_with_versions: list[Path] = []
    for file_path in source_files:
        parser_func = parser_map.get(file_path.name, parse_python_module)
        try:
            version = parser_func(file_path)
        except Exception as e:
            LOGGER.warning(
                "Parsing error in %s: %s", file_path, e, exc_info=args.verbose > 1
            )
            continue
        if version:
            found_versions.append(version)
            source_files_with_versions.append(file_path)

    if not found_versions:
        LOGGER.error("No version declarations found to bump.")
        print("❌ No version declarations found to bump.")
        return NO_VERSION_FOUND

    unique_versions = set(found_versions)
    if len(unique_versions) > 1 and not args.force_write:
        LOGGER.error(
            "Version conflict prevents bump. versions=%s", sorted(unique_versions)
        )
        print(
            f"❌ Version conflict detected! Cannot bump. Found: {', '.join(sorted(unique_versions))}"
        )
        return VERSION_DISAGREEMENT

    current_version = (
        unique_versions.pop() if len(unique_versions) == 1 else found_versions[0]
    )
    print(f"Current version: {current_version}")

    # --- 2. Calculate the new version ---
    try:
        target_version = (
            args.set_version
            if args.set_version
            else bump_version(current_version, increment, args.scheme)
        )
        print(f"New version:     {target_version}")
        LOGGER.debug(
            "Bump result: %s -> %s [scheme=%s, inc=%s]",
            current_version,
            target_version,
            args.scheme,
            increment,
        )
    except ValueError as e:
        LOGGER.error("Version bump failed: %s", e, exc_info=args.verbose > 0)
        print(f"❌ Error bumping version: {e}", file=sys.stderr)
        return VERSION_BUMP_ERROR

    # --- 2.5. PyPI Publication Pre-flight Check ---
    if not args.no_check_pypi and not args.dry_run:
        try:
            package_name = get_package_name(project_root)
            if package_name:
                print("\nConducting PyPI publication check…")
                check_pypi_publication(
                    package_name=package_name,
                    current_version=current_version,
                    new_version=target_version,
                    # >>> PASS THE CONFIG PATH
                    config_path=digest_path,
                )
            else:
                LOGGER.info("Skipping PyPI check: no package name in pyproject.toml.")
                print(
                    "\n⚪ Skipping PyPI check: could not find [project].name in pyproject.toml."
                )
        except UnpublishedVersionError as e:
            LOGGER.error("PyPI pre-flight check failed: %s", e)
            print(f"\n❌ {e}", file=sys.stderr)
            # >>> MORE HELPFUL HINT
            print(
                "Hint: If this is a private package, use --no-check-pypi to bypass this check.",
                file=sys.stderr,
            )
            return PYPI_CHECK_FAILED
        except Exception as e:
            # Catch other potential errors like network issues
            LOGGER.warning(
                "PyPI check could not complete: %s", e, exc_info=args.verbose > 1
            )
            print(f"\n🟡 Warning: Could not complete PyPI check: {e}", file=sys.stderr)

    # --- 3. Write changes ---
    if args.dry_run:
        print("\n--dry-run enabled, no files will be changed.")
    else:
        print("\nUpdating files…")
        updater_map = {
            "pyproject.toml": update_pyproject_toml,
            "setup.cfg": update_setup_cfg,
            "setup.py": update_python_file,
        }
        for file_path in source_files_with_versions:
            relative_path = file_path.relative_to(project_root)
            updater_func = updater_map.get(file_path.name, update_python_file)
            try:
                updater_func(file_path, target_version)
                print(f"✅ Updated {relative_path}")
            except Exception as e:
                LOGGER.error(
                    "Failed to update %s: %s", file_path, e, exc_info=args.verbose > 0
                )
                print(f"❌ Failed to update {relative_path}: {e}", file=sys.stderr)
                return FILE_UPDATE_ERROR
        if args.increment == "auto":
            print("\nUpdating API digest file…")
            try:
                current_symbols = get_current_symbols(project_root, args.ignore)
                write_digest_data(digest_path, current_symbols)
                print("✅ Updated .jiggle_version.config")
            except Exception as e:
                LOGGER.warning(
                    "Failed updating digest: %s", e, exc_info=args.verbose > 0
                )

    # --- 4. Autogit ---
    if args.autogit != "off" and not args.dry_run:
        print("\nRunning autogit…")
        try:
            # Stage
            if args.autogit in ["stage", "commit", "push"]:
                print(f"Staging {len(source_files_with_versions)} file(s)…")
                git.stage_files(project_root, source_files_with_versions)
                print("✅ Files staged.")

            # Commit
            if args.autogit in ["commit", "push"]:
                commit_message = args.commit_message.format(
                    version=target_version, scheme=args.scheme, increment=increment
                )
                print(f"Committing with message: '{commit_message}'…")
                git.commit_changes(project_root, commit_message)
                print("✅ Changes committed.")

            # Push
            if args.autogit == "push":
                current_branch = git.get_current_branch(project_root)
                remote = "origin"  # Default from PEP
                print(f"Pushing to {remote}/{current_branch}…")
                git.push_changes(project_root, remote, current_branch)
                print("✅ Changes pushed.")

        except (RuntimeError, subprocess.CalledProcessError) as e:
            LOGGER.error("Autogit failed: %s", e, exc_info=args.verbose > 0)
            print(f"❌ Autogit failed: {e}", file=sys.stderr)
            return AUTOGIT_ERROR

    elif args.autogit != "off" and args.dry_run:
        print(f"\n--dry-run enabled, skipping autogit '{args.autogit}'.")

    return 0


def handle_print(args: argparse.Namespace) -> int:
    """Handler for the 'print' command."""
    LOGGER.info("Running print… project_root=%s", args.project_root)
    project_root = Path(args.project_root)
    found_versions = []
    parser_map = {
        "pyproject.toml": parse_pyproject_toml,
        "setup.cfg": parse_setup_cfg,
        "setup.py": parse_setup_py,
    }
    # Pass the ignore argument to the discovery function
    try:
        source_files = find_source_files(project_root, args.ignore)
    except Exception as e:
        LOGGER.error("Discovery failed: %s", e, exc_info=args.verbose > 0)
        print(f"Error: Discovery failed: {e}", file=sys.stderr)
        return DISCOVERY_ERROR

    for file_path in source_files:
        parser_func = parser_map.get(file_path.name, parse_python_module)
        try:
            version = parser_func(file_path)
        except Exception as e:
            LOGGER.warning(
                "Parse failed for %s: %s", file_path, e, exc_info=args.verbose > 1
            )
            continue
        if version:
            found_versions.append(
                {"source": str(file_path.relative_to(project_root)), "version": version}
            )
    if not found_versions:
        LOGGER.error("No version found for print.")
        print("Error: No version found.", file=sys.stderr)
        return NO_VERSION_FOUND
    unique_versions = set(item["version"] for item in found_versions)
    if len(unique_versions) > 1:
        LOGGER.error("Version conflict on print: %s", sorted(unique_versions))
        print(
            f"Error: Version conflict detected. Found: {', '.join(sorted(unique_versions))}",
            file=sys.stderr,
        )
        return VERSION_DISAGREEMENT
    print(unique_versions.pop())
    return 0


def handle_inspect(args: argparse.Namespace) -> int:
    """Handler for the 'inspect' command."""
    LOGGER.info("Running inspect… project_root=%s", args.project_root)
    project_root = Path(args.project_root)
    print(f"Inspecting project at: {project_root.resolve()}")
    # Pass the ignore argument to the discovery function
    try:
        source_files = find_source_files(project_root, args.ignore)
    except Exception as e:
        LOGGER.error("Discovery failed: %s", e, exc_info=args.verbose > 0)
        print(f"Error: Discovery failed: {e}", file=sys.stderr)
        return DISCOVERY_ERROR

    print(f"\nFound {len(source_files)} potential source file(s):")
    for file in source_files:
        print(f"  - {file.relative_to(project_root)}")
    handle_check(args)
    return 0


def handle_hash_all(args: argparse.Namespace) -> int:
    """Handler for the 'hash-all' command."""
    LOGGER.info("Running hash-all… project_root=%s", args.project_root)
    project_root = Path(args.project_root)
    digest_path = project_root / ".jiggle_version.config"

    try:
        print("Discovering public API symbols (`__all__`)…")
        # Note: auto-increment's discovery also needs to be aware of ignores.
        # This is handled inside get_current_symbols by calling find_source_files.
        current_symbols = get_current_symbols(project_root, args.ignore)
        write_digest_data(digest_path, current_symbols)
        print(f"✅ Successfully wrote {len(current_symbols)} symbols to {digest_path}")
        return 0
    except Exception as e:
        LOGGER.error("hash-all failed: %s", e, exc_info=args.verbose > 0)
        print(f"❌ Failed to generate digest file: {e}", file=sys.stderr)
        return HASH_ERROR


def handle_init(args: argparse.Namespace) -> int:
    """Handler for the 'init' command."""
    LOGGER.info("Running init… project_root=%s", args.project_root)
    pyproject_path = Path(args.project_root) / "pyproject.toml"
    if not pyproject_path.is_file():
        LOGGER.error("pyproject.toml not found: %s", pyproject_path)
        print(f"Error: pyproject.toml not found at {pyproject_path}", file=sys.stderr)
        return NO_CONFIG_FOUND
    config_str = pyproject_path.read_text(encoding="utf-8")
    if "[tool.jiggle_version]" in config_str:
        print("jiggle_version config already exists in pyproject.toml.")
        return 0

    default_config = """
[tool.jiggle_version]
scheme = "pep440"
default_increment = "patch"
# ignore = ["docs/generated", "build/"] # Example
"""
    with open(pyproject_path, "a", encoding="utf-8") as f:
        f.write(default_config)
    print("✅ Added default [tool.jiggle_version] section to pyproject.toml.")
    return 0


# ----------------------------------------------------------------------------
# Parser construction
# ----------------------------------------------------------------------------

# --- New: isolated bump subparser factory (from-scratch) ---


def build_bump_subparser(
    subparsers: argparse._SubParsersAction,
) -> argparse.ArgumentParser:
    """Define only the `bump` subcommand args here, cleanly and testably.

    IMPORTANT: Do **not** bake config-derived defaults here. We parse first,
    then load pyproject.toml, then *override* selected fields from config.
    This keeps precedence explicit: CONFIG > CLI > hardcoded fallback.
    """
    p = subparsers.add_parser("bump", help="Bump the project version.")
    p.add_argument(
        "--increment",
        choices=["major", "minor", "patch", "auto"],
        help="Version part to increment.",
    )
    p.add_argument(
        "--scheme",
        choices=["pep440", "semver"],
        help="Versioning scheme.",
    )
    p.add_argument(
        "--dry-run", action="store_true", help="Simulate without writing files."
    )
    p.add_argument(
        "--set",
        dest="set_version",
        type=str,
        default="",
        help="Set an explicit version.",
    )
    p.add_argument(
        "--force-write",
        action="store_true",
        default=False,
        help="Write even on disagreement.",
    )

    p.add_argument(
        "--no-check-pypi",
        action="store_true",
        default=False,
        help="Disable the pre-flight check against pypi.org.",
    )

    # Autogit group (all optional; config may override later)
    g = p.add_argument_group("autogit options")
    g.add_argument(
        "--autogit",
        choices=["off", "stage", "commit", "push"],
        default="off",
        help="Automatically stage/commit/push changes.",
    )
    g.add_argument(
        "--commit-message",
        type=str,
        default="Release: {version}",
        help="Commit message template.",
    )
    g.add_argument(
        "--allow-dirty",
        action="store_true",
        default=False,
        help="Allow autogit even if repo has uncommitted changes.",
    )

    p.set_defaults(func=handle_bump)
    return p


def _build_parser(
    config_defaults: dict[str, str], use_smart: bool = True
) -> tuple[argparse.ArgumentParser, argparse._SubParsersAction]:
    """Construct the main parser. `config_defaults` no longer affects construction.

    We apply config late after initial parse to know the correct --config path.
    """
    ParserClass = SmartParser if use_smart else argparse.ArgumentParser
    parser = ParserClass(
        prog="jiggle_version",
        description="A safe, zero-import, config-first version bumper.",
        formatter_class=CustomFormatter,
        add_help=False,
    )
    try:
        parser.register("action", "parsers", argparse._SubParsersAction)
    except Exception:
        LOGGER.debug(
            "Parser register(action=parsers) not supported on this parser class."
        )

    # Global/basic options
    parser.add_argument("-h", "--help", action="help", help="Show help and exit")
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__about__.__version__}"
    )
    parser.add_argument(
        "--config", default="pyproject.toml", help="Path to configuration file"
    )

    # Common options for all commands
    parser.add_argument(
        "--ignore", nargs="+", help="Relative paths to ignore during discovery."
    )
    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="Increase verbosity level"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Explicit log level (overrides -v)",
    )
    parser.add_argument(
        "--project-root", type=str, default=".", help="Project root directory"
    )
    parser.add_argument(
        "--no-color", action="store_true", help="Disable colored output"
    )

    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Sub-commands"
    )

    # check
    parser_check = subparsers.add_parser(
        "check", help="Check that discovered version declarations agree."
    )
    parser_check.set_defaults(func=handle_check)

    # bump (built via dedicated function)
    build_bump_subparser(subparsers)

    # print
    parser_print = subparsers.add_parser(
        "print", help="Print the discovered normalized project version."
    )
    parser_print.set_defaults(func=handle_print)

    # inspect
    parser_inspect = subparsers.add_parser(
        "inspect", help="Show a detailed report of discovered version sources."
    )
    parser_inspect.set_defaults(func=handle_inspect)

    # hash-all
    parser_hash_all = subparsers.add_parser(
        "hash-all", help="Compute and store __all__ digests without bumping."
    )
    parser_hash_all.set_defaults(func=handle_hash_all)

    # init
    parser_init = subparsers.add_parser(
        "init", help="Create default [tool.jiggle_version] config in pyproject.toml."
    )
    parser_init.set_defaults(func=handle_init)

    return parser, subparsers


# ----------------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------------

# --- New: late override helper for bump ---

BUMP_OVERRIDES = {
    # config key -> attr name on args
    "increment": "increment",
    "scheme": "scheme",
    "autogit": "autogit",
    "commit_message": "commit_message",
    "allow_dirty": "allow_dirty",
    # You can add more if you support them in config later:
    # "force_write": "force_write",
    # "set_version": "set_version",
}


def apply_global_overrides(args: argparse.Namespace, cfg: dict[str, Any]) -> None:
    """
    Apply config-derived settings that should affect all commands.
    CLI takes precedence; we only fill when args are empty/None.
    """
    # ignore: fill from config if CLI didn't set it
    if (getattr(args, "ignore", None) in (None, [])) and isinstance(
        cfg.get("ignore"), list
    ):
        args.ignore = [str(p) for p in cfg["ignore"]]
        LOGGER.debug("Override: ignore -> %r (from config)", args.ignore)

    # Optional: allow config to set project_root if user didn't change it
    if getattr(args, "project_root", None) in (None, ".") and isinstance(
        cfg.get("project_root"), str
    ):
        args.project_root = cfg["project_root"]
        LOGGER.debug("Override: project_root -> %r (from config)", args.project_root)


def apply_bump_overrides(args: argparse.Namespace, cfg: dict[str, str]) -> None:
    """Apply config-overrides to bump args *after* parsing CLI.

    Precedence requested by user: CONFIG > CLI > hardcoded fallback.
    We also supply hardcoded fallbacks when both are None.
    """
    if not hasattr(args, "command"):
        return
    if args.command != "bump":
        return
    # Normalize: config loader already maps default_increment->increment.
    for k, attr in BUMP_OVERRIDES.items():
        if k in cfg and cfg[k] not in (None, ""):
            old = getattr(args, attr, None)
            setattr(args, attr, cfg[k])
            LOGGER.debug("Override: %s: %r -> %r (from config)", attr, old, cfg[k])

    # Hardcoded fallbacks
    if getattr(args, "increment", None) in (None, ""):
        setattr(args, "increment", "patch")
    if getattr(args, "scheme", None) in (None, ""):
        setattr(args, "scheme", "pep440")
    if getattr(args, "autogit", None) in (None, ""):
        setattr(args, "autogit", "off")


def main(argv: Sequence[str] | None = None) -> int:
    """Main CLI entry point."""
    cli_args = sys.argv[1:] if argv is None else list(argv)

    # 0) Pre-parse ONLY --config using a minimal parser to avoid early exits
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("--config", default="pyproject.toml")
    try:
        pre_ns, _ = pre.parse_known_args(cli_args)
    except SystemExit:
        # Extremely unlikely, but log it.
        print("❌ Early exit while reading --config", file=sys.stderr)
        return ARGPARSE_ERROR

    config_path = Path(pre_ns.config)
    config_from_file = load_config_from_path(config_path)

    apply_global_overrides(pre_ns, config_from_file)
    apply_bump_overrides(pre_ns, config_from_file)

    # 1) Build the full parser (no config defaults baked in)
    parser, _ = _build_parser(config_from_file, use_smart=False)
    apply_global_overrides(pre_ns, config_from_file)

    # 2) Now parse the full CLI safely, logging parse issues
    try:
        args = parser.parse_args(cli_args)
        apply_bump_overrides(args, config_from_file)
        apply_global_overrides(args, config_from_file)
    except SystemExit as _e:
        # Argparse printed help/errors itself; add a debug breadcrumb and exit.
        # sys.stderr.write(f"[DEBUG] argparse SystemExit code={e.code} args={cli_args}")
        return ARGPARSE_ERROR

    # 2.5) Load config (now that we trust --config path) and apply late overrides for bump
    config_from_file = load_config_from_path(Path(args.config))
    apply_bump_overrides(args, config_from_file)

    # 3) Configure logging as early as possible after parse
    configure_logging(args.verbose, args.log_level)
    LOGGER.debug("Parsed args: %s", args)
    LOGGER.debug(
        "Using config file: %s (exists=%s)", str(config_path), config_path.is_file()
    )
    LOGGER.debug(
        "Effective bump defaults (if bump): increment=%s scheme=%s",
        getattr(args, "increment", None),
        getattr(args, "scheme", None),
    )

    # 4) Dispatch
    try:
        if hasattr(args, "func"):
            return args.func(args)
        # This should be unreachable due to required=True
        LOGGER.error("No subcommand handler set; this indicates a parser wiring bug.")
        parser.print_help(sys.stderr)
        return ARGPARSE_ERROR
    except Exception as e:
        # Provide concise error, rich trace only with -vv
        LOGGER.error("Unhandled exception: %s", e, exc_info=args.verbose > 1)
        print(f"An error occurred: {e}", file=sys.stderr)
        return ARGPARSE_ERROR


if __name__ == "__main__":
    sys.exit(main())
```
## File: git.py
```python
# jiggle_version/git.py
"""
Wrappers for executing Git commands via subprocess.
"""
from __future__ import annotations

import shutil
import subprocess  # nosec
from pathlib import Path


def _run_git_command(args: list[str], cwd: Path) -> str:
    """Helper to run a Git command and return its output."""
    if not shutil.which("git"):
        raise RuntimeError(
            "Git command not found. Please ensure Git is installed and in your PATH."
        )

    result = subprocess.run(  # nosec
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,  # Raise an exception if the command fails
    )
    return result.stdout.strip()


def is_repo_dirty(project_root: Path) -> bool:
    """Checks if the Git repository has uncommitted changes."""
    try:
        status_output = _run_git_command(["status", "--porcelain"], project_root)
        return bool(status_output)
    except subprocess.CalledProcessError:
        # This can happen if not in a git repo
        return False


def get_current_branch(project_root: Path) -> str:
    """Gets the current Git branch name."""
    return _run_git_command(["rev-parse", "--abbrev-ref", "HEAD"], project_root)


def stage_files(project_root: Path, files: list[Path]) -> None:
    """Stages the specified files in Git."""
    file_paths = [str(f.relative_to(project_root)) for f in files]
    _run_git_command(["add", *file_paths], project_root)


def commit_changes(project_root: Path, message: str) -> None:
    """Creates a commit with the given message."""
    _run_git_command(["commit", "-m", message], project_root)


def push_changes(project_root: Path, remote: str, branch: str) -> None:
    """Pushes changes to the specified remote and branch."""
    _run_git_command(["push", remote, branch], project_root)
```
## File: discover.py
```python
# jiggle_version/discover.py
"""
Logic for discovering all potential version source files in a project,
while respecting .gitignore and default ignore patterns.
"""
from __future__ import annotations

import logging
from pathlib import Path

# Use the new gitignore API
from .gitignore import (
    collect_default_spec,
    is_path_explicitly_ignored,
    is_path_gitignored,
)

# Files to search for recursively in the project root.
RECURSIVE_SEARCH_FILES = ["_version.py", "__version__.py", "__about__.py"]

# Statically named files to check for in the project root.
STATIC_SEARCH_FILES = ["pyproject.toml", "setup.cfg", "setup.py"]

# Default directories to always ignore.
DEFAULT_IGNORE_DIRS = {".git", ".tox", ".venv", "__pycache__"}

LOGGER = logging.getLogger(__name__)


def find_source_files(
    project_root: Path, ignore_paths: list[str] | None = None
) -> list[Path]:
    """
    Scans a project directory and returns a list of all potential version
    source files, ignoring gitignored and user-specified paths.

    Args:
        project_root: The root directory of the project to scan.
        ignore_paths: A list of relative paths to explicitly ignore.

    Returns:
        A sorted list of Path objects for all found source files.
    """
    LOGGER.debug("project root %s, ignore_paths %s", project_root, ignore_paths)
    found_files: set[Path] = set()

    # Build a single PathSpec with repo/global ignores and any future extras
    spec = collect_default_spec(project_root)

    # Resolve user-provided ignore paths to absolute form for reliable comparison
    explicit_ignore_set = {(project_root / p).resolve() for p in (ignore_paths or [])}

    _walk_and_discover(
        current_dir=project_root,
        project_root=project_root,
        found_files=found_files,
        spec=spec,
        explicit_ignore_set=explicit_ignore_set,
    )

    return sorted(found_files)


def _walk_and_discover(
    *,
    current_dir: Path,
    project_root: Path,
    found_files: set[Path],
    spec,
    explicit_ignore_set: set[Path],
) -> None:
    """Recursively walk directories to find source files."""
    for item in current_dir.iterdir():
        # Check against default, .gitignore (via PathSpec), and user-specified ignore paths
        if (
            item.name in DEFAULT_IGNORE_DIRS
            or is_path_gitignored(item, project_root, spec)
            or is_path_explicitly_ignored(item, explicit_ignore_set)
        ):
            continue

        if item.is_dir():
            # If top-level package dir has __init__.py, include it
            init_file = item / "__init__.py"
            if init_file.is_file() and current_dir == project_root:
                found_files.add(init_file)

            _walk_and_discover(
                current_dir=item,
                project_root=project_root,
                found_files=found_files,
                spec=spec,
                explicit_ignore_set=explicit_ignore_set,
            )

        elif item.is_file():
            # Root-only statics
            if item.name in STATIC_SEARCH_FILES and item.parent == project_root:
                found_files.add(item)
            # Recursive targets
            elif item.name in RECURSIVE_SEARCH_FILES:
                found_files.add(item)
```
## File: config.py
```python
# jiggle_version/config.py
"""
Handles loading and parsing of the [tool.jiggle_version] section
from a pyproject.toml file.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

# For Python < 3.11, we need tomli
if sys.version_info < (3, 11):
    import tomli as tomllib
else:
    import tomllib

LOGGER = logging.getLogger(__name__)


def load_config_from_path(config_path: Path) -> dict[str, Any]:
    """
    Loads configuration from pyproject.toml and returns it as a dictionary.

    Args:
        config_path: The path to the pyproject.toml file.

    Returns:
        A dictionary of configuration values.
    """
    if not config_path.is_file():
        return {}

    try:
        config_data = tomllib.loads(config_path.read_text(encoding="utf-8"))
        jiggle_config: dict[str, Any] = (
            config_data.get("tool", {}).get("jiggle_version", {}) or {}
        )
        if jiggle_config:
            LOGGER.debug("Config found")

        # The config uses 'default_increment', but argparse dest is 'increment'.
        # We'll normalize the key here to make it compatible with argparse.
        if "default_increment" in jiggle_config:
            jiggle_config["increment"] = jiggle_config.pop("default_increment")
            LOGGER.debug(f"increment: {jiggle_config.get('increment')}")

        # >>> ADD THIS: normalize [tool.jiggle_version].ignore to list[str]
        if "ignore" in jiggle_config:
            ig = jiggle_config["ignore"]
            if isinstance(ig, str):
                jiggle_config["ignore"] = [ig]
            elif isinstance(ig, (tuple, set)):
                jiggle_config["ignore"] = list(ig)
            elif not isinstance(ig, list):
                print(
                    "Warning: [tool.jiggle_version].ignore must be a list of paths or a string.",
                    file=sys.stderr,
                )
                jiggle_config.pop("ignore", None)
        # <<< END ADD
        LOGGER.debug(f"ignore: {jiggle_config.get('ignore')}")
        # print(f"ignore: {jiggle_config.get('ignore')}")
        return jiggle_config
    except tomllib.TOMLDecodeError:
        print(
            f"Warning: Could not parse '{config_path}'. Invalid TOML.", file=sys.stderr
        )
        return {}
```
## File: utils/cli_suggestions.py
```python
"""
Smart argument parser with typo suggestions.

This module provides a subclass of `argparse.ArgumentParser` that enhances
the error reporting behavior when users supply invalid choices. If a user
makes a typo in a choice, the parser will suggest the closest matches
based on string similarity.

Example:
    ```python
    import sys

    parser = SmartParser(prog="myapp")
    parser.add_argument("color", choices=["red", "green", "blue"])
    args = parser.parse_args()

    # If the user runs:
    #   myapp gren
    #
    # The output will include:
    #   error: invalid choice: 'gren' (choose from 'red', 'green', 'blue')
    #
    #   Did you mean: green?
    ```
"""

from __future__ import annotations

import argparse
import sys
from difflib import get_close_matches


class SmartParser(argparse.ArgumentParser):
    """Argument parser that suggests similar choices on invalid input.

    This class extends `argparse.ArgumentParser` to provide more helpful
    error messages when the user provides an invalid choice for an argument.
    Instead of only showing the list of valid choices, it also suggests the
    closest matches using fuzzy string matching.

    Example:
        ```python
        parser = SmartParser()
        parser.add_argument("fruit", choices=["apple", "banana", "cherry"])
        args = parser.parse_args()
        ```

    If the user types:
        ```
        myprog bannna
        ```

    The error message will include:
        ```
        Did you mean: banana?
        ```
    """

    def error(self, message: str):
        """Handle parsing errors with suggestions for invalid choices.

        Args:
            message (str): The error message generated by argparse,
                typically when parsing fails (e.g., due to invalid
                choices or syntax errors).

        Side Effects:
            - Prints usage information to `sys.stderr`.
            - Exits the program with status code 2.

        Behavior:
            - If the error message contains an "invalid choice" message,
              attempts to suggest the closest valid alternatives by
              computing string similarity.
            - Otherwise, preserves standard argparse behavior.
        """
        # Detect "invalid choice: 'foo' (choose from ...)"
        if "invalid choice" in message and "choose from" in message:
            bad = message.split("invalid choice:")[1].split("(")[0].strip().strip("'\"")
            choices_str = message.split("choose from")[1]
            choices = [
                c.strip().strip(",)'") for c in choices_str.split() if c.strip(",)")
            ]

            tips = get_close_matches(bad, choices, n=3, cutoff=0.6)
            if tips:
                message += f"\n\nDid you mean: {', '.join(tips)}?"

        self.print_usage(sys.stderr)
        self.exit(2, f"{self.prog}: error: {message}\n")
```
## File: utils/logging_config.py
```python
from __future__ import annotations

import logging
import sys

LOGGER = logging.getLogger(__name__)


def configure_logging(verbosity: int, explicit_level: str | None) -> None:
    """Configure logging based on -v and/or --log-level.

    Precedence: explicit level > verbosity; default INFO.
    -v => INFO, -vv => DEBUG, -vvv => DEBUG with very chatty modules enabled.
    """
    if explicit_level:
        level = getattr(logging, explicit_level.upper(), logging.INFO)
    else:
        level = logging.WARNING
        if verbosity >= 2:
            level = logging.DEBUG
        elif verbosity == 1:
            level = logging.INFO

    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    handler.setFormatter(formatter)

    root = logging.getLogger()
    # Clear any prior handlers if running in REPL/tests
    for h in list(root.handlers):
        root.removeHandler(h)
    root.addHandler(handler)
    root.setLevel(level)

    # Tame noisy libs unless -vvv
    if verbosity < 3 and not explicit_level:
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("tomllib").setLevel(logging.WARNING)

    LOGGER.debug(
        "Logging configured: level=%s verbosity=%s",
        logging.getLevelName(root.level),
        verbosity,
    )
```
## File: parsers/config_parser.py
```python
# jiggle_version/parsers/config_parser.py
"""
Parsers for configuration files like pyproject.toml and setup.cfg.
"""
from __future__ import annotations

import configparser
import sys
from pathlib import Path

# Handle Python < 3.11 needing tomli
if sys.version_info < (3, 11):
    import tomli as tomllib
else:
    import tomllib


def parse_pyproject_toml(file_path: Path) -> str | None:
    """
    Finds and returns the version string from a pyproject.toml file.

    It checks for the version in the following order of priority:
    1. [project].version (PEP 621)
    2. [tool.setuptools].version

    Args:
        file_path: The path to the pyproject.toml file.

    Returns:
        The version string if found, otherwise None.
    """
    if not file_path.is_file():
        return None

    try:
        config = tomllib.loads(file_path.read_text(encoding="utf-8"))

        # 1. Check for PEP 621 project metadata
        if version := config.get("project", {}).get("version"):
            return str(version)

        # 2. Check for setuptools-specific metadata
        if version := config.get("tool", {}).get("setuptools", {}).get("version"):
            return str(version)

    except tomllib.TOMLDecodeError:
        # Handle cases with invalid TOML
        print(f"Warning: Could not parse '{file_path}'. Invalid TOML.", file=sys.stderr)
        return None

    return None


def parse_setup_cfg(file_path: Path) -> str | None:
    """
    Finds and returns the version string from a setup.cfg file.

    It checks for the version in [metadata].version.

    Args:
        file_path: The path to the setup.cfg file.

    Returns:
        The version string if found, otherwise None.
    """
    if not file_path.is_file():
        return None

    try:
        config = configparser.ConfigParser()
        config.read(file_path, encoding="utf-8")
        return config.get("metadata", "version", fallback=None)
    except configparser.Error:
        # Handle cases with invalid INI format
        print(f"Warning: Could not parse '{file_path}'.", file=sys.stderr)
        return None
```
## File: parsers/ast_parser.py
```python
# jiggle_version/parsers/ast_parsers.py
"""
Parsers for Python source files using the `ast` module.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path


class SetupCallVisitor(ast.NodeVisitor):
    """
    An AST visitor that looks for a `setup()` call and extracts literal keyword arguments.
    """

    def __init__(self):
        self.version: str | None = None

    def visit_Call(self, node: ast.Call):
        """Visit a Call node in the AST."""
        # Check if the function being called is `setup`
        is_setup_call = False
        if isinstance(node.func, ast.Name) and node.func.id == "setup":
            is_setup_call = True
        elif isinstance(node.func, ast.Attribute) and node.func.attr == "setup":
            # This handles cases like `setuptools.setup()`
            is_setup_call = True

        if is_setup_call:
            # Find the 'version' keyword argument
            for keyword in node.keywords:
                if keyword.arg == "version":
                    try:
                        # ast.literal_eval is a safe way to get the value of a
                        # node, but it only works for literals (strings, numbers, etc.)
                        # If the version is a variable, this will raise an error.
                        self.version = ast.literal_eval(keyword.value)
                    except ValueError:
                        # The version is not a literal, so we ignore it per the PEP.
                        print(
                            "Warning: Could not statically parse 'version' in setup.py; it is not a literal."
                        )
                    # We found the version keyword, no need to check others
                    break

        # Continue traversing the tree
        self.generic_visit(node)


class VersionVisitor(ast.NodeVisitor):
    """
    An AST visitor that looks for a `__version__ = "..."` assignment.
    """

    def __init__(self):
        self.version: str | None = None

    def visit_Assign(self, node: ast.Assign):
        """Visit an assignment node."""
        # We are looking for a simple assignment: `__version__ = "..."`
        # We only consider assignments with a single target.
        if len(node.targets) == 1:
            target = node.targets[0]
            # Check if the target is a Name node with the id `__version__`
            if isinstance(target, ast.Name) and target.id == "__version__":
                try:
                    self.version = ast.literal_eval(node.value)
                except ValueError:
                    print(
                        "Warning: Found `__version__` but its value was not a literal."
                    )
        self.generic_visit(node)


class AllVisitor(ast.NodeVisitor):
    """An AST visitor that looks for `__all__ = [...]` assignments."""

    def __init__(self):
        self.symbols: set[str] = set()

    def visit_Assign(self, node: ast.Assign):
        if len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and target.id == "__all__":
                try:
                    # Safely evaluate the list/tuple of strings
                    value = ast.literal_eval(node.value)
                    if isinstance(value, (list, tuple)):
                        self.symbols.update(str(s) for s in value)
                except ValueError:
                    print(
                        "Warning: Found `__all__` but its value was not a literal list/tuple."
                    )
        self.generic_visit(node)


def parse_setup_py(file_path: Path) -> str | None:
    """
    Finds and returns the version string from a setup.py file using AST.

    Args:
        file_path: The path to the setup.py file.

    Returns:
        The version string if found as a literal, otherwise None.
    """
    if not file_path.is_file():
        return None

    try:
        source_code = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source_code, filename=str(file_path))

        visitor = SetupCallVisitor()
        visitor.visit(tree)

        return visitor.version
    except (SyntaxError, ValueError) as e:
        print(f"Warning: Could not parse '{file_path}'. Error: {e}", file=sys.stderr)
        return None


def parse_python_module(file_path: Path) -> str | None:
    """
    Finds and returns a `__version__` string from a Python module using AST.

    Args:
        file_path: The path to the Python module file.

    Returns:
        The version string if found as a literal, otherwise None.
    """
    if not file_path.is_file():
        return None

    try:
        source_code = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source_code, filename=str(file_path))

        visitor = VersionVisitor()
        visitor.visit(tree)

        return visitor.version
    except (SyntaxError, ValueError) as e:
        print(f"Warning: Could not parse '{file_path}'. Error: {e}", file=sys.stderr)
        return None


def parse_dunder_all(file_path: Path) -> set[str]:
    """
    Finds and returns a set of symbols from `__all__` in a Python module.
    """
    if not file_path.is_file():
        return set()

    try:
        source_code = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source_code, filename=str(file_path))
        visitor = AllVisitor()
        visitor.visit(tree)
        return visitor.symbols
    except (SyntaxError, ValueError):
        # Ignore files that can't be parsed
        return set()
```
