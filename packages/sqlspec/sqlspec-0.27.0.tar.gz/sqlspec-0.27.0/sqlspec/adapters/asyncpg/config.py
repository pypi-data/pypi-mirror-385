"""AsyncPG database configuration with direct field-based configuration."""

import logging
from collections.abc import Callable
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any, ClassVar, TypedDict

from asyncpg import Connection, Record
from asyncpg import create_pool as asyncpg_create_pool
from asyncpg.connection import ConnectionMeta
from asyncpg.pool import Pool, PoolConnectionProxy, PoolConnectionProxyMeta
from typing_extensions import NotRequired

from sqlspec.adapters.asyncpg._types import AsyncpgConnection
from sqlspec.adapters.asyncpg.driver import AsyncpgCursor, AsyncpgDriver, asyncpg_statement_config
from sqlspec.config import AsyncDatabaseConfig
from sqlspec.typing import PGVECTOR_INSTALLED
from sqlspec.utils.serializers import from_json, to_json

if TYPE_CHECKING:
    from asyncio.events import AbstractEventLoop
    from collections.abc import AsyncGenerator, Awaitable

    from sqlspec.core.statement import StatementConfig


__all__ = ("AsyncpgConfig", "AsyncpgConnectionConfig", "AsyncpgDriverFeatures", "AsyncpgPoolConfig")

logger = logging.getLogger("sqlspec")


class AsyncpgConnectionConfig(TypedDict):
    """TypedDict for AsyncPG connection parameters."""

    dsn: NotRequired[str]
    host: NotRequired[str]
    port: NotRequired[int]
    user: NotRequired[str]
    password: NotRequired[str]
    database: NotRequired[str]
    ssl: NotRequired[Any]
    passfile: NotRequired[str]
    direct_tls: NotRequired[bool]
    connect_timeout: NotRequired[float]
    command_timeout: NotRequired[float]
    statement_cache_size: NotRequired[int]
    max_cached_statement_lifetime: NotRequired[int]
    max_cacheable_statement_size: NotRequired[int]
    server_settings: NotRequired[dict[str, str]]


class AsyncpgPoolConfig(AsyncpgConnectionConfig):
    """TypedDict for AsyncPG pool parameters, inheriting connection parameters."""

    min_size: NotRequired[int]
    max_size: NotRequired[int]
    max_queries: NotRequired[int]
    max_inactive_connection_lifetime: NotRequired[float]
    setup: NotRequired["Callable[[AsyncpgConnection], Awaitable[None]]"]
    init: NotRequired["Callable[[AsyncpgConnection], Awaitable[None]]"]
    loop: NotRequired["AbstractEventLoop"]
    connection_class: NotRequired[type["AsyncpgConnection"]]
    record_class: NotRequired[type[Record]]
    extra: NotRequired[dict[str, Any]]


class AsyncpgDriverFeatures(TypedDict):
    """AsyncPG driver feature flags.

    json_serializer: Custom JSON serializer function for PostgreSQL JSON/JSONB types.
        Defaults to sqlspec.utils.serializers.to_json.
        Use for performance optimization (e.g., orjson) or custom encoding behavior.
        Applied when enable_json_codecs is True.
    json_deserializer: Custom JSON deserializer function for PostgreSQL JSON/JSONB types.
        Defaults to sqlspec.utils.serializers.from_json.
        Use for performance optimization (e.g., orjson) or custom decoding behavior.
        Applied when enable_json_codecs is True.
    enable_json_codecs: Enable automatic JSON/JSONB codec registration on connections.
        Defaults to True for seamless Python dict/list to PostgreSQL JSON/JSONB conversion.
        Set to False to disable automatic codec registration (manual handling required).
    enable_pgvector: Enable pgvector extension support for vector similarity search.
        Requires pgvector-python package (pip install pgvector) and PostgreSQL with pgvector extension.
        Defaults to True when pgvector-python is installed.
        Provides automatic conversion between Python objects and PostgreSQL vector types.
        Enables vector similarity operations and index support.
    """

    json_serializer: NotRequired[Callable[[Any], str]]
    json_deserializer: NotRequired[Callable[[str], Any]]
    enable_json_codecs: NotRequired[bool]
    enable_pgvector: NotRequired[bool]


