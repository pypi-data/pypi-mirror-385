"""Reusable mixins for INSERT/UPDATE/DELETE builders."""

from collections.abc import Mapping, Sequence
from typing import Any, cast

from mypy_extensions import trait
from sqlglot import exp
from typing_extensions import Self

from sqlspec.builder._parsing_utils import extract_sql_object_expression
from sqlspec.exceptions import SQLBuilderError
from sqlspec.protocols import SQLBuilderProtocol
from sqlspec.utils.type_guards import has_expression_and_sql, has_query_builder_parameters

__all__ = (
    "DeleteFromClauseMixin",
    "InsertFromSelectMixin",
    "InsertIntoClauseMixin",
    "InsertValuesMixin",
    "UpdateFromClauseMixin",
    "UpdateSetClauseMixin",
    "UpdateTableClauseMixin",
)

ARG_PAIR_COUNT = 2
SINGLE_VALUE_COUNT = 1


# ---------------------------------------------------------------------------
# DELETE helpers
# ---------------------------------------------------------------------------


@trait
class DeleteFromClauseMixin:
    """Mixin providing FROM clause support for DELETE builders."""

    __slots__ = ()

    def get_expression(self) -> exp.Expression | None: ...
    def set_expression(self, expression: exp.Expression) -> None: ...

    def from_(self, table: str) -> Self:
        current_expr = self.get_expression()
        if current_expr is None:
            self.set_expression(exp.Delete())
            current_expr = self.get_expression()

        if not isinstance(current_expr, exp.Delete):
            msg = f"Base expression for Delete is {type(current_expr).__name__}, expected Delete."
            raise SQLBuilderError(msg)

        assert current_expr is not None
        setattr(self, "_table", table)
        current_expr.set("this", exp.to_table(table))
        return self


# ---------------------------------------------------------------------------
# INSERT helpers
# ---------------------------------------------------------------------------


@trait
class InsertIntoClauseMixin:
    __slots__ = ()

    def get_expression(self) -> exp.Expression | None: ...
    def set_expression(self, expression: exp.Expression) -> None: ...

    def into(self, table: str) -> Self:
        current_expr = self.get_expression()
        if current_expr is None:
            self.set_expression(exp.Insert())
            current_expr = self.get_expression()

        if not isinstance(current_expr, exp.Insert):
            msg = "Cannot set target table on a non-INSERT expression."
            raise SQLBuilderError(msg)

        assert current_expr is not None
        setattr(self, "_table", table)
        current_expr.set("this", exp.to_table(table))
        return self


