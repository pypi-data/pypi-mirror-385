"""ADBC database configuration."""

import logging
from collections.abc import Callable
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, ClassVar, TypedDict

from typing_extensions import NotRequired

from sqlspec.adapters.adbc._types import AdbcConnection
from sqlspec.adapters.adbc.driver import AdbcCursor, AdbcDriver, get_adbc_statement_config
from sqlspec.config import NoPoolSyncConfig
from sqlspec.core.statement import StatementConfig
from sqlspec.exceptions import ImproperConfigurationError
from sqlspec.utils.module_loader import import_string

if TYPE_CHECKING:
    from collections.abc import Generator
    from contextlib import AbstractContextManager

    from sqlglot.dialects.dialect import DialectType

logger = logging.getLogger("sqlspec.adapters.adbc")


class AdbcConnectionParams(TypedDict):
    """ADBC connection parameters."""

    uri: NotRequired[str]
    driver_name: NotRequired[str]
    db_kwargs: NotRequired[dict[str, Any]]
    conn_kwargs: NotRequired[dict[str, Any]]
    adbc_driver_manager_entrypoint: NotRequired[str]
    autocommit: NotRequired[bool]
    isolation_level: NotRequired[str]
    batch_size: NotRequired[int]
    query_timeout: NotRequired[float]
    connection_timeout: NotRequired[float]
    ssl_mode: NotRequired[str]
    ssl_cert: NotRequired[str]
    ssl_key: NotRequired[str]
    ssl_ca: NotRequired[str]
    username: NotRequired[str]
    password: NotRequired[str]
    token: NotRequired[str]
    project_id: NotRequired[str]
    dataset_id: NotRequired[str]
    account: NotRequired[str]
    warehouse: NotRequired[str]
    database: NotRequired[str]
    schema: NotRequired[str]
    role: NotRequired[str]
    authorization_header: NotRequired[str]
    grpc_options: NotRequired[dict[str, Any]]
    extra: NotRequired[dict[str, Any]]


class AdbcDriverFeatures(TypedDict):
    """ADBC driver feature configuration.

    Controls optional type handling and serialization behavior for the ADBC adapter.
    These features configure how data is converted between Python and Arrow types.

    Attributes:
        json_serializer: JSON serialization function to use.
            Callable that takes Any and returns str (JSON string).
            Default: sqlspec.utils.serializers.to_json
        enable_cast_detection: Enable cast-aware parameter processing.
            When True, detects SQL casts (e.g., ::JSONB) and applies appropriate
            serialization. Currently used for PostgreSQL JSONB handling.
            Default: True
        strict_type_coercion: Enforce strict type coercion rules.
            When True, raises errors for unsupported type conversions.
            When False, attempts best-effort conversion.
            Default: False
        arrow_extension_types: Enable PyArrow extension type support.
            When True, preserves Arrow extension type metadata when reading data.
            When False, falls back to storage types.
            Default: True
    """

    json_serializer: "NotRequired[Callable[[Any], str]]"
    enable_cast_detection: NotRequired[bool]
    strict_type_coercion: NotRequired[bool]
    arrow_extension_types: NotRequired[bool]


__all__ = ("AdbcConfig", "AdbcConnectionParams", "AdbcDriverFeatures")


