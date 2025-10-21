from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal, NoReturn, cast, overload

from litestar.di import Provide
from litestar.plugins import CLIPlugin, InitPluginProtocol

from sqlspec.base import SQLSpec
from sqlspec.config import (
    AsyncConfigT,
    AsyncDatabaseConfig,
    DatabaseConfigProtocol,
    DriverT,
    NoPoolAsyncConfig,
    NoPoolSyncConfig,
    SyncConfigT,
    SyncDatabaseConfig,
)
from sqlspec.exceptions import ImproperConfigurationError
from sqlspec.extensions.litestar._utils import get_sqlspec_scope_state, set_sqlspec_scope_state
from sqlspec.extensions.litestar.handlers import (
    autocommit_handler_maker,
    connection_provider_maker,
    lifespan_handler_maker,
    manual_handler_maker,
    pool_provider_maker,
    session_provider_maker,
)
from sqlspec.typing import ConnectionT, PoolT
from sqlspec.utils.logging import get_logger

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable
    from contextlib import AbstractAsyncContextManager

    from litestar import Litestar
    from litestar.config.app import AppConfig
    from litestar.datastructures.state import State
    from litestar.types import BeforeMessageSendHookHandler, Scope
    from rich_click import Group

    from sqlspec.driver import AsyncDriverAdapterBase, SyncDriverAdapterBase
    from sqlspec.loader import SQLFileLoader

logger = get_logger("extensions.litestar")

CommitMode = Literal["manual", "autocommit", "autocommit_include_redirect"]
DEFAULT_COMMIT_MODE: CommitMode = "manual"
DEFAULT_CONNECTION_KEY = "db_connection"
DEFAULT_POOL_KEY = "db_pool"
DEFAULT_SESSION_KEY = "db_session"

__all__ = (
    "DEFAULT_COMMIT_MODE",
    "DEFAULT_CONNECTION_KEY",
    "DEFAULT_POOL_KEY",
    "DEFAULT_SESSION_KEY",
    "CommitMode",
    "SQLSpecPlugin",
)


@dataclass
class _PluginConfigState:
    """Internal state for each database configuration."""

    config: "DatabaseConfigProtocol[Any, Any, Any]"
    connection_key: str
    pool_key: str
    session_key: str
    commit_mode: CommitMode
    extra_commit_statuses: "set[int] | None"
    extra_rollback_statuses: "set[int] | None"
    enable_correlation_middleware: bool
    connection_provider: "Callable[[State, Scope], AsyncGenerator[Any, None]]" = field(init=False)
    pool_provider: "Callable[[State, Scope], Any]" = field(init=False)
    session_provider: "Callable[..., AsyncGenerator[Any, None]]" = field(init=False)
    before_send_handler: "BeforeMessageSendHookHandler" = field(init=False)
    lifespan_handler: "Callable[[Litestar], AbstractAsyncContextManager[None]]" = field(init=False)
    annotation: "type[DatabaseConfigProtocol[Any, Any, Any]]" = field(init=False)


