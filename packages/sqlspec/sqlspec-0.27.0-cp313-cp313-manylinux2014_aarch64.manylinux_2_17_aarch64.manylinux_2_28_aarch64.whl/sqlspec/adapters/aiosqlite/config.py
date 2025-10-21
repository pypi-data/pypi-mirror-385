"""Aiosqlite database configuration."""

import logging
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any, ClassVar, TypedDict

from typing_extensions import NotRequired

from sqlspec.adapters.aiosqlite._types import AiosqliteConnection
from sqlspec.adapters.aiosqlite.driver import AiosqliteCursor, AiosqliteDriver, aiosqlite_statement_config
from sqlspec.adapters.aiosqlite.pool import (
    AiosqliteConnectionPool,
    AiosqliteConnectTimeoutError,
    AiosqlitePoolClosedError,
    AiosqlitePoolConnection,
)
from sqlspec.config import AsyncDatabaseConfig
from sqlspec.utils.serializers import from_json, to_json

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable

    from sqlspec.core.statement import StatementConfig

__all__ = ("AiosqliteConfig", "AiosqliteConnectionParams", "AiosqliteDriverFeatures", "AiosqlitePoolParams")

logger = logging.getLogger(__name__)


class AiosqliteConnectionParams(TypedDict):
    """TypedDict for aiosqlite connection parameters."""

    database: NotRequired[str]
    timeout: NotRequired[float]
    detect_types: NotRequired[int]
    isolation_level: NotRequired[str | None]
    check_same_thread: NotRequired[bool]
    cached_statements: NotRequired[int]
    uri: NotRequired[bool]


class AiosqlitePoolParams(AiosqliteConnectionParams):
    """TypedDict for aiosqlite pool parameters, inheriting connection parameters."""

    pool_size: NotRequired[int]
    connect_timeout: NotRequired[float]
    idle_timeout: NotRequired[float]
    operation_timeout: NotRequired[float]
    extra: NotRequired[dict[str, Any]]


class AiosqliteDriverFeatures(TypedDict):
    """Aiosqlite driver feature configuration.

    Controls optional type handling and serialization features for SQLite connections.

    enable_custom_adapters: Enable custom type adapters for JSON/UUID/datetime conversion.
        Defaults to True for enhanced Python type support.
        Set to False only if you need pure SQLite behavior without type conversions.
    json_serializer: Custom JSON serializer function.
        Defaults to sqlspec.utils.serializers.to_json.
    json_deserializer: Custom JSON deserializer function.
        Defaults to sqlspec.utils.serializers.from_json.
    """

    enable_custom_adapters: NotRequired[bool]
    json_serializer: "NotRequired[Callable[[Any], str]]"
    json_deserializer: "NotRequired[Callable[[str], Any]]"


