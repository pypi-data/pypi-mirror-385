"""Utilities for checking optional dependency availability."""

import re
from importlib.metadata import PackageNotFoundError, distribution, version
from typing import Optional

from packaging.requirements import Requirement
from packaging.version import Version


def _normalize_package_name(name: str) -> str:
    """Normalize package name for comparison (PEP 503).

    Args:
        name: Package name to normalize

    Returns:
        Normalized package name (lowercase, underscores/dashes converted to dashes)
    """
    return re.sub(r"[-_.]+", "-", name).lower()


# Descriptions for optional feature groups
# WARNING: When adding new commands to a group, update the description here
# to keep it in sync with actual available commands
EXTRA_DESCRIPTIONS = {
    "model": "Model operations (init, stage, submit, list)",
    "data": "Data operations (search, download, describe, preview, summary)",
    "benchmarks": "Benchmark operations (run, list, get)",
}

# Mapping of Python import names to PyPI distribution names where they differ
# This is the single source of truth for package name mappings
IMPORT_TO_DIST_MAP = {
    "git": "GitPython",
    "cz_benchmarks": "cz-benchmarks",
    "mypy_boto3_s3": "mypy-boto3-s3",
}

# Reverse mapping: distribution name (normalized) to import name
DIST_TO_IMPORT_MAP = {
    _normalize_package_name(dist): import_name
    for import_name, dist in IMPORT_TO_DIST_MAP.items()
}


def get_install_command(extra_name: str) -> str:
    """Get the pip install command for an optional extra.

    Args:
        extra_name: Name of the extra (e.g., 'model', 'data', 'benchmarks', 'all')

    Returns:
        The pip install command string (e.g., "pip install 'vcp-cli[model]'")
    """
    return f"pip install 'vcp-cli[{extra_name}]'"


def is_package_installed(package_name: str, min_version: Optional[str] = None) -> bool:
    """Check if a package is installed and optionally meets minimum version.

    This uses importlib.metadata which is more reliable than find_spec because:
    1. It checks the actual installed package metadata
    2. It can verify versions
    3. It works even if the package has import issues

    Args:
        package_name: The import name of the package to check (e.g., 'git' for GitPython)
        min_version: Optional minimum version requirement (e.g., '2.0.0')

    Returns:
        True if the package is installed and meets version requirements
    """
    # Use the module-level mapping of import names to distribution names
    dist_name = IMPORT_TO_DIST_MAP.get(package_name, package_name)

    try:
        # Check if the distribution is installed
        distribution(dist_name)

        # If no version requirement, we're done
        if min_version is None:
            return True

        # Check version requirement
        installed_version = version(dist_name)
        return Version(installed_version) >= Version(min_version)

    except PackageNotFoundError:
        # Package not installed
        return False
    except Exception:
        # For any other error (import issues, version parsing, etc.), try a fallback
        # This handles edge cases where metadata exists but is malformed
        try:
            __import__(package_name)
            return True
        except ImportError:
            return False


def get_extra_requirements(extra_name: str) -> list[Requirement]:
    """Get the requirements for a specific extra from vcp-cli metadata.

    Args:
        extra_name: Name of the extra (e.g., 'model', 'data', 'benchmarks')

    Returns:
        List of Requirement objects for the extra
    """
    try:
        dist = distribution("vcp-cli")
        requirements = []

        # Parse the metadata to find requirements for this extra
        if dist.requires:
            for req_string in dist.requires:
                req = Requirement(req_string)
                # Check if this requirement is for the specified extra
                if req.marker and req.marker.evaluate({"extra": extra_name}):
                    requirements.append(req)

        return requirements

    except PackageNotFoundError:
        return []


def check_extra_dependencies(extra_name: str) -> bool:
    """Check if all dependencies for a specific extra are installed.

    This dynamically reads the requirements from the installed package metadata,
    so it always stays in sync with pyproject.toml.

    Args:
        extra_name: Name of the extra to check (e.g., 'model', 'data', 'benchmarks')

    Returns:
        True if all dependencies for the extra are satisfied
    """
    requirements = get_extra_requirements(extra_name)

    if not requirements:
        # No requirements found - either extra doesn't exist or has no deps
        return True

    for req in requirements:
        # Get the package name and version spec
        dist_name = _normalize_package_name(req.name)
        # Use the module-level reverse mapping
        import_name = DIST_TO_IMPORT_MAP.get(dist_name, req.name.replace("-", "_"))

        # Extract minimum version from specifier if present
        min_version = None
        if req.specifier:
            for spec in req.specifier:
                # Handle >=, ~=, ==, etc.
                if spec.operator in (">=", "~=", "=="):
                    min_version = spec.version
                    break

        # Check if the package is installed with the right version
        if not is_package_installed(import_name, min_version):
            return False

    return True


def get_installed_extras() -> set[str]:
    """Detect which optional extras were installed for vcp-cli.

    This provides a more accurate way to determine what features are available
    by checking the actual installation metadata.

    Returns:
        Set of extra names that were installed (e.g., {'model', 'data', 'benchmarks'})
    """
    try:
        # Verify vcp-cli is installed
        distribution("vcp-cli")

        # Check each known extra
        extras = ["model", "data", "benchmarks"]
        installed = set()

        for extra in extras:
            if check_extra_dependencies(extra):
                installed.add(extra)

        return installed

    except PackageNotFoundError:
        return set()
