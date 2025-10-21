"""DELETE statement builder.

Provides a fluent interface for building SQL DELETE queries with
parameter binding and validation.
"""

from typing import Any

from sqlglot import exp

from sqlspec.builder._base import QueryBuilder, SafeQuery
from sqlspec.builder._dml import DeleteFromClauseMixin
from sqlspec.builder._select import ReturningClauseMixin, WhereClauseMixin
from sqlspec.core.result import SQLResult
from sqlspec.exceptions import SQLBuilderError

__all__ = ("Delete",)


class Delete(QueryBuilder, WhereClauseMixin, ReturningClauseMixin, DeleteFromClauseMixin):
    """Builder for DELETE statements.

    Constructs SQL DELETE statements with parameter binding and validation.
    Does not support JOIN operations to maintain cross-dialect compatibility.
    """

    __slots__ = ("_table",)
    _expression: exp.Expression | None

    def __init__(self, table: str | None = None, **kwargs: Any) -> None:
        """Initialize DELETE with optional table.

        Args:
            table: Target table name
            **kwargs: Additional QueryBuilder arguments
        """
        super().__init__(**kwargs)
        self._initialize_expression()

        self._table = None

        if table:
            self.from_(table)

    @property
    def _expected_result_type(self) -> "type[SQLResult]":
        """Get the expected result type for DELETE operations.

        Returns:
            The ExecuteResult type for DELETE statements.
        """
        return SQLResult

    def _create_base_expression(self) -> "exp.Delete":
        """Create a new sqlglot Delete expression.

        Returns:
            A new sqlglot Delete expression.
        """
        return exp.Delete()

    def build(self) -> "SafeQuery":
        """Build the DELETE query with validation.

        Returns:
            SafeQuery: The built query with SQL and parameters.

        Raises:
            SQLBuilderError: If the table is not specified.
        """

        if not self._table:
            msg = "DELETE requires a table to be specified. Use from() to set the table."
            raise SQLBuilderError(msg)

        return super().build()