class AiosqliteConfig(AsyncDatabaseConfig["AiosqliteConnection", AiosqliteConnectionPool, AiosqliteDriver]):
    """Database configuration for AioSQLite engine."""

    driver_type: "ClassVar[type[AiosqliteDriver]]" = AiosqliteDriver
    connection_type: "ClassVar[type[AiosqliteConnection]]" = AiosqliteConnection
    supports_transactional_ddl: "ClassVar[bool]" = True

    def __init__(
        self,
        *,
        pool_config: "AiosqlitePoolParams | dict[str, Any] | None" = None,
        pool_instance: "AiosqliteConnectionPool | None" = None,
        migration_config: "dict[str, Any] | None" = None,
        statement_config: "StatementConfig | None" = None,
        driver_features: "AiosqliteDriverFeatures | dict[str, Any] | None" = None,
        bind_key: "str | None" = None,
        extension_config: "dict[str, dict[str, Any]] | None" = None,
    ) -> None:
        """Initialize AioSQLite configuration.

        Args:
            pool_config: Pool configuration parameters (TypedDict or dict)
            pool_instance: Optional pre-configured connection pool instance.
            migration_config: Optional migration configuration.
            statement_config: Optional statement configuration.
            driver_features: Optional driver feature configuration.
            bind_key: Optional unique identifier for this configuration.
            extension_config: Extension-specific configuration (e.g., Litestar plugin settings)
        """
        config_dict = dict(pool_config) if pool_config else {}

        if "database" not in config_dict or config_dict["database"] == ":memory:":
            config_dict["database"] = "file::memory:?cache=shared"
            config_dict["uri"] = True
        elif "database" in config_dict:
            database_path = str(config_dict["database"])
            if database_path.startswith("file:") and not config_dict.get("uri"):
                logger.debug(
                    "Database URI detected (%s) but uri=True not set. "
                    "Auto-enabling URI mode to prevent physical file creation.",
                    database_path,
                )
                config_dict["uri"] = True

        processed_driver_features: dict[str, Any] = dict(driver_features) if driver_features else {}

        if "enable_custom_adapters" not in processed_driver_features:
            processed_driver_features["enable_custom_adapters"] = True

        if "json_serializer" not in processed_driver_features:
            processed_driver_features["json_serializer"] = to_json

        if "json_deserializer" not in processed_driver_features:
            processed_driver_features["json_deserializer"] = from_json

        super().__init__(
            pool_config=config_dict,
            pool_instance=pool_instance,
            migration_config=migration_config,
            statement_config=statement_config or aiosqlite_statement_config,
            driver_features=processed_driver_features,
            bind_key=bind_key,
            extension_config=extension_config,
        )

    def _get_pool_config_dict(self) -> "dict[str, Any]":
        """Get pool configuration as plain dict for external library.

        Returns:
            Dictionary with pool parameters, filtering out None values.
        """
        config: dict[str, Any] = dict(self.pool_config)
        extras = config.pop("extra", {})
        config.update(extras)
        return {k: v for k, v in config.items() if v is not None}

    def _get_connection_config_dict(self) -> "dict[str, Any]":
        """Get connection configuration as plain dict for pool creation.

        Returns:
            Dictionary with connection parameters for creating connections.
        """

        excluded_keys = {
            "pool_size",
            "connect_timeout",
            "idle_timeout",
            "operation_timeout",
            "extra",
            "pool_min_size",
            "pool_max_size",
            "pool_timeout",
            "pool_recycle_seconds",
        }
        return {k: v for k, v in self.pool_config.items() if k not in excluded_keys}

    @asynccontextmanager
    async def provide_connection(self, *args: Any, **kwargs: Any) -> "AsyncGenerator[AiosqliteConnection, None]":
        """Provide an async connection context manager.

        Args:
            *args: Additional arguments.
            **kwargs: Additional keyword arguments.

        Yields:
            An aiosqlite connection instance.
        """
        if self.pool_instance is None:
            self.pool_instance = await self._create_pool()
        async with self.pool_instance.get_connection() as connection:
            yield connection

    @asynccontextmanager
    async def provide_session(
        self, *_args: Any, statement_config: "StatementConfig | None" = None, **_kwargs: Any
    ) -> "AsyncGenerator[AiosqliteDriver, None]":
        """Provide an async driver session context manager.

        Args:
            *_args: Additional arguments.
            statement_config: Optional statement configuration override.
            **_kwargs: Additional keyword arguments.

        Yields:
            An AiosqliteDriver instance.
        """
        async with self.provide_connection(*_args, **_kwargs) as connection:
            yield self.driver_type(
                connection=connection,
                statement_config=statement_config or self.statement_config,
                driver_features=self.driver_features,
            )

    async def _create_pool(self) -> AiosqliteConnectionPool:
        """Create the connection pool instance.

        Returns:
            AiosqliteConnectionPool: The connection pool instance.
        """
        config = self._get_pool_config_dict()
        pool_size = config.pop("pool_size", 5)
        connect_timeout = config.pop("connect_timeout", 30.0)
        idle_timeout = config.pop("idle_timeout", 24 * 60 * 60)
        operation_timeout = config.pop("operation_timeout", 10.0)

        pool = AiosqliteConnectionPool(
            connection_parameters=self._get_connection_config_dict(),
            pool_size=pool_size,
            connect_timeout=connect_timeout,
            idle_timeout=idle_timeout,
            operation_timeout=operation_timeout,
        )

        if self.driver_features.get("enable_custom_adapters", False):
            self._register_type_adapters()

        return pool

    def _register_type_adapters(self) -> None:
        """Register custom type adapters and converters for SQLite.

        Called once during pool creation if enable_custom_adapters is True.
        Registers JSON serialization handlers if configured.

        Note: aiosqlite uses the same sqlite3 module type registration as the
        sync adapter, so this shares the implementation.
        """
        if self.driver_features.get("enable_custom_adapters", False):
            from sqlspec.adapters.sqlite._type_handlers import register_type_handlers

            register_type_handlers(
                json_serializer=self.driver_features.get("json_serializer"),
                json_deserializer=self.driver_features.get("json_deserializer"),
            )

    async def close_pool(self) -> None:
        """Close the connection pool."""
        if self.pool_instance and not self.pool_instance.is_closed:
            await self.pool_instance.close()

    async def create_connection(self) -> "AiosqliteConnection":
        """Create a single async connection from the pool.

        Returns:
            An aiosqlite connection instance.
        """
        if self.pool_instance is None:
            self.pool_instance = await self._create_pool()
        pool_connection = await self.pool_instance.acquire()
        return pool_connection.connection

    async def provide_pool(self) -> AiosqliteConnectionPool:
        """Provide async pool instance.

        Returns:
            The async connection pool.
        """
        if not self.pool_instance:
            self.pool_instance = await self.create_pool()
        return self.pool_instance

    def get_signature_namespace(self) -> "dict[str, type[Any]]":
        """Get the signature namespace for aiosqlite types.

        Returns:
            Dictionary mapping type names to types.
        """
        namespace = super().get_signature_namespace()
        namespace.update(
            {
                "AiosqliteConnection": AiosqliteConnection,
                "AiosqliteConnectionPool": AiosqliteConnectionPool,
                "AiosqliteConnectTimeoutError": AiosqliteConnectTimeoutError,
                "AiosqliteCursor": AiosqliteCursor,
                "AiosqlitePoolClosedError": AiosqlitePoolClosedError,
                "AiosqlitePoolConnection": AiosqlitePoolConnection,
            }
        )
        return namespace

    async def _close_pool(self) -> None:
        """Close the connection pool."""
        await self.close_pool()