class AdbcConfig(NoPoolSyncConfig[AdbcConnection, AdbcDriver]):
    """ADBC configuration for Arrow Database Connectivity.

    ADBC provides an interface for connecting to multiple database systems
    with Arrow-native data transfer.

    Supports multiple database backends including PostgreSQL, SQLite, DuckDB,
    BigQuery, and Snowflake with automatic driver detection and loading.
    """

    driver_type: ClassVar[type[AdbcDriver]] = AdbcDriver
    connection_type: "ClassVar[type[AdbcConnection]]" = AdbcConnection
    supports_transactional_ddl: ClassVar[bool] = False

    def __init__(
        self,
        *,
        connection_config: AdbcConnectionParams | dict[str, Any] | None = None,
        migration_config: dict[str, Any] | None = None,
        statement_config: StatementConfig | None = None,
        driver_features: "AdbcDriverFeatures | dict[str, Any] | None" = None,
        bind_key: str | None = None,
        extension_config: "dict[str, dict[str, Any]] | None" = None,
    ) -> None:
        """Initialize configuration.

        Args:
            connection_config: Connection configuration parameters
            migration_config: Migration configuration
            statement_config: Default SQL statement configuration
            driver_features: Driver feature configuration (AdbcDriverFeatures)
            bind_key: Optional unique identifier for this configuration
            extension_config: Extension-specific configuration (e.g., Litestar plugin settings)
        """
        if connection_config is None:
            connection_config = {}
        extras = connection_config.pop("extra", {})
        if not isinstance(extras, dict):
            msg = "The 'extra' field in connection_config must be a dictionary."
            raise ImproperConfigurationError(msg)
        self.connection_config: dict[str, Any] = dict(connection_config)
        self.connection_config.update(extras)

        if statement_config is None:
            detected_dialect = str(self._get_dialect() or "sqlite")
            statement_config = get_adbc_statement_config(detected_dialect)

        from sqlspec.utils.serializers import to_json

        if driver_features is None:
            driver_features = {}
        if "json_serializer" not in driver_features:
            driver_features["json_serializer"] = to_json
        if "enable_cast_detection" not in driver_features:
            driver_features["enable_cast_detection"] = True
        if "strict_type_coercion" not in driver_features:
            driver_features["strict_type_coercion"] = False
        if "arrow_extension_types" not in driver_features:
            driver_features["arrow_extension_types"] = True

        super().__init__(
            connection_config=self.connection_config,
            migration_config=migration_config,
            statement_config=statement_config,
            driver_features=dict(driver_features),
            bind_key=bind_key,
            extension_config=extension_config,
        )

    def _resolve_driver_name(self) -> str:
        """Resolve and normalize the driver name.

        Returns:
            The normalized driver connect function path.
        """
        driver_name = self.connection_config.get("driver_name")
        uri = self.connection_config.get("uri")

        if isinstance(driver_name, str):
            driver_aliases = {
                "sqlite": "adbc_driver_sqlite.dbapi.connect",
                "sqlite3": "adbc_driver_sqlite.dbapi.connect",
                "adbc_driver_sqlite": "adbc_driver_sqlite.dbapi.connect",
                "duckdb": "adbc_driver_duckdb.dbapi.connect",
                "adbc_driver_duckdb": "adbc_driver_duckdb.dbapi.connect",
                "postgres": "adbc_driver_postgresql.dbapi.connect",
                "postgresql": "adbc_driver_postgresql.dbapi.connect",
                "pg": "adbc_driver_postgresql.dbapi.connect",
                "adbc_driver_postgresql": "adbc_driver_postgresql.dbapi.connect",
                "snowflake": "adbc_driver_snowflake.dbapi.connect",
                "sf": "adbc_driver_snowflake.dbapi.connect",
                "adbc_driver_snowflake": "adbc_driver_snowflake.dbapi.connect",
                "bigquery": "adbc_driver_bigquery.dbapi.connect",
                "bq": "adbc_driver_bigquery.dbapi.connect",
                "adbc_driver_bigquery": "adbc_driver_bigquery.dbapi.connect",
                "flightsql": "adbc_driver_flightsql.dbapi.connect",
                "adbc_driver_flightsql": "adbc_driver_flightsql.dbapi.connect",
                "grpc": "adbc_driver_flightsql.dbapi.connect",
            }

            resolved_driver = driver_aliases.get(driver_name, driver_name)

            if not resolved_driver.endswith(".dbapi.connect"):
                resolved_driver = f"{resolved_driver}.dbapi.connect"

            return resolved_driver

        if isinstance(uri, str):
            if uri.startswith(("postgresql://", "postgres://")):
                return "adbc_driver_postgresql.dbapi.connect"
            if uri.startswith("sqlite://"):
                return "adbc_driver_sqlite.dbapi.connect"
            if uri.startswith("duckdb://"):
                return "adbc_driver_duckdb.dbapi.connect"
            if uri.startswith("grpc://"):
                return "adbc_driver_flightsql.dbapi.connect"
            if uri.startswith("snowflake://"):
                return "adbc_driver_snowflake.dbapi.connect"
            if uri.startswith("bigquery://"):
                return "adbc_driver_bigquery.dbapi.connect"

        return "adbc_driver_sqlite.dbapi.connect"

    def _get_connect_func(self) -> Callable[..., AdbcConnection]:
        """Get the driver connect function.

        Returns:
            The driver connect function.

        Raises:
            ImproperConfigurationError: If driver cannot be loaded.
        """
        driver_path = self._resolve_driver_name()

        try:
            connect_func = import_string(driver_path)
        except ImportError as e:
            # Only add .dbapi.connect if it's not already there
            if not driver_path.endswith(".dbapi.connect"):
                driver_path_with_suffix = f"{driver_path}.dbapi.connect"
            else:
                driver_path_with_suffix = driver_path
            try:
                connect_func = import_string(driver_path_with_suffix)
            except ImportError as e2:
                msg = (
                    f"Failed to import connect function from '{driver_path}' or "
                    f"'{driver_path_with_suffix}'. Is the driver installed? "
                    f"Original errors: {e} / {e2}"
                )
                raise ImproperConfigurationError(msg) from e2

        if not callable(connect_func):
            msg = f"The path '{driver_path}' did not resolve to a callable function."
            raise ImproperConfigurationError(msg)

        return connect_func  # type: ignore[no-any-return]

    def _get_dialect(self) -> "DialectType":
        """Get the SQL dialect type based on the driver.

        Returns:
            The SQL dialect type for the driver.
        """
        try:
            driver_path = self._resolve_driver_name()
        except ImproperConfigurationError:
            return None

        dialect_map = {
            "postgres": "postgres",
            "sqlite": "sqlite",
            "duckdb": "duckdb",
            "bigquery": "bigquery",
            "snowflake": "snowflake",
            "flightsql": "sqlite",
            "grpc": "sqlite",
        }
        for keyword, dialect in dialect_map.items():
            if keyword in driver_path:
                return dialect
        return None

    def _get_parameter_styles(self) -> tuple[tuple[str, ...], str]:
        """Get parameter styles based on the underlying driver.

        Returns:
            Tuple of (supported_parameter_styles, default_parameter_style)
        """
        try:
            driver_path = self._resolve_driver_name()
            if "postgresql" in driver_path:
                return (("numeric",), "numeric")
            if "sqlite" in driver_path:
                return (("qmark", "named_colon"), "qmark")
            if "duckdb" in driver_path:
                return (("qmark", "numeric"), "qmark")
            if "bigquery" in driver_path:
                return (("named_at",), "named_at")
            if "snowflake" in driver_path:
                return (("qmark", "numeric"), "qmark")

        except Exception:
            logger.debug("Error resolving parameter styles, using defaults")
        return (("qmark",), "qmark")

    def create_connection(self) -> AdbcConnection:
        """Create and return a new connection using the specified driver.

        Returns:
            A new connection instance.

        Raises:
            ImproperConfigurationError: If the connection could not be established.
        """

        try:
            connect_func = self._get_connect_func()
            connection_config_dict = self._get_connection_config_dict()
            connection = connect_func(**connection_config_dict)
        except Exception as e:
            driver_name = self.connection_config.get("driver_name", "Unknown")
            msg = f"Could not configure connection using driver '{driver_name}'. Error: {e}"
            raise ImproperConfigurationError(msg) from e
        return connection

    @contextmanager
    def provide_connection(self, *args: Any, **kwargs: Any) -> "Generator[AdbcConnection, None, None]":
        """Provide a connection context manager.

        Args:
            *args: Additional arguments.
            **kwargs: Additional keyword arguments.

        Yields:
            A connection instance.
        """
        connection = self.create_connection()
        try:
            yield connection
        finally:
            connection.close()

    def provide_session(
        self, *args: Any, statement_config: "StatementConfig | None" = None, **kwargs: Any
    ) -> "AbstractContextManager[AdbcDriver]":
        """Provide a driver session context manager.

        Args:
            *args: Additional arguments.
            statement_config: Optional statement configuration override.
            **kwargs: Additional keyword arguments.

        Returns:
            A context manager that yields an AdbcDriver instance.
        """

        @contextmanager
        def session_manager() -> "Generator[AdbcDriver, None, None]":
            with self.provide_connection(*args, **kwargs) as connection:
                final_statement_config = (
                    statement_config
                    or self.statement_config
                    or get_adbc_statement_config(str(self._get_dialect() or "sqlite"))
                )
                yield self.driver_type(
                    connection=connection, statement_config=final_statement_config, driver_features=self.driver_features
                )

        return session_manager()

    def _get_connection_config_dict(self) -> dict[str, Any]:
        """Get the connection configuration dictionary.

        Returns:
            The connection configuration dictionary.
        """
        config = dict(self.connection_config)

        if "driver_name" in config:
            driver_name = config["driver_name"]

            if "uri" in config:
                uri = config["uri"]

                if driver_name in {"sqlite", "sqlite3", "adbc_driver_sqlite"} and uri.startswith("sqlite://"):  # pyright: ignore
                    config["uri"] = uri[9:]  # pyright: ignore

                elif driver_name in {"duckdb", "adbc_driver_duckdb"} and uri.startswith("duckdb://"):  # pyright: ignore
                    config["path"] = uri[9:]  # pyright: ignore
                    config.pop("uri", None)

            if driver_name in {"bigquery", "bq", "adbc_driver_bigquery"}:
                bigquery_parameters = ["project_id", "dataset_id", "token"]
                db_kwargs = config.get("db_kwargs", {})

                for param in bigquery_parameters:
                    if param in config and param != "db_kwargs":
                        db_kwargs[param] = config.pop(param)  # pyright: ignore

                if db_kwargs:
                    config["db_kwargs"] = db_kwargs

            elif "db_kwargs" in config and driver_name not in {"bigquery", "bq", "adbc_driver_bigquery"}:
                db_kwargs = config.pop("db_kwargs")
                if isinstance(db_kwargs, dict):
                    config.update(db_kwargs)

            config.pop("driver_name", None)

        return config

    def get_signature_namespace(self) -> "dict[str, type[Any]]":
        """Get the signature namespace for types.

        Returns:
            Dictionary mapping type names to types.
        """

        namespace = super().get_signature_namespace()
        namespace.update({"AdbcConnection": AdbcConnection, "AdbcCursor": AdbcCursor})
        return namespace