@trait
class InsertValuesMixin:
    __slots__ = ()

    def get_expression(self) -> exp.Expression | None: ...
    def set_expression(self, expression: exp.Expression) -> None: ...

    _columns: Any

    def add_parameter(self, value: Any, name: str | None = None) -> tuple[Any, str]:
        msg = "Method must be provided by QueryBuilder subclass"
        raise NotImplementedError(msg)

    def _generate_unique_parameter_name(self, base_name: str) -> str:
        msg = "Method must be provided by QueryBuilder subclass"
        raise NotImplementedError(msg)

    def columns(self, *columns: str | exp.Expression) -> Self:
        current_expr = self.get_expression()
        if current_expr is None:
            self.set_expression(exp.Insert())
            current_expr = self.get_expression()

        if not isinstance(current_expr, exp.Insert):
            msg = "Cannot set columns on a non-INSERT expression."
            raise SQLBuilderError(msg)

        assert current_expr is not None
        current_this = current_expr.args.get("this")
        if current_this is None:
            msg = "Table must be set using .into() before setting columns."
            raise SQLBuilderError(msg)

        if columns:
            identifiers = [exp.to_identifier(col) if isinstance(col, str) else col for col in columns]
            table_name = current_this.this
            current_expr.set("this", exp.Schema(this=table_name, expressions=identifiers))
        elif isinstance(current_this, exp.Schema):
            table_name = current_this.this
            current_expr.set("this", exp.Table(this=table_name))

        try:
            cols = self._columns
            if not columns:
                cols.clear()
            else:
                cols[:] = [col if isinstance(col, str) else str(col) for col in columns]
        except AttributeError:
            pass
        return self

    def values(self, *values: Any, **kwargs: Any) -> Self:
        current_expr = self.get_expression()
        if current_expr is None:
            self.set_expression(exp.Insert())
            current_expr = self.get_expression()

        if not isinstance(current_expr, exp.Insert):
            msg = "Cannot add values to a non-INSERT expression."
            raise SQLBuilderError(msg)

        assert current_expr is not None
        table_name = cast("str | None", self._table)  # type: ignore[attr-defined]
        if not table_name:
            msg = "The target table must be set using .into() before adding values."
            raise SQLBuilderError(msg)

        positional_values = list(values)
        if len(positional_values) == SINGLE_VALUE_COUNT and hasattr(positional_values[0], "items") and not kwargs:
            kwargs = cast("dict[str, Any]", positional_values[0])
            positional_values = []

        if kwargs and positional_values:
            msg = "Cannot mix positional values with keyword values."
            raise SQLBuilderError(msg)

        row_expressions: list[exp.Expression] = []
        column_defs = cast("list[str]", self._columns or [])

        if kwargs:
            if not column_defs:
                self.columns(*kwargs.keys())
                column_defs = cast("list[str]", self._columns)
            for col, val in kwargs.items():
                if isinstance(val, exp.Expression):
                    row_expressions.append(val)
                    continue
                if has_expression_and_sql(val):
                    row_expressions.append(extract_sql_object_expression(val, builder=self))
                    continue
                column_name = str(col).split(".")[-1]
                unique_name = self._generate_unique_parameter_name(column_name)
                _, unique_name = self.add_parameter(val, name=unique_name)
                row_expressions.append(exp.Placeholder(this=unique_name))
        else:
            if column_defs and len(positional_values) != len(column_defs):
                msg = (
                    f"Number of values ({len(positional_values)}) does not match the number of specified columns "
                    f"({len(column_defs)})."
                )
                raise SQLBuilderError(msg)

            for index, raw_value in enumerate(positional_values):
                if isinstance(raw_value, exp.Expression):
                    row_expressions.append(raw_value)
                elif has_expression_and_sql(raw_value):
                    row_expressions.append(extract_sql_object_expression(raw_value, builder=self))
                else:
                    if column_defs and index < len(column_defs):
                        column_token = column_defs[index]
                        column_name = column_token.rsplit(".", maxsplit=1)[-1]
                    else:
                        column_name = f"value_{index + 1}"
                    unique_name = self._generate_unique_parameter_name(column_name)
                    _, unique_name = self.add_parameter(raw_value, name=unique_name)
                    row_expressions.append(exp.Placeholder(this=unique_name))

        values_node = current_expr.args.get("expression")
        tuple_expression = exp.Tuple(expressions=row_expressions)
        if isinstance(values_node, exp.Values):
            values_node.expressions.append(tuple_expression)
        else:
            current_expr.set("expression", exp.Values(expressions=[tuple_expression]))
        return self

    def add_values(self, values: Sequence[Any]) -> Self:
        return self.values(*values)


@trait
class InsertFromSelectMixin:
    __slots__ = ()

    def get_expression(self) -> exp.Expression | None: ...
    def set_expression(self, expression: exp.Expression) -> None: ...

    _table: Any

    def add_parameter(self, value: Any, name: str | None = None) -> tuple[Any, str]:
        msg = "Method must be provided by QueryBuilder subclass"
        raise NotImplementedError(msg)

    def from_select(self, select_builder: SQLBuilderProtocol) -> Self:
        if not getattr(self, "_table", None):
            msg = "The target table must be set using .into() before adding values."
            raise SQLBuilderError(msg)

        current_expr = self.get_expression()
        if current_expr is None:
            self.set_expression(exp.Insert())
            current_expr = self.get_expression()

        if not isinstance(current_expr, exp.Insert):
            msg = "Cannot set INSERT source on a non-INSERT expression."
            raise SQLBuilderError(msg)

        assert current_expr is not None
        subquery_parameters = getattr(select_builder, "_parameters", None)
        if isinstance(subquery_parameters, dict):
            builder_with_params = cast("SQLBuilderProtocol", self)
            for param_name, param_value in subquery_parameters.items():
                builder_with_params.add_parameter(param_value, name=param_name)

        select_expr = getattr(select_builder, "_expression", None)
        if select_expr and isinstance(select_expr, exp.Select):
            current_expr.set("expression", select_expr.copy())
        else:
            msg = "SelectBuilder must have a valid SELECT expression."
            raise SQLBuilderError(msg)
        return self


# ---------------------------------------------------------------------------
# UPDATE helpers
# ---------------------------------------------------------------------------


@trait
class UpdateTableClauseMixin:
    __slots__ = ()

    def get_expression(self) -> exp.Expression | None: ...
    def set_expression(self, expression: exp.Expression) -> None: ...

    def table(self, table_name: str, alias: str | None = None) -> Self:
        current_expr = self.get_expression()
        if current_expr is None or not isinstance(current_expr, exp.Update):
            self.set_expression(exp.Update(this=None, expressions=[], joins=[]))
            current_expr = self.get_expression()

        assert current_expr is not None

        table_expr: exp.Expression = exp.to_table(table_name, alias=alias)
        current_expr.set("this", table_expr)
        setattr(self, "_table", table_name)
        return self


@trait
class UpdateSetClauseMixin:
    __slots__ = ()

    def get_expression(self) -> exp.Expression | None: ...
    def set_expression(self, expression: exp.Expression) -> None: ...

    def add_parameter(self, value: Any, name: str | None = None) -> tuple[Any, str]:
        msg = "Method must be provided by QueryBuilder subclass"
        raise NotImplementedError(msg)

    def _generate_unique_parameter_name(self, base_name: str) -> str:
        msg = "Method must be provided by QueryBuilder subclass"
        raise NotImplementedError(msg)

    def _process_update_value(self, val: Any, col: Any) -> exp.Expression:
        if isinstance(val, exp.Expression):
            return val
        if has_query_builder_parameters(val):
            subquery = val.build()
            sql_text = subquery.sql if hasattr(subquery, "sql") and not callable(subquery.sql) else str(subquery)
            value_expr = exp.paren(exp.maybe_parse(sql_text, dialect=getattr(self, "dialect", None)))
            for p_name, p_value in getattr(val, "parameters", {}).items():
                self.add_parameter(p_value, name=p_name)
            return value_expr
        if hasattr(val, "expression") and hasattr(val, "sql"):
            return extract_sql_object_expression(val, builder=self)
        column_name = col if isinstance(col, str) else str(col)
        if "." in column_name:
            column_name = column_name.split(".")[-1]
        param_name = self._generate_unique_parameter_name(column_name)
        param_name = self.add_parameter(val, name=param_name)[1]
        return exp.Placeholder(this=param_name)

    def set(self, *args: Any, **kwargs: Any) -> Self:
        current_expr = self.get_expression()
        if current_expr is None:
            self.set_expression(exp.Update())
            current_expr = self.get_expression()

        if not isinstance(current_expr, exp.Update):
            msg = "Cannot add SET clause to non-UPDATE expression."
            raise SQLBuilderError(msg)

        assert current_expr is not None

        assignments: list[exp.Expression] = []
        if len(args) == ARG_PAIR_COUNT and not kwargs:
            col, val = args
            col_expr = col if isinstance(col, exp.Column) else exp.column(col)
            assignments.append(exp.EQ(this=col_expr, expression=self._process_update_value(val, col)))
        elif (len(args) == SINGLE_VALUE_COUNT and isinstance(args[0], Mapping)) or kwargs:
            all_values = dict(args[0] if args else {}, **kwargs)
            for col, val in all_values.items():
                assignments.append(exp.EQ(this=exp.column(col), expression=self._process_update_value(val, col)))
        else:
            msg = "Invalid arguments for set(): use (column, value), mapping, or kwargs."
            raise SQLBuilderError(msg)

        existing = current_expr.args.get("expressions", [])
        current_expr.set("expressions", existing + assignments)
        return self


@trait
class UpdateFromClauseMixin:
    __slots__ = ()

    def get_expression(self) -> exp.Expression | None: ...
    def set_expression(self, expression: exp.Expression) -> None: ...

    def from_(self, table: str | exp.Expression | Any, alias: str | None = None) -> Self:
        current_expr = self.get_expression()
        if current_expr is None or not isinstance(current_expr, exp.Update):
            msg = "Cannot add FROM clause to non-UPDATE expression. Set the main table first."
            raise SQLBuilderError(msg)

        assert current_expr is not None
        table_expr: exp.Expression
        if isinstance(table, str):
            table_expr = exp.to_table(table, alias=alias)
        elif has_query_builder_parameters(table):
            subquery_params = getattr(table, "_parameters", None)
            if isinstance(subquery_params, dict):
                builder_with_params = cast("SQLBuilderProtocol", self)
                for param_name, param_value in subquery_params.items():
                    builder_with_params.add_parameter(param_value, name=param_name)
            raw_expression = getattr(table, "_expression", None)
            subquery_source = raw_expression if isinstance(raw_expression, exp.Expression) else exp.select()
            subquery_exp = exp.paren(subquery_source)
            table_expr = exp.alias_(subquery_exp, alias) if alias else subquery_exp
        elif isinstance(table, exp.Expression):
            table_expr = exp.alias_(table, alias) if alias else table
        else:
            msg = f"Unsupported table type for FROM clause: {type(table)}"
            raise SQLBuilderError(msg)

        from_clause = current_expr.args.get("from")
        if from_clause is None:
            from_clause = exp.From(expressions=[])
            current_expr.set("from", from_clause)

        from_clause.append("expressions", table_expr)
        return self
