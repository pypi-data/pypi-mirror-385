"""AIOSQLite driver implementation for async SQLite operations."""

import asyncio
import contextlib
import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

import aiosqlite

from sqlspec.core.cache import get_cache_config
from sqlspec.core.parameters import ParameterStyle, ParameterStyleConfig
from sqlspec.core.statement import StatementConfig
from sqlspec.driver import AsyncDriverAdapterBase
from sqlspec.exceptions import (
    CheckViolationError,
    DatabaseConnectionError,
    DataError,
    ForeignKeyViolationError,
    IntegrityError,
    NotNullViolationError,
    OperationalError,
    SQLParsingError,
    SQLSpecError,
    UniqueViolationError,
)
from sqlspec.utils.serializers import to_json

if TYPE_CHECKING:
    from contextlib import AbstractAsyncContextManager

    from sqlspec.adapters.aiosqlite._types import AiosqliteConnection
    from sqlspec.core.result import SQLResult
    from sqlspec.core.statement import SQL
    from sqlspec.driver import ExecutionResult
    from sqlspec.driver._async import AsyncDataDictionaryBase

__all__ = ("AiosqliteCursor", "AiosqliteDriver", "AiosqliteExceptionHandler", "aiosqlite_statement_config")

SQLITE_CONSTRAINT_UNIQUE_CODE = 2067
SQLITE_CONSTRAINT_FOREIGNKEY_CODE = 787
SQLITE_CONSTRAINT_NOTNULL_CODE = 1811
SQLITE_CONSTRAINT_CHECK_CODE = 531
SQLITE_CONSTRAINT_CODE = 19
SQLITE_CANTOPEN_CODE = 14
SQLITE_IOERR_CODE = 10
SQLITE_MISMATCH_CODE = 20


aiosqlite_statement_config = StatementConfig(
    dialect="sqlite",
    parameter_config=ParameterStyleConfig(
        default_parameter_style=ParameterStyle.QMARK,
        supported_parameter_styles={ParameterStyle.QMARK},
        default_execution_parameter_style=ParameterStyle.QMARK,
        supported_execution_parameter_styles={ParameterStyle.QMARK},
        type_coercion_map={
            bool: int,
            datetime.datetime: lambda v: v.isoformat(),
            datetime.date: lambda v: v.isoformat(),
            Decimal: str,
            dict: to_json,
            list: to_json,
            tuple: lambda v: to_json(list(v)),
        },
        has_native_list_expansion=False,
        needs_static_script_compilation=False,
        preserve_parameter_format=True,
    ),
    enable_parsing=True,
    enable_validation=True,
    enable_caching=True,
    enable_parameter_type_wrapping=True,
)


class AiosqliteCursor:
    """Async context manager for AIOSQLite cursors."""

    __slots__ = ("connection", "cursor")

    def __init__(self, connection: "AiosqliteConnection") -> None:
        self.connection = connection
        self.cursor: aiosqlite.Cursor | None = None

    async def __aenter__(self) -> "aiosqlite.Cursor":
        self.cursor = await self.connection.cursor()
        return self.cursor

    async def __aexit__(self, *_: Any) -> None:
        if self.cursor is not None:
            with contextlib.suppress(Exception):
                await self.cursor.close()


