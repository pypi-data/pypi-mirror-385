"""Documentation build and validation tests."""

import subprocess
from pathlib import Path


def test_docs_build():
    """Verify documentation builds without errors.

    Uses sphinx-build with -W flag to treat warnings as errors,
    ensuring documentation quality.
    """
    result = subprocess.run(
        ["sphinx-build", "-W", "-b", "html", "docs", "docs/_build/html"],
        check=False, capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )
    assert result.returncode == 0, f"Build failed: {result.stderr}"


def test_docs_no_warnings():
    """Verify documentation build produces no warnings.

    Checks that the build output does not contain any warning messages,
    ensuring documentation adheres to quality standards.
    """
    result = subprocess.run(
        ["sphinx-build", "-W", "-b", "html", "docs", "docs/_build/html"],
        check=False, capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )
    assert "warning" not in result.stderr.lower(), f"Warnings detected: {result.stderr}"


def test_all_required_files_exist():
    """Verify all required documentation files exist (MVP phase).

    Ensures that the minimum set of documentation files required for
    the MVP documentation site are present (Phase 1-3 only).
    """
    repo_root = Path(__file__).parent.parent
    # MVP Phase (Phase 1-3): Basic documentation only
    required_files = [
        "docs/index.md",
        "docs/installation.md",
        "docs/quickstart.md",
    ]
    for file_path in required_files:
        full_path = repo_root / file_path
        assert full_path.exists(), f"{file_path} does not exist"
