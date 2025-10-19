"""Automation sessions for StudentScore."""

from __future__ import annotations

import nox


nox.options.sessions = ("lint", "tests", "check-manifest")
nox.options.reuse_existing_virtualenvs = True

PYTEST_DEFAULTS = (
    "--cov=StudentScore",
    "--cov-report=term",
    "--cov-report=xml",
)


TEST_DEPENDENCIES = (
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "coverage[toml]>=7.11.0",
)


@nox.session
def tests(session: nox.Session) -> None:
    """Run the unit test suite."""
    session.install(".[test]")
    session.install(*TEST_DEPENDENCIES)
    session.run("pytest", *(session.posargs or PYTEST_DEFAULTS))


@nox.session
def lint(session: nox.Session) -> None:
    """Lint the codebase with Ruff."""
    session.install("ruff>=0.5.0")
    session.run("ruff", "check", "StudentScore", "tests")


@nox.session(name="check-manifest")
def check_manifest_session(session: nox.Session) -> None:
    """Verify that MANIFEST.in matches the repository contents."""
    session.install("check-manifest>=0.49")
    session.env["POETRY_DYNAMIC_VERSIONING_BYPASS"] = "1"
    session.run("check-manifest")