class AiosqliteExceptionHandler:
    """Async context manager for handling aiosqlite database exceptions.

    Maps SQLite extended result codes to specific SQLSpec exceptions
    for better error handling in application code.
    """

    __slots__ = ()

    async def __aenter__(self) -> None:
        return None

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if exc_type is None:
            return
        if issubclass(exc_type, aiosqlite.Error):
            self._map_sqlite_exception(exc_val)

    def _map_sqlite_exception(self, e: Any) -> None:
        """Map SQLite exception to SQLSpec exception.

        Args:
            e: aiosqlite.Error instance

        Raises:
            Specific SQLSpec exception based on error code
        """
        error_code = getattr(e, "sqlite_errorcode", None)
        error_name = getattr(e, "sqlite_errorname", None)
        error_msg = str(e).lower()

        if "locked" in error_msg:
            msg = f"AIOSQLite database locked: {e}. Consider enabling WAL mode or reducing concurrency."
            raise SQLSpecError(msg) from e

        if not error_code:
            if "unique constraint" in error_msg:
                self._raise_unique_violation(e, 0)
            elif "foreign key constraint" in error_msg:
                self._raise_foreign_key_violation(e, 0)
            elif "not null constraint" in error_msg:
                self._raise_not_null_violation(e, 0)
            elif "check constraint" in error_msg:
                self._raise_check_violation(e, 0)
            elif "syntax" in error_msg:
                self._raise_parsing_error(e, None)
            else:
                self._raise_generic_error(e)
            return

        if error_code == SQLITE_CONSTRAINT_UNIQUE_CODE or error_name == "SQLITE_CONSTRAINT_UNIQUE":
            self._raise_unique_violation(e, error_code)
        elif error_code == SQLITE_CONSTRAINT_FOREIGNKEY_CODE or error_name == "SQLITE_CONSTRAINT_FOREIGNKEY":
            self._raise_foreign_key_violation(e, error_code)
        elif error_code == SQLITE_CONSTRAINT_NOTNULL_CODE or error_name == "SQLITE_CONSTRAINT_NOTNULL":
            self._raise_not_null_violation(e, error_code)
        elif error_code == SQLITE_CONSTRAINT_CHECK_CODE or error_name == "SQLITE_CONSTRAINT_CHECK":
            self._raise_check_violation(e, error_code)
        elif error_code == SQLITE_CONSTRAINT_CODE or error_name == "SQLITE_CONSTRAINT":
            self._raise_integrity_error(e, error_code)
        elif error_code == SQLITE_CANTOPEN_CODE or error_name == "SQLITE_CANTOPEN":
            self._raise_connection_error(e, error_code)
        elif error_code == SQLITE_IOERR_CODE or error_name == "SQLITE_IOERR":
            self._raise_operational_error(e, error_code)
        elif error_code == SQLITE_MISMATCH_CODE or error_name == "SQLITE_MISMATCH":
            self._raise_data_error(e, error_code)
        elif error_code == 1 or "syntax" in error_msg:
            self._raise_parsing_error(e, error_code)
        else:
            self._raise_generic_error(e)

    def _raise_unique_violation(self, e: Any, code: int) -> None:
        msg = f"SQLite unique constraint violation [code {code}]: {e}"
        raise UniqueViolationError(msg) from e

    def _raise_foreign_key_violation(self, e: Any, code: int) -> None:
        msg = f"SQLite foreign key constraint violation [code {code}]: {e}"
        raise ForeignKeyViolationError(msg) from e

    def _raise_not_null_violation(self, e: Any, code: int) -> None:
        msg = f"SQLite not-null constraint violation [code {code}]: {e}"
        raise NotNullViolationError(msg) from e

    def _raise_check_violation(self, e: Any, code: int) -> None:
        msg = f"SQLite check constraint violation [code {code}]: {e}"
        raise CheckViolationError(msg) from e

    def _raise_integrity_error(self, e: Any, code: int) -> None:
        msg = f"SQLite integrity constraint violation [code {code}]: {e}"
        raise IntegrityError(msg) from e

    def _raise_parsing_error(self, e: Any, code: "int | None") -> None:
        code_str = f"[code {code}]" if code else ""
        msg = f"SQLite SQL syntax error {code_str}: {e}"
        raise SQLParsingError(msg) from e

    def _raise_connection_error(self, e: Any, code: int) -> None:
        msg = f"SQLite connection error [code {code}]: {e}"
        raise DatabaseConnectionError(msg) from e

    def _raise_operational_error(self, e: Any, code: int) -> None:
        msg = f"SQLite operational error [code {code}]: {e}"
        raise OperationalError(msg) from e

    def _raise_data_error(self, e: Any, code: int) -> None:
        msg = f"SQLite data error [code {code}]: {e}"
        raise DataError(msg) from e

    def _raise_generic_error(self, e: Any) -> None:
        msg = f"SQLite database error: {e}"
        raise SQLSpecError(msg) from e


class AiosqliteDriver(AsyncDriverAdapterBase):
    """AIOSQLite driver for async SQLite database operations."""

    __slots__ = ("_data_dictionary",)
    dialect = "sqlite"

    def __init__(
        self,
        connection: "AiosqliteConnection",
        statement_config: "StatementConfig | None" = None,
        driver_features: "dict[str, Any] | None" = None,
    ) -> None:
        if statement_config is None:
            cache_config = get_cache_config()
            statement_config = aiosqlite_statement_config.replace(enable_caching=cache_config.compiled_cache_enabled)

        super().__init__(connection=connection, statement_config=statement_config, driver_features=driver_features)
        self._data_dictionary: AsyncDataDictionaryBase | None = None

    def with_cursor(self, connection: "AiosqliteConnection") -> "AiosqliteCursor":
        """Create async context manager for AIOSQLite cursor."""
        return AiosqliteCursor(connection)

    def handle_database_exceptions(self) -> "AbstractAsyncContextManager[None]":
        """Handle AIOSQLite-specific exceptions."""
        return AiosqliteExceptionHandler()

    async def _try_special_handling(self, cursor: "aiosqlite.Cursor", statement: "SQL") -> "SQLResult | None":
        """Hook for AIOSQLite-specific special operations.

        Args:
            cursor: AIOSQLite cursor object
            statement: SQL statement to analyze

        Returns:
            None - always proceeds with standard execution for AIOSQLite
        """
        _ = (cursor, statement)
        return None

    async def _execute_script(self, cursor: "aiosqlite.Cursor", statement: "SQL") -> "ExecutionResult":
        """Execute SQL script."""
        sql, prepared_parameters = self._get_compiled_sql(statement, self.statement_config)
        statements = self.split_script_statements(sql, statement.statement_config, strip_trailing_semicolon=True)

        successful_count = 0
        last_cursor = cursor

        for stmt in statements:
            await cursor.execute(stmt, prepared_parameters or ())
            successful_count += 1

        return self.create_execution_result(
            last_cursor, statement_count=len(statements), successful_statements=successful_count, is_script_result=True
        )

    async def _execute_many(self, cursor: "aiosqlite.Cursor", statement: "SQL") -> "ExecutionResult":
        """Execute SQL with multiple parameter sets."""
        sql, prepared_parameters = self._get_compiled_sql(statement, self.statement_config)

        if not prepared_parameters:
            msg = "execute_many requires parameters"
            raise ValueError(msg)

        await cursor.executemany(sql, prepared_parameters)

        affected_rows = cursor.rowcount if cursor.rowcount and cursor.rowcount > 0 else 0

        return self.create_execution_result(cursor, rowcount_override=affected_rows, is_many_result=True)

    async def _execute_statement(self, cursor: "aiosqlite.Cursor", statement: "SQL") -> "ExecutionResult":
        """Execute single SQL statement."""
        sql, prepared_parameters = self._get_compiled_sql(statement, self.statement_config)
        await cursor.execute(sql, prepared_parameters or ())

        if statement.returns_rows():
            fetched_data = await cursor.fetchall()
            column_names = [col[0] for col in cursor.description or []]

            data = [dict(zip(column_names, row, strict=False)) for row in fetched_data]

            return self.create_execution_result(
                cursor, selected_data=data, column_names=column_names, data_row_count=len(data), is_select_result=True
            )

        affected_rows = cursor.rowcount if cursor.rowcount and cursor.rowcount > 0 else 0
        return self.create_execution_result(cursor, rowcount_override=affected_rows)

    async def begin(self) -> None:
        """Begin a database transaction."""
        try:
            if not self.connection.in_transaction:
                await self.connection.execute("BEGIN IMMEDIATE")
        except aiosqlite.Error as e:
            import random

            max_retries = 3
            for attempt in range(max_retries):
                delay = 0.01 * (2**attempt) + random.uniform(0, 0.01)  # noqa: S311
                await asyncio.sleep(delay)
                try:
                    await self.connection.execute("BEGIN IMMEDIATE")
                except aiosqlite.Error:
                    if attempt == max_retries - 1:
                        break
                else:
                    return
            msg = f"Failed to begin transaction after retries: {e}"
            raise SQLSpecError(msg) from e

    async def rollback(self) -> None:
        """Rollback the current transaction."""
        try:
            await self.connection.rollback()
        except aiosqlite.Error as e:
            msg = f"Failed to rollback transaction: {e}"
            raise SQLSpecError(msg) from e

    async def commit(self) -> None:
        """Commit the current transaction."""
        try:
            await self.connection.commit()
        except aiosqlite.Error as e:
            msg = f"Failed to commit transaction: {e}"
            raise SQLSpecError(msg) from e

    @property
    def data_dictionary(self) -> "AsyncDataDictionaryBase":
        """Get the data dictionary for this driver.

        Returns:
            Data dictionary instance for metadata queries
        """
        if self._data_dictionary is None:
            from sqlspec.adapters.aiosqlite.data_dictionary import AiosqliteAsyncDataDictionary

            self._data_dictionary = AiosqliteAsyncDataDictionary()
        return self._data_dictionary