class AsyncpgConfig(AsyncDatabaseConfig[AsyncpgConnection, "Pool[Record]", AsyncpgDriver]):
    """Configuration for AsyncPG database connections using TypedDict."""

    driver_type: "ClassVar[type[AsyncpgDriver]]" = AsyncpgDriver
    connection_type: "ClassVar[type[AsyncpgConnection]]" = type(AsyncpgConnection)  # type: ignore[assignment]
    supports_transactional_ddl: "ClassVar[bool]" = True

    def __init__(
        self,
        *,
        pool_config: "AsyncpgPoolConfig | dict[str, Any] | None" = None,
        pool_instance: "Pool[Record] | None" = None,
        migration_config: "dict[str, Any] | None" = None,
        statement_config: "StatementConfig | None" = None,
        driver_features: "AsyncpgDriverFeatures | dict[str, Any] | None" = None,
        bind_key: "str | None" = None,
        extension_config: "dict[str, dict[str, Any]] | None" = None,
    ) -> None:
        """Initialize AsyncPG configuration.

        Args:
            pool_config: Pool configuration parameters (TypedDict or dict)
            pool_instance: Existing pool instance to use
            migration_config: Migration configuration
            statement_config: Statement configuration override
            driver_features: Driver features configuration (TypedDict or dict)
            bind_key: Optional unique identifier for this configuration
            extension_config: Extension-specific configuration (e.g., Litestar plugin settings)
        """
        features_dict: dict[str, Any] = dict(driver_features) if driver_features else {}

        if "json_serializer" not in features_dict:
            features_dict["json_serializer"] = to_json
        if "json_deserializer" not in features_dict:
            features_dict["json_deserializer"] = from_json
        if "enable_json_codecs" not in features_dict:
            features_dict["enable_json_codecs"] = True
        if "enable_pgvector" not in features_dict:
            features_dict["enable_pgvector"] = PGVECTOR_INSTALLED

        super().__init__(
            pool_config=dict(pool_config) if pool_config else {},
            pool_instance=pool_instance,
            migration_config=migration_config,
            statement_config=statement_config or asyncpg_statement_config,
            driver_features=features_dict,
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

    async def _create_pool(self) -> "Pool[Record]":
        """Create the actual async connection pool."""
        config = self._get_pool_config_dict()

        if "init" not in config:
            config["init"] = self._init_connection

        return await asyncpg_create_pool(**config)

    async def _init_connection(self, connection: "AsyncpgConnection") -> None:
        """Initialize connection with JSON codecs and pgvector support.

        Args:
            connection: AsyncPG connection to initialize.
        """
        if self.driver_features.get("enable_json_codecs", True):
            from sqlspec.adapters.asyncpg._type_handlers import register_json_codecs

            await register_json_codecs(
                connection,
                encoder=self.driver_features.get("json_serializer", to_json),
                decoder=self.driver_features.get("json_deserializer", from_json),
            )

        if self.driver_features.get("enable_pgvector", False):
            from sqlspec.adapters.asyncpg._type_handlers import register_pgvector_support

            await register_pgvector_support(connection)

    async def _close_pool(self) -> None:
        """Close the actual async connection pool."""
        if self.pool_instance:
            await self.pool_instance.close()

    async def close_pool(self) -> None:
        """Close the connection pool."""
        await self._close_pool()

    async def create_connection(self) -> "AsyncpgConnection":
        """Create a single async connection from the pool.

        Returns:
            An AsyncPG connection instance.
        """
        if self.pool_instance is None:
            self.pool_instance = await self._create_pool()
        return await self.pool_instance.acquire()

    @asynccontextmanager
    async def provide_connection(self, *args: Any, **kwargs: Any) -> "AsyncGenerator[AsyncpgConnection, None]":
        """Provide an async connection context manager.

        Args:
            *args: Additional arguments.
            **kwargs: Additional keyword arguments.

        Yields:
            An AsyncPG connection instance.
        """
        if self.pool_instance is None:
            self.pool_instance = await self._create_pool()
        connection = None
        try:
            connection = await self.pool_instance.acquire()
            yield connection
        finally:
            if connection is not None:
                await self.pool_instance.release(connection)

    @asynccontextmanager
    async def provide_session(
        self, *args: Any, statement_config: "StatementConfig | None" = None, **kwargs: Any
    ) -> "AsyncGenerator[AsyncpgDriver, None]":
        """Provide an async driver session context manager.

        Args:
            *args: Additional arguments.
            statement_config: Optional statement configuration override.
            **kwargs: Additional keyword arguments.

        Yields:
            An AsyncpgDriver instance.
        """
        async with self.provide_connection(*args, **kwargs) as connection:
            final_statement_config = statement_config or self.statement_config or asyncpg_statement_config
            yield self.driver_type(
                connection=connection, statement_config=final_statement_config, driver_features=self.driver_features
            )

    async def provide_pool(self, *args: Any, **kwargs: Any) -> "Pool[Record]":
        """Provide async pool instance.

        Returns:
            The async connection pool.
        """
        if not self.pool_instance:
            self.pool_instance = await self.create_pool()
        return self.pool_instance

    def get_signature_namespace(self) -> "dict[str, type[Any]]":
        """Get the signature namespace for AsyncPG types.

        This provides all AsyncPG-specific types that Litestar needs to recognize
        to avoid serialization attempts.

        Returns:
            Dictionary mapping type names to types.
        """

        namespace = super().get_signature_namespace()
        namespace.update(
            {
                "Connection": Connection,
                "Pool": Pool,
                "PoolConnectionProxy": PoolConnectionProxy,
                "PoolConnectionProxyMeta": PoolConnectionProxyMeta,
                "ConnectionMeta": ConnectionMeta,
                "Record": Record,
                "AsyncpgConnection": AsyncpgConnection,  # type: ignore[dict-item]
                "AsyncpgCursor": AsyncpgCursor,
            }
        )
        return namespace
