from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

__all__ = (
    "CheckViolationError",
    "ConfigResolverError",
    "DataError",
    "DatabaseConnectionError",
    "FileNotFoundInStorageError",
    "ForeignKeyViolationError",
    "ImproperConfigurationError",
    "IntegrityError",
    "InvalidVersionFormatError",
    "MigrationError",
    "MissingDependencyError",
    "MultipleResultsFoundError",
    "NotFoundError",
    "NotNullViolationError",
    "OperationalError",
    "OutOfOrderMigrationError",
    "RepositoryError",
    "SQLBuilderError",
    "SQLConversionError",
    "SQLFileNotFoundError",
    "SQLFileParseError",
    "SQLParsingError",
    "SQLSpecError",
    "SerializationError",
    "StorageOperationFailedError",
    "TransactionError",
    "UniqueViolationError",
)


class SQLSpecError(Exception):
    """Base exception class for SQLSpec exceptions."""

    detail: str

    def __init__(self, *args: Any, detail: str = "") -> None:
        """Initialize SQLSpecError.

        Args:
            *args: args are converted to :class:`str` before passing to :class:`Exception`
            detail: detail of the exception.
        """
        str_args = [str(arg) for arg in args if arg]
        if not detail:
            if str_args:
                detail, *str_args = str_args
            elif hasattr(self, "detail"):
                detail = self.detail
        self.detail = detail
        super().__init__(*str_args)

    def __repr__(self) -> str:
        if self.detail:
            return f"{self.__class__.__name__} - {self.detail}"
        return self.__class__.__name__

    def __str__(self) -> str:
        return " ".join((*self.args, self.detail)).strip()


class MissingDependencyError(SQLSpecError, ImportError):
    """Raised when a required dependency is not installed."""

    def __init__(self, package: str, install_package: str | None = None) -> None:
        super().__init__(
            f"Package {package!r} is not installed but required. You can install it by running "
            f"'pip install sqlspec[{install_package or package}]' to install sqlspec with the required extra "
            f"or 'pip install {install_package or package}' to install the package separately"
        )


class BackendNotRegisteredError(SQLSpecError):
    """Raised when a requested storage backend key is not registered."""

    def __init__(self, backend_key: str) -> None:
        super().__init__(f"Storage backend '{backend_key}' is not registered. Please register it before use.")


class ConfigResolverError(SQLSpecError):
    """Exception raised when config resolution fails."""


class SQLParsingError(SQLSpecError):
    """Issues parsing SQL statements."""

    def __init__(self, message: str | None = None) -> None:
        if message is None:
            message = "Issues parsing SQL statement."
        super().__init__(message)


class SQLBuilderError(SQLSpecError):
    """Issues Building or Generating SQL statements."""

    def __init__(self, message: str | None = None) -> None:
        if message is None:
            message = "Issues building SQL statement."
        super().__init__(message)


class SQLConversionError(SQLSpecError):
    """Issues converting SQL statements."""

    def __init__(self, message: str | None = None) -> None:
        if message is None:
            message = "Issues converting SQL statement."
        super().__init__(message)


class ImproperConfigurationError(SQLSpecError):
    """Raised when configuration is invalid or incomplete."""


class SerializationError(SQLSpecError):
    """Encoding or decoding of an object failed."""


class RepositoryError(SQLSpecError):
    """Base repository exception type."""


class IntegrityError(RepositoryError):
    """Data integrity error."""


class NotFoundError(RepositoryError):
    """An identity does not exist."""


class MultipleResultsFoundError(RepositoryError):
    """A single database result was required but more than one were found."""


class UniqueViolationError(IntegrityError):
    """A unique constraint was violated."""


class ForeignKeyViolationError(IntegrityError):
    """A foreign key constraint was violated."""


class CheckViolationError(IntegrityError):
    """A check constraint was violated."""


class NotNullViolationError(IntegrityError):
    """A not-null constraint was violated."""


class DatabaseConnectionError(SQLSpecError):
    """Database connection error (invalid credentials, network failure, etc.)."""


class TransactionError(SQLSpecError):
    """Transaction error (rollback, deadlock, serialization failure)."""


class DataError(SQLSpecError):
    """Invalid data type or format for database operation."""


class OperationalError(SQLSpecError):
    """Operational database error (timeout, disk full, resource limit)."""


class StorageOperationFailedError(SQLSpecError):
    """Raised when a storage backend operation fails (e.g., network, permission, API error)."""


class FileNotFoundInStorageError(StorageOperationFailedError):
    """Raised when a file or object is not found in the storage backend."""


class SQLFileNotFoundError(SQLSpecError):
    """Raised when a SQL file cannot be found."""

    def __init__(self, name: str, path: "str | None" = None) -> None:
        """Initialize the error.

        Args:
            name: Name of the SQL file.
            path: Optional path where the file was expected.
        """
        message = f"SQL file '{name}' not found at path: {path}" if path else f"SQL file '{name}' not found"
        super().__init__(message)
        self.name = name
        self.path = path


class SQLFileParseError(SQLSpecError):
    """Raised when a SQL file cannot be parsed."""

    def __init__(self, name: str, path: str, original_error: "Exception") -> None:
        """Initialize the error.

        Args:
            name: Name of the SQL file.
            path: Path to the SQL file.
            original_error: The underlying parsing error.
        """
        message = f"Failed to parse SQL file '{name}' at {path}: {original_error}"
        super().__init__(message)
        self.name = name
        self.path = path
        self.original_error = original_error


class MigrationError(SQLSpecError):
    """Base exception for migration-related errors."""


class InvalidVersionFormatError(MigrationError):
    """Raised when a migration version format is invalid.

    Invalid formats include versions that don't match sequential (0001)
    or timestamp (YYYYMMDDHHmmss) patterns, or timestamps with invalid dates.
    """


class OutOfOrderMigrationError(MigrationError):
    """Raised when an out-of-order migration is detected in strict mode.

    Out-of-order migrations occur when a pending migration has a timestamp
    earlier than already-applied migrations, typically from late-merging branches.
    """


@contextmanager
def wrap_exceptions(
    wrap_exceptions: bool = True, suppress: "type[Exception] | tuple[type[Exception], ...] | None" = None
) -> Generator[None, None, None]:
    """Context manager for exception handling with optional suppression.

    Args:
        wrap_exceptions: If True, wrap exceptions in RepositoryError. If False, let them pass through.
        suppress: Exception type(s) to suppress completely (like contextlib.suppress).
                 If provided, these exceptions are caught and ignored.
    """
    try:
        yield

    except Exception as exc:
        if suppress is not None and (
            (isinstance(suppress, type) and isinstance(exc, suppress))
            or (isinstance(suppress, tuple) and isinstance(exc, suppress))
        ):
            return

        if isinstance(exc, SQLSpecError):
            raise

        if wrap_exceptions is False:
            raise
        msg = "An error occurred during the operation."
        raise RepositoryError(detail=msg) from exc