class SQLSpecPlugin(InitPluginProtocol, CLIPlugin):
    """Litestar plugin for SQLSpec database integration.

    Session Table Migrations:
        The Litestar extension includes migrations for creating session storage tables.
        To include these migrations in your database migration workflow, add 'litestar'
        to the include_extensions list in your migration configuration.

    Example:
        config = AsyncpgConfig(
            pool_config={"dsn": "postgresql://localhost/db"},
            extension_config={
                "litestar": {
                    "session_table": "custom_sessions"  # Optional custom table name
                }
            },
            migration_config={
                "script_location": "migrations",
                "include_extensions": ["litestar"],  # Simple string list only
            }
        )

        The session table migration will automatically use the appropriate column types
        for your database dialect (JSONB for PostgreSQL, JSON for MySQL, TEXT for SQLite).

        Extension migrations use the ext_litestar_ prefix (e.g., ext_litestar_0001) to
        prevent version conflicts with application migrations.
    """

    __slots__ = ("_plugin_configs", "_sqlspec")

    def __init__(self, sqlspec: SQLSpec, *, loader: "SQLFileLoader | None" = None) -> None:
        """Initialize SQLSpec plugin.

        Args:
            sqlspec: Pre-configured SQLSpec instance with registered database configs.
            loader: Optional SQL file loader instance (SQLSpec may already have one).
        """
        self._sqlspec = sqlspec

        self._plugin_configs: list[_PluginConfigState] = []
        for cfg in self._sqlspec.configs.values():
            config_union = cast(
                "SyncDatabaseConfig[Any, Any, Any] | NoPoolSyncConfig[Any, Any] | AsyncDatabaseConfig[Any, Any, Any] | NoPoolAsyncConfig[Any, Any]",
                cfg,
            )
            settings = self._extract_litestar_settings(config_union)
            state = self._create_config_state(config_union, settings)
            self._plugin_configs.append(state)

    def _extract_litestar_settings(
        self,
        config: "SyncDatabaseConfig[Any, Any, Any] | NoPoolSyncConfig[Any, Any] | AsyncDatabaseConfig[Any, Any, Any] | NoPoolAsyncConfig[Any, Any]",
    ) -> "dict[str, Any]":
        """Extract Litestar settings from config.extension_config."""
        litestar_config = config.extension_config.get("litestar", {})

        connection_key = litestar_config.get("connection_key", DEFAULT_CONNECTION_KEY)
        pool_key = litestar_config.get("pool_key", DEFAULT_POOL_KEY)
        session_key = litestar_config.get("session_key", DEFAULT_SESSION_KEY)
        commit_mode = litestar_config.get("commit_mode", DEFAULT_COMMIT_MODE)

        if not config.supports_connection_pooling and pool_key == DEFAULT_POOL_KEY:
            pool_key = f"_{DEFAULT_POOL_KEY}_{id(config)}"

        return {
            "connection_key": connection_key,
            "pool_key": pool_key,
            "session_key": session_key,
            "commit_mode": commit_mode,
            "extra_commit_statuses": litestar_config.get("extra_commit_statuses"),
            "extra_rollback_statuses": litestar_config.get("extra_rollback_statuses"),
            "enable_correlation_middleware": litestar_config.get("enable_correlation_middleware", True),
        }

    def _create_config_state(
        self,
        config: "SyncDatabaseConfig[Any, Any, Any] | NoPoolSyncConfig[Any, Any] | AsyncDatabaseConfig[Any, Any, Any] | NoPoolAsyncConfig[Any, Any]",
        settings: "dict[str, Any]",
    ) -> _PluginConfigState:
        """Create plugin state with handlers for the given configuration."""
        state = _PluginConfigState(
            config=config,
            connection_key=settings["connection_key"],
            pool_key=settings["pool_key"],
            session_key=settings["session_key"],
            commit_mode=settings["commit_mode"],
            extra_commit_statuses=settings.get("extra_commit_statuses"),
            extra_rollback_statuses=settings.get("extra_rollback_statuses"),
            enable_correlation_middleware=settings["enable_correlation_middleware"],
        )

        self._setup_handlers(state)
        return state

    def _setup_handlers(self, state: _PluginConfigState) -> None:
        """Setup handlers for the plugin state."""
        connection_key = state.connection_key
        pool_key = state.pool_key
        commit_mode = state.commit_mode
        config = state.config
        is_async = config.is_async

        state.connection_provider = connection_provider_maker(config, pool_key, connection_key)
        state.pool_provider = pool_provider_maker(config, pool_key)
        state.session_provider = session_provider_maker(config, connection_key)
        state.lifespan_handler = lifespan_handler_maker(config, pool_key)

        if commit_mode == "manual":
            state.before_send_handler = manual_handler_maker(connection_key, is_async)
        else:
            commit_on_redirect = commit_mode == "autocommit_include_redirect"
            state.before_send_handler = autocommit_handler_maker(
                connection_key, is_async, commit_on_redirect, state.extra_commit_statuses, state.extra_rollback_statuses
            )

    @property
    def config(
        self,
    ) -> "list[SyncDatabaseConfig[Any, Any, Any] | NoPoolSyncConfig[Any, Any] | AsyncDatabaseConfig[Any, Any, Any] | NoPoolAsyncConfig[Any, Any]]":
        """Return the plugin configurations.

        Returns:
            List of database configurations.
        """
        return [
            cast(
                "SyncDatabaseConfig[Any, Any, Any] | NoPoolSyncConfig[Any, Any] | AsyncDatabaseConfig[Any, Any, Any] | NoPoolAsyncConfig[Any, Any]",
                state.config,
            )
            for state in self._plugin_configs
        ]

    def on_cli_init(self, cli: "Group") -> None:
        """Configure CLI commands for SQLSpec database operations.

        Args:
            cli: The Click command group to add commands to.
        """
        from sqlspec.extensions.litestar.cli import database_group

        cli.add_command(database_group)

    def on_app_init(self, app_config: "AppConfig") -> "AppConfig":
        """Configure Litestar application with SQLSpec database integration.

        Args:
            app_config: The Litestar application configuration instance.

        Returns:
            The updated application configuration instance.
        """
        self._validate_dependency_keys()

        def store_sqlspec_in_state() -> None:
            app_config.state.sqlspec = self

        app_config.on_startup.append(store_sqlspec_in_state)
        app_config.signature_types.extend([SQLSpec, DatabaseConfigProtocol, SyncConfigT, AsyncConfigT])

        signature_namespace = {"ConnectionT": ConnectionT, "PoolT": PoolT, "DriverT": DriverT}

        for state in self._plugin_configs:
            state.annotation = type(state.config)
            app_config.signature_types.append(state.annotation)
            app_config.signature_types.append(state.config.connection_type)
            app_config.signature_types.append(state.config.driver_type)

            signature_namespace.update(state.config.get_signature_namespace())  # type: ignore[arg-type]

            app_config.before_send.append(state.before_send_handler)
            app_config.lifespan.append(state.lifespan_handler)
            app_config.dependencies.update(
                {
                    state.connection_key: Provide(state.connection_provider),
                    state.pool_key: Provide(state.pool_provider),
                    state.session_key: Provide(state.session_provider),
                }
            )

        if signature_namespace:
            app_config.signature_namespace.update(signature_namespace)

        return app_config

    def get_annotations(
        self,
    ) -> "list[type[SyncDatabaseConfig[Any, Any, Any] | NoPoolSyncConfig[Any, Any] | AsyncDatabaseConfig[Any, Any, Any] | NoPoolAsyncConfig[Any, Any]]]":
        """Return the list of annotations.

        Returns:
            List of annotations.
        """
        return [
            cast(
                "type[SyncDatabaseConfig[Any, Any, Any] | NoPoolSyncConfig[Any, Any] | AsyncDatabaseConfig[Any, Any, Any] | NoPoolAsyncConfig[Any, Any]]",
                state.annotation,
            )
            for state in self._plugin_configs
        ]

    def get_annotation(
        self,
        key: "str | SyncDatabaseConfig[Any, Any, Any] | NoPoolSyncConfig[Any, Any] | AsyncDatabaseConfig[Any, Any, Any] | NoPoolAsyncConfig[Any, Any] | type[SyncDatabaseConfig[Any, Any, Any] | NoPoolSyncConfig[Any, Any] | AsyncDatabaseConfig[Any, Any, Any] | NoPoolAsyncConfig[Any, Any]]",
    ) -> "type[SyncDatabaseConfig[Any, Any, Any] | NoPoolSyncConfig[Any, Any] | AsyncDatabaseConfig[Any, Any, Any] | NoPoolAsyncConfig[Any, Any]]":
        """Return the annotation for the given configuration.

        Args:
            key: The configuration instance or key to lookup.

        Raises:
            KeyError: If no configuration is found for the given key.

        Returns:
            The annotation for the configuration.
        """
        for state in self._plugin_configs:
            if key in {state.config, state.annotation} or key in {state.connection_key, state.pool_key}:
                return cast(
                    "type[SyncDatabaseConfig[Any, Any, Any] | NoPoolSyncConfig[Any, Any] | AsyncDatabaseConfig[Any, Any, Any] | NoPoolAsyncConfig[Any, Any]]",
                    state.annotation,
                )

        msg = f"No configuration found for {key}"
        raise KeyError(msg)

    @overload
    def get_config(
        self, name: "type[SyncDatabaseConfig[Any, Any, Any] | NoPoolSyncConfig[Any, Any]]"
    ) -> "SyncDatabaseConfig[Any, Any, Any] | NoPoolSyncConfig[Any, Any]": ...

    @overload
    def get_config(
        self, name: "type[AsyncDatabaseConfig[Any, Any, Any] | NoPoolAsyncConfig[Any, Any]]"
    ) -> "AsyncDatabaseConfig[Any, Any, Any] | NoPoolAsyncConfig[Any, Any]": ...

    @overload
    def get_config(
        self, name: str
    ) -> "SyncDatabaseConfig[Any, Any, Any] | NoPoolSyncConfig[Any, Any] | AsyncDatabaseConfig[Any, Any, Any] | NoPoolAsyncConfig[Any, Any]": ...

    def get_config(
        self, name: "type[DatabaseConfigProtocol[Any, Any, Any]] | str | Any"
    ) -> "DatabaseConfigProtocol[Any, Any, Any]":
        """Get a configuration instance by name.

        Args:
            name: The configuration identifier.

        Raises:
            KeyError: If no configuration is found for the given name.

        Returns:
            The configuration instance for the specified name.
        """
        if isinstance(name, str):
            for state in self._plugin_configs:
                if name in {state.connection_key, state.pool_key, state.session_key}:
                    return cast("DatabaseConfigProtocol[Any, Any, Any]", state.config)  # type: ignore[redundant-cast]

        for state in self._plugin_configs:
            if name in {state.config, state.annotation}:
                return cast("DatabaseConfigProtocol[Any, Any, Any]", state.config)  # type: ignore[redundant-cast]

        msg = f"No database configuration found for name '{name}'. Available keys: {self._get_available_keys()}"
        raise KeyError(msg)

    def provide_request_session(
        self, key: "str | SyncConfigT | AsyncConfigT | type[SyncConfigT | AsyncConfigT]", state: "State", scope: "Scope"
    ) -> "SyncDriverAdapterBase | AsyncDriverAdapterBase":
        """Provide a database session for the specified configuration key from request scope.

        Args:
            key: The configuration identifier (same as get_config).
            state: The Litestar application State object.
            scope: The ASGI scope containing the request context.

        Returns:
            A driver session instance for the specified database configuration.
        """
        plugin_state = self._get_plugin_state(key)
        session_scope_key = f"{plugin_state.session_key}_instance"

        session = get_sqlspec_scope_state(scope, session_scope_key)
        if session is not None:
            return cast("SyncDriverAdapterBase | AsyncDriverAdapterBase", session)

        connection = get_sqlspec_scope_state(scope, plugin_state.connection_key)
        if connection is None:
            self._raise_missing_connection(plugin_state.connection_key)

        session = plugin_state.config.driver_type(
            connection=connection,
            statement_config=plugin_state.config.statement_config,
            driver_features=plugin_state.config.driver_features,
        )
        set_sqlspec_scope_state(scope, session_scope_key, session)

        return cast("SyncDriverAdapterBase | AsyncDriverAdapterBase", session)

    def provide_sync_request_session(
        self, key: "str | SyncConfigT | type[SyncConfigT]", state: "State", scope: "Scope"
    ) -> "SyncDriverAdapterBase":
        """Provide a sync database session for the specified configuration key from request scope.

        Args:
            key: The sync configuration identifier.
            state: The Litestar application State object.
            scope: The ASGI scope containing the request context.

        Returns:
            A sync driver session instance for the specified database configuration.
        """
        session = self.provide_request_session(key, state, scope)
        return cast("SyncDriverAdapterBase", session)

    def provide_async_request_session(
        self, key: "str | AsyncConfigT | type[AsyncConfigT]", state: "State", scope: "Scope"
    ) -> "AsyncDriverAdapterBase":
        """Provide an async database session for the specified configuration key from request scope.

        Args:
            key: The async configuration identifier.
            state: The Litestar application State object.
            scope: The ASGI scope containing the request context.

        Returns:
            An async driver session instance for the specified database configuration.
        """
        session = self.provide_request_session(key, state, scope)
        return cast("AsyncDriverAdapterBase", session)

    def provide_request_connection(
        self, key: "str | SyncConfigT | AsyncConfigT | type[SyncConfigT | AsyncConfigT]", state: "State", scope: "Scope"
    ) -> "Any":
        """Provide a database connection for the specified configuration key from request scope.

        Args:
            key: The configuration identifier (same as get_config).
            state: The Litestar application State object.
            scope: The ASGI scope containing the request context.

        Returns:
            A database connection instance for the specified database configuration.
        """
        plugin_state = self._get_plugin_state(key)
        connection = get_sqlspec_scope_state(scope, plugin_state.connection_key)
        if connection is None:
            self._raise_missing_connection(plugin_state.connection_key)

        return connection

    def _get_plugin_state(
        self, key: "str | SyncConfigT | AsyncConfigT | type[SyncConfigT | AsyncConfigT]"
    ) -> _PluginConfigState:
        """Get plugin state for a configuration by key."""
        if isinstance(key, str):
            for state in self._plugin_configs:
                if key in {state.connection_key, state.pool_key, state.session_key}:
                    return state

        for state in self._plugin_configs:
            if key in {state.config, state.annotation}:
                return state

        self._raise_config_not_found(key)
        return None

    def _get_available_keys(self) -> "list[str]":
        """Get a list of all available configuration keys for error messages."""
        keys = []
        for state in self._plugin_configs:
            keys.extend([state.connection_key, state.pool_key, state.session_key])
        return keys

    def _validate_dependency_keys(self) -> None:
        """Validate that connection and pool keys are unique across configurations."""
        connection_keys = [state.connection_key for state in self._plugin_configs]
        pool_keys = [state.pool_key for state in self._plugin_configs]

        if len(set(connection_keys)) != len(connection_keys):
            self._raise_duplicate_connection_keys()

        if len(set(pool_keys)) != len(pool_keys):
            self._raise_duplicate_pool_keys()

    def _raise_missing_connection(self, connection_key: str) -> None:
        """Raise error when connection is not found in scope."""
        msg = f"No database connection found in scope for key '{connection_key}'. "
        msg += "Ensure the connection dependency is properly configured and available."
        raise ImproperConfigurationError(detail=msg)

    def _raise_config_not_found(self, key: Any) -> NoReturn:
        """Raise error when configuration is not found."""
        msg = f"No database configuration found for name '{key}'. Available keys: {self._get_available_keys()}"
        raise KeyError(msg)

    def _raise_duplicate_connection_keys(self) -> None:
        """Raise error when connection keys are not unique."""
        msg = "When using multiple database configuration, each configuration must have a unique `connection_key`."
        raise ImproperConfigurationError(detail=msg)

    def _raise_duplicate_pool_keys(self) -> None:
        """Raise error when pool keys are not unique."""
        msg = "When using multiple database configuration, each configuration must have a unique `pool_key`."
        raise ImproperConfigurationError(detail=msg)
