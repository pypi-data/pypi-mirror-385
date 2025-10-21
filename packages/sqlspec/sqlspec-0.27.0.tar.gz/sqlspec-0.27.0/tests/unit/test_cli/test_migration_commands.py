"""Tests for CLI migration commands functionality."""

import os
import sys
import tempfile
from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from sqlspec.cli import add_migration_commands

if TYPE_CHECKING:
    from unittest.mock import Mock


@pytest.fixture
def cleanup_test_modules() -> Iterator[None]:
    """Fixture to clean up test modules from sys.modules after each test."""
    modules_before = set(sys.modules.keys())
    yield
    # Remove any test modules that were imported during the test
    modules_after = set(sys.modules.keys())
    test_modules = {m for m in modules_after - modules_before if m.startswith("test_config")}
    for module in test_modules:
        if module in sys.modules:
            del sys.modules[module]


def test_show_config_command(cleanup_test_modules: None) -> None:
    """Test show-config command displays migration configurations."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        try:
            config_module = """
from sqlspec.adapters.sqlite.config import SqliteConfig

def get_config():
    config = SqliteConfig(
        bind_key="migration_test",
        pool_config={"database": ":memory:"},
        migration_config={
            "enabled": True,
            "script_location": "migrations"
        }
    )
    return config
"""
            Path("test_config.py").write_text(config_module)

            result = runner.invoke(add_migration_commands(), ["--config", "test_config.get_config", "show-config"])

        finally:
            os.chdir(original_dir)

        assert result.exit_code == 0
        assert "migration_test" in result.output
        assert "Migration Enabled" in result.output or "SqliteConfig" in result.output


def test_show_config_with_multiple_configs(cleanup_test_modules: None) -> None:
    """Test show-config with multiple migration configurations."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        try:
            config_module = """
from sqlspec.adapters.sqlite.config import SqliteConfig
from sqlspec.adapters.duckdb.config import DuckDBConfig

def get_configs():
    sqlite_config = SqliteConfig(
        bind_key="sqlite_migrations",
        pool_config={"database": ":memory:"},
        migration_config={"enabled": True, "script_location": "sqlite_migrations"}
    )

    duckdb_config = DuckDBConfig(
        bind_key="duckdb_migrations",
        pool_config={"database": ":memory:"},
        migration_config={"enabled": True, "script_location": "duckdb_migrations"}
    )

    return [sqlite_config, duckdb_config]
"""
            Path("test_config.py").write_text(config_module)

            result = runner.invoke(add_migration_commands(), ["--config", "test_config.get_configs", "show-config"])

        finally:
            os.chdir(original_dir)

        assert result.exit_code == 0
        assert "sqlite_migrations" in result.output
        assert "duckdb_migrations" in result.output
        assert "2 configuration(s)" in result.output


def test_show_config_no_migrations(cleanup_test_modules: None) -> None:
    """Test show-config when no migrations are configured."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        try:
            config_module = """
from sqlspec.adapters.sqlite.config import SqliteConfig

def get_config():
    # Config without migration_config
    config = SqliteConfig(
        bind_key="no_migrations",
        pool_config={"database": ":memory:"}
    )
    return config
"""
            Path("test_config.py").write_text(config_module)

            result = runner.invoke(add_migration_commands(), ["--config", "test_config.get_config", "show-config"])

        finally:
            os.chdir(original_dir)

        assert result.exit_code == 0
        assert (
            "No configurations with migrations detected" in result.output or "no_migrations" in result.output
        )  # Depends on validation logic


@patch("sqlspec.migrations.commands.create_migration_commands")
def test_show_current_revision_command(mock_create_commands: "Mock", cleanup_test_modules: None) -> None:
    """Test show-current-revision command."""
    runner = CliRunner()

    # Mock the migration commands
    mock_commands = Mock()
    mock_commands.current = Mock(return_value=None)  # Sync function
    mock_create_commands.return_value = mock_commands

    with tempfile.TemporaryDirectory() as temp_dir:
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        try:
            config_module = """
from sqlspec.adapters.sqlite.config import SqliteConfig

def get_config():
    config = SqliteConfig(
        bind_key="revision_test",
        pool_config={"database": ":memory:"},
        migration_config={"enabled": True, "script_location": "migrations"}
    )
    return config
"""
            Path("test_config.py").write_text(config_module)

            result = runner.invoke(
                add_migration_commands(), ["--config", "test_config.get_config", "show-current-revision"]
            )

        finally:
            os.chdir(original_dir)

        assert result.exit_code == 0
        mock_commands.current.assert_called_once_with(verbose=False)


@patch("sqlspec.migrations.commands.create_migration_commands")
def test_show_current_revision_verbose(mock_create_commands: "Mock", cleanup_test_modules: None) -> None:
    """Test show-current-revision command with verbose flag."""
    runner = CliRunner()

    mock_commands = Mock()
    mock_commands.current = Mock(return_value=None)
    mock_create_commands.return_value = mock_commands

    with tempfile.TemporaryDirectory() as temp_dir:
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        try:
            config_module = """
from sqlspec.adapters.sqlite.config import SqliteConfig

def get_config():
    config = SqliteConfig(
        bind_key="verbose_test",
        pool_config={"database": ":memory:"},
        migration_config={"enabled": True}
    )
    return config
"""
            Path("test_config.py").write_text(config_module)

            result = runner.invoke(
                add_migration_commands(), ["--config", "test_config.get_config", "show-current-revision", "--verbose"]
            )

        finally:
            os.chdir(original_dir)

        assert result.exit_code == 0
        mock_commands.current.assert_called_once_with(verbose=True)


@patch("sqlspec.migrations.commands.create_migration_commands")
def test_init_command(mock_create_commands: "Mock", cleanup_test_modules: None) -> None:
    """Test init command for initializing migrations."""
    runner = CliRunner()

    mock_commands = Mock()
    mock_commands.init = Mock(return_value=None)
    mock_create_commands.return_value = mock_commands

    with tempfile.TemporaryDirectory() as temp_dir:
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        try:
            config_module = """
from sqlspec.adapters.sqlite.config import SqliteConfig

def get_config():
    config = SqliteConfig(pool_config={"database": ":memory:"})
    config.bind_key = "init_test"
    config.migration_config = {"script_location": "test_migrations"}
    return config
"""
            Path("test_config.py").write_text(config_module)

            result = runner.invoke(
                add_migration_commands(), ["--config", "test_config.get_config", "init", "--no-prompt"]
            )

        finally:
            os.chdir(original_dir)

        assert result.exit_code == 0
        mock_commands.init.assert_called_once_with(directory="test_migrations", package=True)


@patch("sqlspec.migrations.commands.create_migration_commands")
def test_init_command_custom_directory(mock_create_commands: "Mock", cleanup_test_modules: None) -> None:
    """Test init command with custom directory."""
    runner = CliRunner()

    mock_commands = Mock()
    mock_commands.init = Mock(return_value=None)
    mock_create_commands.return_value = mock_commands

    with tempfile.TemporaryDirectory() as temp_dir:
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        try:
            config_module = """
from sqlspec.adapters.sqlite.config import SqliteConfig

def get_config():
    config = SqliteConfig(pool_config={"database": ":memory:"})
    config.bind_key = "custom_init"
    config.migration_config = {"script_location": "migrations"}
    return config
"""
            Path("test_config.py").write_text(config_module)

            result = runner.invoke(
                add_migration_commands(),
                ["--config", "test_config.get_config", "init", "custom_migrations", "--no-prompt"],
            )

        finally:
            os.chdir(original_dir)

        assert result.exit_code == 0
        mock_commands.init.assert_called_once_with(directory="custom_migrations", package=True)


@patch("sqlspec.migrations.commands.create_migration_commands")
def test_create_migration_command(mock_create_commands: "Mock", cleanup_test_modules: None) -> None:
    """Test create-migration command."""
    runner = CliRunner()

    mock_commands = Mock()
    mock_commands.revision = Mock(return_value=None)
    mock_create_commands.return_value = mock_commands

    with tempfile.TemporaryDirectory() as temp_dir:
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        try:
            config_module = """
from sqlspec.adapters.sqlite.config import SqliteConfig

def get_config():
    config = SqliteConfig(pool_config={"database": ":memory:"})
    config.bind_key = "revision_test"
    config.migration_config = {"enabled": True}
    return config
"""
            Path("test_config.py").write_text(config_module)

            result = runner.invoke(
                add_migration_commands(),
                ["--config", "test_config.get_config", "create-migration", "-m", "test migration", "--no-prompt"],
            )

        finally:
            os.chdir(original_dir)

        assert result.exit_code == 0
        mock_commands.revision.assert_called_once_with(message="test migration")


@patch("sqlspec.migrations.commands.create_migration_commands")
def test_make_migration_alias(mock_create_commands: "Mock", cleanup_test_modules: None) -> None:
    """Test make-migration alias for backward compatibility."""
    runner = CliRunner()

    mock_commands = Mock()
    mock_commands.revision = Mock(return_value=None)
    mock_create_commands.return_value = mock_commands

    with tempfile.TemporaryDirectory() as temp_dir:
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        try:
            config_module = """
from sqlspec.adapters.sqlite.config import SqliteConfig

def get_config():
    config = SqliteConfig(pool_config={"database": ":memory:"})
    config.bind_key = "revision_test"
    config.migration_config = {"enabled": True}
    return config
"""
            Path("test_config.py").write_text(config_module)

            result = runner.invoke(
                add_migration_commands(),
                ["--config", "test_config.get_config", "make-migration", "-m", "test migration", "--no-prompt"],
            )

        finally:
            os.chdir(original_dir)

        assert result.exit_code == 0
        mock_commands.revision.assert_called_once_with(message="test migration")


@patch("sqlspec.migrations.commands.create_migration_commands")
def test_upgrade_command(mock_create_commands: "Mock", cleanup_test_modules: None) -> None:
    """Test upgrade command."""
    runner = CliRunner()

    mock_commands = Mock()
    mock_commands.upgrade = Mock(return_value=None)
    mock_create_commands.return_value = mock_commands

    with tempfile.TemporaryDirectory() as temp_dir:
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        try:
            config_module = """
from sqlspec.adapters.sqlite.config import SqliteConfig

def get_config():
    config = SqliteConfig(pool_config={"database": ":memory:"})
    config.bind_key = "upgrade_test"
    config.migration_config = {"enabled": True}
    return config
"""
            Path("test_config.py").write_text(config_module)

            result = runner.invoke(
                add_migration_commands(), ["--config", "test_config.get_config", "upgrade", "--no-prompt"]
            )

        finally:
            os.chdir(original_dir)

        assert result.exit_code == 0
        mock_commands.upgrade.assert_called_once_with(revision="head", auto_sync=True, dry_run=False)


@patch("sqlspec.migrations.commands.create_migration_commands")
def test_upgrade_command_specific_revision(mock_create_commands: "Mock", cleanup_test_modules: None) -> None:
    """Test upgrade command with specific revision."""
    runner = CliRunner()

    mock_commands = Mock()
    mock_commands.upgrade = Mock(return_value=None)
    mock_create_commands.return_value = mock_commands

    with tempfile.TemporaryDirectory() as temp_dir:
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        try:
            config_module = """
from sqlspec.adapters.sqlite.config import SqliteConfig

def get_config():
    config = SqliteConfig(pool_config={"database": ":memory:"})
    config.bind_key = "upgrade_revision_test"
    config.migration_config = {"enabled": True}
    return config
"""
            Path("test_config.py").write_text(config_module)

            result = runner.invoke(
                add_migration_commands(), ["--config", "test_config.get_config", "upgrade", "abc123", "--no-prompt"]
            )

        finally:
            os.chdir(original_dir)

        assert result.exit_code == 0
        mock_commands.upgrade.assert_called_once_with(revision="abc123", auto_sync=True, dry_run=False)


@patch("sqlspec.migrations.commands.create_migration_commands")
def test_downgrade_command(mock_create_commands: "Mock", cleanup_test_modules: None) -> None:
    """Test downgrade command."""
    runner = CliRunner()

    mock_commands = Mock()
    mock_commands.downgrade = Mock(return_value=None)
    mock_create_commands.return_value = mock_commands

    with tempfile.TemporaryDirectory() as temp_dir:
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        try:
            config_module = """
from sqlspec.adapters.sqlite.config import SqliteConfig

def get_config():
    config = SqliteConfig(pool_config={"database": ":memory:"})
    config.bind_key = "downgrade_test"
    config.migration_config = {"enabled": True}
    return config
"""
            Path("test_config.py").write_text(config_module)

            result = runner.invoke(
                add_migration_commands(), ["--config", "test_config.get_config", "downgrade", "--no-prompt"]
            )

        finally:
            os.chdir(original_dir)

        assert result.exit_code == 0
        mock_commands.downgrade.assert_called_once_with(revision="-1", dry_run=False)


@patch("sqlspec.migrations.commands.create_migration_commands")
def test_stamp_command(mock_create_commands: "Mock", cleanup_test_modules: None) -> None:
    """Test stamp command."""
    runner = CliRunner()

    mock_commands = Mock()
    mock_commands.stamp = Mock(return_value=None)
    mock_create_commands.return_value = mock_commands

    with tempfile.TemporaryDirectory() as temp_dir:
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        try:
            config_module = """
from sqlspec.adapters.sqlite.config import SqliteConfig

def get_config():
    config = SqliteConfig(pool_config={"database": ":memory:"})
    config.bind_key = "stamp_test"
    config.migration_config = {"enabled": True}
    return config
"""
            Path("test_config.py").write_text(config_module)

            result = runner.invoke(add_migration_commands(), ["--config", "test_config.get_config", "stamp", "abc123"])

        finally:
            os.chdir(original_dir)

        assert result.exit_code == 0
        mock_commands.stamp.assert_called_once_with(revision="abc123")


@patch("sqlspec.migrations.commands.create_migration_commands")
def test_multi_config_operations(mock_create_commands: "Mock", cleanup_test_modules: None) -> None:
    """Test multi-configuration operations with include/exclude filters."""
    runner = CliRunner()

    mock_commands = Mock()
    mock_commands.current = Mock(return_value=None)
    mock_create_commands.return_value = mock_commands

    with tempfile.TemporaryDirectory() as temp_dir:
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        try:
            config_module = """
from sqlspec.adapters.sqlite.config import SqliteConfig
from sqlspec.adapters.duckdb.config import DuckDBConfig

def get_configs():
    sqlite_config = SqliteConfig(pool_config={"database": ":memory:"})
    sqlite_config.bind_key = "sqlite_multi"
    sqlite_config.migration_config = {"enabled": True}

    duckdb_config = DuckDBConfig(pool_config={"database": ":memory:"})
    duckdb_config.bind_key = "duckdb_multi"
    duckdb_config.migration_config = {"enabled": True}

    return [sqlite_config, duckdb_config]
"""
            Path("test_config.py").write_text(config_module)

            result = runner.invoke(
                add_migration_commands(),
                ["--config", "test_config.get_configs", "show-current-revision", "--include", "sqlite_multi"],
            )

        finally:
            os.chdir(original_dir)

        assert result.exit_code == 0
        # Should process only the included configuration
        assert "sqlite_multi" in result.output


@patch("sqlspec.migrations.commands.create_migration_commands")
def test_dry_run_operations(mock_create_commands: "Mock", cleanup_test_modules: None) -> None:
    """Test dry-run operations show what would be executed."""
    runner = CliRunner()

    mock_commands = Mock()
    mock_commands.upgrade = Mock(return_value=None)
    mock_create_commands.return_value = mock_commands

    with tempfile.TemporaryDirectory() as temp_dir:
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        try:
            config_module = """
from sqlspec.adapters.sqlite.config import SqliteConfig

def get_configs():
    config1 = SqliteConfig(pool_config={"database": ":memory:"})
    config1.bind_key = "dry_run_test1"
    config1.migration_config = {"enabled": True}

    config2 = SqliteConfig(pool_config={"database": "test.db"})
    config2.bind_key = "dry_run_test2"
    config2.migration_config = {"enabled": True}

    return [config1, config2]
"""
            Path("test_config.py").write_text(config_module)

            result = runner.invoke(
                add_migration_commands(), ["--config", "test_config.get_configs", "upgrade", "--dry-run"]
            )

        finally:
            os.chdir(original_dir)

        assert result.exit_code == 0
        assert "Dry run" in result.output
        assert "Would upgrade" in result.output
        # Should not actually call the upgrade method with dry-run
        mock_commands.upgrade.assert_not_called()


def test_execution_mode_reporting(cleanup_test_modules: None) -> None:
    """Test that execution mode is reported when specified."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        try:
            config_module = """
from sqlspec.adapters.sqlite.config import SqliteConfig

def get_config():
    config = SqliteConfig(pool_config={"database": ":memory:"})
    config.bind_key = "execution_mode_test"
    config.migration_config = {"enabled": True}
    return config
"""
            Path("test_config.py").write_text(config_module)

            with patch("sqlspec.migrations.commands.create_migration_commands") as mock_create:
                mock_commands = Mock()
                mock_commands.upgrade = Mock(return_value=None)
                mock_create.return_value = mock_commands

                result = runner.invoke(
                    add_migration_commands(),
                    ["--config", "test_config.get_config", "upgrade", "--execution-mode", "sync", "--no-prompt"],
                )

        finally:
            os.chdir(original_dir)

        assert result.exit_code == 0
        assert "Execution mode: sync" in result.output


def test_bind_key_filtering_single_config(cleanup_test_modules: None) -> None:
    """Test --bind-key filtering with single config."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        try:
            config_module = """
from sqlspec.adapters.sqlite.config import SqliteConfig

def get_config():
    return SqliteConfig(
        bind_key="target_config",
        pool_config={"database": ":memory:"},
        migration_config={"enabled": True, "script_location": "migrations"}
    )
"""
            Path("test_config.py").write_text(config_module)

            result = runner.invoke(
                add_migration_commands(),
                ["--config", "test_config.get_config", "show-config", "--bind-key", "target_config"],
            )

        finally:
            os.chdir(original_dir)

        assert result.exit_code == 0
        assert "target_config" in result.output


def test_bind_key_filtering_multiple_configs(cleanup_test_modules: None) -> None:
    """Test --bind-key filtering with multiple configs."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        try:
            config_module = """
from sqlspec.adapters.sqlite.config import SqliteConfig
from sqlspec.adapters.duckdb.config import DuckDBConfig

def get_configs():
    sqlite_config = SqliteConfig(
        bind_key="sqlite_db",
        pool_config={"database": ":memory:"},
        migration_config={"enabled": True, "script_location": "sqlite_migrations"}
    )

    duckdb_config = DuckDBConfig(
        bind_key="duckdb_db",
        pool_config={"database": ":memory:"},
        migration_config={"enabled": True, "script_location": "duckdb_migrations"}
    )

    postgres_config = SqliteConfig(
        bind_key="postgres_db",
        pool_config={"database": ":memory:"},
        migration_config={"enabled": True, "script_location": "postgres_migrations"}
    )

    return [sqlite_config, duckdb_config, postgres_config]
"""
            Path("test_config.py").write_text(config_module)

            # Test filtering for sqlite_db only
            result = runner.invoke(
                add_migration_commands(),
                ["--config", "test_config.get_configs", "show-config", "--bind-key", "sqlite_db"],
            )

        finally:
            os.chdir(original_dir)

        assert result.exit_code == 0
        assert "sqlite_db" in result.output
        # Should only show one config, not all three
        assert "Found 1 configuration(s)" in result.output or "sqlite_migrations" in result.output
        assert "duckdb_db" not in result.output
        assert "postgres_db" not in result.output


def test_bind_key_filtering_nonexistent_key(cleanup_test_modules: None) -> None:
    """Test --bind-key filtering with nonexistent bind key."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        try:
            config_module = """
from sqlspec.adapters.sqlite.config import SqliteConfig

def get_configs():
    return [
        SqliteConfig(
            bind_key="existing_config",
            pool_config={"database": ":memory:"},
            migration_config={"enabled": True}
        )
    ]
"""
            Path("test_config.py").write_text(config_module)

            result = runner.invoke(
                add_migration_commands(),
                ["--config", "test_config.get_configs", "show-config", "--bind-key", "nonexistent"],
            )

        finally:
            os.chdir(original_dir)

        assert result.exit_code == 1
        assert "No config found for bind key: nonexistent" in result.output


@patch("sqlspec.migrations.commands.create_migration_commands")
def test_bind_key_filtering_with_migration_commands(mock_create_commands: "Mock", cleanup_test_modules: None) -> None:
    """Test --bind-key filtering works with actual migration commands."""
    runner = CliRunner()

    mock_commands = Mock()
    mock_commands.upgrade = Mock(return_value=None)
    mock_create_commands.return_value = mock_commands

    with tempfile.TemporaryDirectory() as temp_dir:
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        try:
            config_module = """
from sqlspec.adapters.sqlite.config import SqliteConfig
from sqlspec.adapters.duckdb.config import DuckDBConfig

def get_multi_configs():
    return [
        SqliteConfig(
            bind_key="primary_db",
            pool_config={"database": "primary.db"},
            migration_config={"enabled": True, "script_location": "primary_migrations"}
        ),
        DuckDBConfig(
            bind_key="analytics_db",
            pool_config={"database": "analytics.duckdb"},
            migration_config={"enabled": True, "script_location": "analytics_migrations"}
        )
    ]
"""
            Path("test_config.py").write_text(config_module)

            result = runner.invoke(
                add_migration_commands(),
                ["--config", "test_config.get_multi_configs", "upgrade", "--bind-key", "analytics_db", "--no-prompt"],
            )

        finally:
            os.chdir(original_dir)

        assert result.exit_code == 0
        # Should only process the analytics_db config
        mock_commands.upgrade.assert_called_once_with(revision="head", auto_sync=True, dry_run=False)
