"""Shared fixtures for tool tests."""

import tempfile
from collections.abc import Generator

import pytest

from clippy.executor import ActionExecutor
from clippy.permissions import PermissionConfig, PermissionManager


@pytest.fixture
def executor() -> ActionExecutor:
    """Create an executor instance."""
    manager = PermissionManager()
    return ActionExecutor(manager)


@pytest.fixture
def executor_direct() -> ActionExecutor:
    """Create an executor instance for direct method access."""
    config = PermissionConfig(
        auto_approve=set(),
        require_approval=set(),
        deny=set(),
    )
    manager = PermissionManager(config)
    return ActionExecutor(manager)


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir
