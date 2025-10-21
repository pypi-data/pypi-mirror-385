"""Unit tests for the sqlspec.core.parameters module.

Tests the 2-Phase Parameter Conversion System:
- Phase 1: SQLGlot compatibility conversion
- Phase 2: Execution format conversion
- Multi-database parameter style support (10+ styles)
- Parameter container type preservation
- Performance and edge cases
"""

import math
from datetime import date, datetime
from decimal import Decimal
from typing import Any

import pytest

from sqlspec.core.parameters import (
    ParameterConverter,
    ParameterInfo,
    ParameterProcessor,
    ParameterStyle,
    ParameterStyleConfig,
    ParameterValidator,
    TypedParameter,
    is_iterable_parameters,
    wrap_with_type,
)

pytestmark = pytest.mark.xdist_group("core")


@pytest.mark.parametrize(
    "style,expected_value",
    [
        (ParameterStyle.NONE, "none"),
        (ParameterStyle.STATIC, "static"),
        (ParameterStyle.QMARK, "qmark"),
        (ParameterStyle.NUMERIC, "numeric"),
        (ParameterStyle.NAMED_COLON, "named_colon"),
        (ParameterStyle.POSITIONAL_COLON, "positional_colon"),
        (ParameterStyle.NAMED_AT, "named_at"),
        (ParameterStyle.NAMED_DOLLAR, "named_dollar"),
        (ParameterStyle.NAMED_PYFORMAT, "pyformat_named"),
        (ParameterStyle.POSITIONAL_PYFORMAT, "pyformat_positional"),
    ],
)
def test_parameter_style_values(style: ParameterStyle, expected_value: str) -> None:
    """Test ParameterStyle enum values match expected strings."""
    assert style.value == expected_value

    assert style == expected_value


def test_typed_parameter_basic() -> None:
    """Test basic TypedParameter creation and properties."""
    param = TypedParameter(True, bool, "is_active")

    assert param.value is True
    assert param.original_type is bool
    assert param.semantic_name == "is_active"


def test_typed_parameter_defaults() -> None:
    """Test TypedParameter with default values."""
    param = TypedParameter(42)

    assert param.value == 42
    assert param.original_type is int
    assert param.semantic_name is None


def test_typed_parameter_hash_equality() -> None:
    """Test TypedParameter hash and equality for dictionary operations."""
    param1 = TypedParameter(True, bool, "active")
    param2 = TypedParameter(True, bool, "active")
    param3 = TypedParameter(False, bool, "active")

    assert param1 == param2
    assert hash(param1) == hash(param2)

    assert param1 != param3

    first_hash = hash(param1)
    second_hash = hash(param1)
    assert first_hash == second_hash


def test_typed_parameter_repr() -> None:
    """Test TypedParameter string representation for debugging."""
    param = TypedParameter(Decimal("123.45"), Decimal, "price")
    repr_str = repr(param)

    assert "TypedParameter" in repr_str
    assert "123.45" in repr_str
    assert "Decimal" in repr_str
    assert "price" in repr_str


@pytest.mark.parametrize(
    "value,expected_type",
    [
        (True, bool),
        (False, bool),
        (42, int),
        ("test", str),
        (Decimal("12.34"), Decimal),
        (datetime(2023, 1, 1), datetime),
        (date(2023, 1, 1), date),
        ([1, 2, 3], list),
        ({"key": "value"}, dict),
    ],
)
def test_typed_parameter_with_different_types(value: Any, expected_type: type) -> None:
    """Test TypedParameter with different value types."""
    param = TypedParameter(value)
    assert param.original_type == expected_type
    assert param.value == value


def test_wrap_with_type_basic_types() -> None:
    """Test type wrapping for basic Python types."""

    bool_result = wrap_with_type(True, "is_active")
    assert isinstance(bool_result, TypedParameter)
    assert bool_result.value is True
    assert bool_result.original_type is bool
    assert bool_result.semantic_name == "is_active"

    decimal_result = wrap_with_type(Decimal("123.45"))
    assert isinstance(decimal_result, TypedParameter)
    assert decimal_result.value == Decimal("123.45")
    assert decimal_result.original_type == Decimal


def test_wrap_with_type_datetime_types() -> None:
    """Test type wrapping for date/datetime types."""
    test_date = date(2023, 1, 1)
    date_result = wrap_with_type(test_date)
    assert isinstance(date_result, TypedParameter)
    assert date_result.value == test_date
    assert date_result.original_type == date

    test_datetime = datetime(2023, 1, 1, 12, 0, 0)
    datetime_result = wrap_with_type(test_datetime)
    assert isinstance(datetime_result, TypedParameter)
    assert datetime_result.value == test_datetime
    assert datetime_result.original_type == datetime


def test_wrap_with_type_no_wrapping_needed() -> None:
    """Test types that don't need wrapping are returned unchanged."""

    assert wrap_with_type("test") == "test"
    assert wrap_with_type(42) == 42
    assert wrap_with_type(math.pi) == math.pi
    assert wrap_with_type(None) is None


@pytest.mark.parametrize(
    "name,style,position,ordinal,placeholder_text",
    [
        ("user_id", ParameterStyle.NAMED_COLON, 25, 0, ":user_id"),
        (None, ParameterStyle.QMARK, 10, 1, "?"),
        ("param1", ParameterStyle.NAMED_PYFORMAT, 35, 0, "%(param1)s"),
        (None, ParameterStyle.POSITIONAL_PYFORMAT, 15, 2, "%s"),
        ("id", ParameterStyle.NAMED_AT, 20, 0, "@id"),
        ("value", ParameterStyle.NAMED_DOLLAR, 30, 0, "$value"),
        ("1", ParameterStyle.NUMERIC, 5, 1, "$1"),
        ("2", ParameterStyle.POSITIONAL_COLON, 40, 3, ":2"),
    ],
)
def test_parameter_info_creation(
    name: str | None, style: ParameterStyle, position: int, ordinal: int, placeholder_text: str
) -> None:
    """Test ParameterInfo creation with various parameter types."""
    param_info = ParameterInfo(
        name=name, style=style, position=position, ordinal=ordinal, placeholder_text=placeholder_text
    )

    assert param_info.name == name
    assert param_info.style == style
    assert param_info.position == position
    assert param_info.ordinal == ordinal
    assert param_info.placeholder_text == placeholder_text


def test_mixed_named_and_numeric_parameters() -> None:
    """Test mixed named (:name) and numeric ($2) parameters."""
    sql = "SELECT :name::text as name, $2::int as age"
    parameters = {"name": "Mixed", "age": 25}

    converter = ParameterConverter()

    converted_sql, converted_params = converter.convert_placeholder_style(
        sql, parameters, ParameterStyle.NUMERIC, is_many=False
    )

    assert converted_sql == "SELECT $1::text as name, $2::int as age"
    assert converted_params == ("Mixed", 25)
    assert len(converted_params) == 2


def test_mixed_parameter_style_with_processor() -> None:
    """Test mixed parameter styles through the full processor pipeline."""
    sql = "SELECT :name::text as name, $2::int as age"
    parameters = {"name": "Test", "age": 30}

    config = ParameterStyleConfig(
        default_parameter_style=ParameterStyle.NUMERIC,
        supported_parameter_styles={ParameterStyle.NUMERIC, ParameterStyle.NAMED_COLON},
        default_execution_parameter_style=ParameterStyle.NUMERIC,
        supported_execution_parameter_styles={ParameterStyle.NUMERIC},
        allow_mixed_parameter_styles=False,
        preserve_parameter_format=True,
    )

    processor = ParameterProcessor()
    processed_sql, processed_params = processor.process(
        sql=sql, parameters=parameters, config=config, dialect="postgres", is_many=False
    )

    assert processed_sql == "SELECT $1::text as name, $2::int as age"
    assert processed_params == ("Test", 30)
    assert len(processed_params) == 2


def test_mixed_parameters_order_sensitivity() -> None:
    """Test that mixed parameters maintain correct order mapping."""

    sql = "SELECT $1::text as first, :middle::text as mid, $3::int as last"
    parameters = {"first": "A", "middle": "B", "last": "C"}

    converter = ParameterConverter()
    converted_sql, converted_params = converter.convert_placeholder_style(
        sql, parameters, ParameterStyle.NUMERIC, is_many=False
    )

    assert converted_sql == "SELECT $1::text as first, $2::text as mid, $3::int as last"

    assert converted_params == ("A", "B", "C")
    assert len(converted_params) == 3


def test_mixed_parameters_with_repeated_numeric() -> None:
    """Test mixed parameters with repeated numeric parameters."""
    sql = "SELECT :name::text as name, $2::int as age, $2::int as age2"
    parameters = {"name": "User", "age": 25}

    converter = ParameterConverter()
    converted_sql, converted_params = converter.convert_placeholder_style(
        sql, parameters, ParameterStyle.NUMERIC, is_many=False
    )

    assert converted_sql == "SELECT $1::text as name, $2::int as age, $2::int as age2"
    assert converted_params == ("User", 25)
    assert len(converted_params) == 2


def test_edge_case_all_numeric_parameters() -> None:
    """Test that non-mixed numeric parameters still work correctly."""
    sql = "SELECT $1::text as name, $2::int as age"
    parameters = ("Alice", 30)

    converter = ParameterConverter()
    converted_sql, converted_params = converter.convert_placeholder_style(
        sql, parameters, ParameterStyle.NUMERIC, is_many=False
    )

    assert converted_sql == "SELECT $1::text as name, $2::int as age"
    assert converted_params == ("Alice", 30)


def test_edge_case_all_named_parameters() -> None:
    """Test that non-mixed named parameters still work correctly."""
    sql = "SELECT :name::text as name, :age::int as age"
    parameters = {"name": "Bob", "age": 35}

    converter = ParameterConverter()
    converted_sql, converted_params = converter.convert_placeholder_style(
        sql, parameters, ParameterStyle.NUMERIC, is_many=False
    )

    assert converted_sql == "SELECT $1::text as name, $2::int as age"
    assert converted_params == ("Bob", 35)


def test_parameter_info_repr() -> None:
    """Test ParameterInfo string representation."""
    param = ParameterInfo("test_param", ParameterStyle.NAMED_COLON, 10, 0, ":test_param")
    repr_str = repr(param)

    assert "ParameterInfo" in repr_str
    assert "test_param" in repr_str
    assert "ParameterStyle.NAMED_COLON" in repr_str
    assert "10" in repr_str


def test_parameter_style_config_basic() -> None:
    """Test basic ParameterStyleConfig creation."""
    config = ParameterStyleConfig(ParameterStyle.QMARK)

    assert config.default_parameter_style == ParameterStyle.QMARK
    assert config.supported_parameter_styles == {ParameterStyle.QMARK}
    assert config.default_execution_parameter_style == ParameterStyle.QMARK
    assert config.type_coercion_map == {}
    assert not config.has_native_list_expansion
    assert config.output_transformer is None
    assert config.needs_static_script_compilation is False


def test_parameter_style_config_advanced() -> None:
    """Test ParameterStyleConfig with advanced options."""
    coercion_map: dict[type, Any] = {bool: lambda x: 1 if x else 0}

    def output_transformer(sql: str, params: Any) -> tuple[str, Any]:
        return (sql.upper(), params)

    config = ParameterStyleConfig(
        default_parameter_style=ParameterStyle.NAMED_COLON,
        supported_parameter_styles={ParameterStyle.NAMED_COLON, ParameterStyle.QMARK},
        supported_execution_parameter_styles={ParameterStyle.QMARK},
        default_execution_parameter_style=ParameterStyle.QMARK,
        type_coercion_map=coercion_map,
        has_native_list_expansion=True,
        output_transformer=output_transformer,
        needs_static_script_compilation=False,
        allow_mixed_parameter_styles=True,
        preserve_parameter_format=True,
    )

    assert config.default_parameter_style == ParameterStyle.NAMED_COLON
    assert config.supported_parameter_styles == {ParameterStyle.NAMED_COLON, ParameterStyle.QMARK}
    assert config.supported_execution_parameter_styles == {ParameterStyle.QMARK}
    assert config.default_execution_parameter_style == ParameterStyle.QMARK
    assert config.type_coercion_map == coercion_map
    assert config.has_native_list_expansion is True
    assert config.output_transformer == output_transformer
    assert config.needs_static_script_compilation is False
    assert config.allow_mixed_parameter_styles is True
    assert config.preserve_parameter_format is True


def test_parameter_style_config_hash() -> None:
    """Test ParameterStyleConfig hash method for caching."""
    config1 = ParameterStyleConfig(ParameterStyle.QMARK)
    config2 = ParameterStyleConfig(ParameterStyle.QMARK)
    config3 = ParameterStyleConfig(ParameterStyle.NAMED_COLON)

    assert config1.hash() == config2.hash()

    assert config1.hash() != config3.hash()


@pytest.fixture
def validator() -> ParameterValidator:
    """Create a ParameterValidator instance."""
    return ParameterValidator()


@pytest.mark.parametrize(
    "sql,expected_count,expected_styles",
    [
        ("SELECT * FROM users", 0, []),
        ("SELECT * FROM users WHERE id = ?", 1, [ParameterStyle.QMARK]),
        ("SELECT * FROM users WHERE name = :name", 1, [ParameterStyle.NAMED_COLON]),
        ("SELECT * FROM users WHERE id = ? AND name = ?", 2, [ParameterStyle.QMARK, ParameterStyle.QMARK]),
        (
            "SELECT * FROM users WHERE name = :name AND email = :email",
            2,
            [ParameterStyle.NAMED_COLON, ParameterStyle.NAMED_COLON],
        ),
        ("SELECT * FROM users WHERE id = %(id)s", 1, [ParameterStyle.NAMED_PYFORMAT]),
        ("SELECT * FROM users WHERE name = %s", 1, [ParameterStyle.POSITIONAL_PYFORMAT]),
        ("SELECT * FROM users WHERE id = @id", 1, [ParameterStyle.NAMED_AT]),
        ("SELECT * FROM users WHERE id = $1", 1, [ParameterStyle.NUMERIC]),
        ("SELECT * FROM users WHERE name = $name", 1, [ParameterStyle.NAMED_DOLLAR]),
        ("SELECT * FROM users WHERE id = :1", 1, [ParameterStyle.POSITIONAL_COLON]),
    ],
)
def test_extract_parameters(
    validator: ParameterValidator, sql: str, expected_count: int, expected_styles: list[ParameterStyle]
) -> None:
    """Test parameter extraction from various SQL patterns."""
    parameters = validator.extract_parameters(sql)

    assert len(parameters) == expected_count
    for i, expected_style in enumerate(expected_styles):
        assert parameters[i].style == expected_style


@pytest.mark.parametrize(
    "sql,should_be_ignored",
    [
        ("SELECT 'test with ? inside'", True),
        ('SELECT "test with ? inside"', True),
        ("SELECT $tag$content with ? and :param$tag$", True),
        ("SELECT * FROM test -- comment with ? and :param", True),
        ("SELECT * FROM test /* comment with ? and :param */", True),
        ("SELECT * FROM json WHERE data ?? 'key'", True),
        ("SELECT * FROM json WHERE data ?| array['key']", True),
        ("SELECT * FROM json WHERE data ?& array['key']", True),
        ("SELECT * FROM users WHERE id::int = 5", False),
    ],
)
def test_extract_parameters_ignores_special_cases(
    validator: ParameterValidator, sql: str, should_be_ignored: bool
) -> None:
    """Test that parameters in special contexts are handled correctly."""
    parameters = validator.extract_parameters(sql)

    if should_be_ignored:
        assert len(parameters) == 0
    else:
        assert all(p.placeholder_text != "::int" for p in parameters)


def test_extract_parameters_caching(validator: ParameterValidator) -> None:
    """Test that parameter extraction results are cached."""
    sql = "SELECT * FROM users WHERE id = ? AND name = :name"

    parameters1 = validator.extract_parameters(sql)
    parameters2 = validator.extract_parameters(sql)

    assert parameters1 is parameters2


def test_extract_parameters_complex_sql(validator: ParameterValidator) -> None:
    """Test parameter extraction from complex SQL with multiple styles."""
    sql = """
    SELECT u.*, o.*
    FROM users u
    JOIN orders o ON u.id = o.user_id
    WHERE u.name = :name
      AND u.email = %(email)s
      AND o.created_at > ?
      AND o.status = @status
      AND o.total > $1
    """
    parameters = validator.extract_parameters(sql)

    assert len(parameters) == 5
    styles = {p.style for p in parameters}
    assert ParameterStyle.NAMED_COLON in styles
    assert ParameterStyle.NAMED_PYFORMAT in styles
    assert ParameterStyle.QMARK in styles
    assert ParameterStyle.NAMED_AT in styles

    assert ParameterStyle.NUMERIC in styles


def test_parameter_position_tracking(validator: ParameterValidator) -> None:
    """Test that parameter positions are tracked correctly."""
    sql = "SELECT * FROM users WHERE id = ? AND name = :name"
    parameters = validator.extract_parameters(sql)

    assert len(parameters) == 2
    qmark_param = next(p for p in parameters if p.style == ParameterStyle.QMARK)
    named_param = next(p for p in parameters if p.style == ParameterStyle.NAMED_COLON)

    assert qmark_param.position < named_param.position
    assert sql[qmark_param.position] == "?"
    assert sql[named_param.position : named_param.position + len(":name")] == ":name"


@pytest.mark.parametrize(
    "dialect,expected_incompatible",
    [
        (None, {ParameterStyle.POSITIONAL_PYFORMAT, ParameterStyle.NAMED_PYFORMAT, ParameterStyle.POSITIONAL_COLON}),
        ("mysql", {ParameterStyle.POSITIONAL_PYFORMAT, ParameterStyle.NAMED_PYFORMAT, ParameterStyle.POSITIONAL_COLON}),
        ("postgres", {ParameterStyle.POSITIONAL_COLON}),
        ("sqlite", {ParameterStyle.POSITIONAL_COLON}),
        (
            "oracle",
            {ParameterStyle.POSITIONAL_PYFORMAT, ParameterStyle.NAMED_PYFORMAT, ParameterStyle.POSITIONAL_COLON},
        ),
        (
            "bigquery",
            {ParameterStyle.POSITIONAL_PYFORMAT, ParameterStyle.NAMED_PYFORMAT, ParameterStyle.POSITIONAL_COLON},
        ),
    ],
)
def test_get_sqlglot_incompatible_styles(
    validator: ParameterValidator, dialect: str | None, expected_incompatible: set[ParameterStyle]
) -> None:
    """Test dialect-specific SQLGlot incompatible style detection."""
    incompatible = validator.get_sqlglot_incompatible_styles(dialect)
    assert incompatible == expected_incompatible


@pytest.fixture
def converter() -> ParameterConverter:
    """Create a ParameterConverter instance."""
    return ParameterConverter()


@pytest.mark.parametrize(
    "sql,dialect,expected_needs_conversion",
    [
        ("SELECT * FROM users WHERE id = ?", "postgres", False),
        ("SELECT * FROM users WHERE id = :name", "postgres", False),
        ("SELECT * FROM users WHERE id = %s", "postgres", False),
        ("SELECT * FROM users WHERE id = %s", "mysql", True),
        ("SELECT * FROM users WHERE id = %(name)s", "mysql", True),
        ("SELECT * FROM users WHERE id = :1", "postgres", True),
        ("SELECT * FROM users WHERE id = :1", "oracle", True),
    ],
)
def test_normalize_sql_for_parsing(
    converter: ParameterConverter, sql: str, dialect: str, expected_needs_conversion: bool
) -> None:
    """Test Phase 1 SQLGlot compatibility normalization."""
    normalized_sql, param_info = converter.normalize_sql_for_parsing(sql, dialect)

    if expected_needs_conversion:
        assert normalized_sql != sql

        assert ":param_" in normalized_sql
    else:
        assert normalized_sql == sql

    assert len(param_info) > 0


def test_normalize_sql_pyformat_conversion(converter: ParameterConverter) -> None:
    """Test conversion of problematic pyformat styles."""
    sql = "SELECT * FROM users WHERE name = %s AND id = %(user_id)s"
    normalized_sql, param_info = converter.normalize_sql_for_parsing(sql, "mysql")

    assert "%s" not in normalized_sql
    assert "%(user_id)s" not in normalized_sql
    assert ":param_0" in normalized_sql
    assert ":param_1" in normalized_sql

    assert len(param_info) == 2
    assert param_info[0].style == ParameterStyle.POSITIONAL_PYFORMAT
    assert param_info[1].style == ParameterStyle.NAMED_PYFORMAT
    assert param_info[1].name == "user_id"


def test_normalize_sql_positional_colon_conversion(converter: ParameterConverter) -> None:
    """Test conversion of Oracle-style positional colon parameters."""
    sql = "SELECT * FROM users WHERE id = :1 AND name = :2"
    normalized_sql, param_info = converter.normalize_sql_for_parsing(sql, "oracle")

    assert ":1" not in normalized_sql
    assert ":2" not in normalized_sql
    assert ":param_0" in normalized_sql
    assert ":param_1" in normalized_sql

    assert len(param_info) == 2
    assert param_info[0].style == ParameterStyle.POSITIONAL_COLON
    assert param_info[1].style == ParameterStyle.POSITIONAL_COLON


@pytest.mark.parametrize(
    "sql,parameters,target_style,expected_sql_pattern,expected_param_format",
    [
        ("SELECT * FROM users WHERE name = :param_0", ["john"], ParameterStyle.QMARK, "?", list),
        ("SELECT * FROM users WHERE name = :param_0", ["john"], ParameterStyle.NUMERIC, "$1", list),
        ("SELECT * FROM users WHERE name = :param_0", ["john"], ParameterStyle.POSITIONAL_PYFORMAT, "%s", list),
        ("SELECT * FROM users WHERE id = ?", {"id": 123}, ParameterStyle.NAMED_COLON, ":param_0", dict),
        ("SELECT * FROM users WHERE id = ?", {"id": 123}, ParameterStyle.NAMED_PYFORMAT, "%(param_0)s", dict),
        ("SELECT * FROM users WHERE id = ?", {"id": 123}, ParameterStyle.NAMED_AT, "@param_0", dict),
    ],
)
def test_convert_placeholder_style(
    converter: ParameterConverter,
    sql: str,
    parameters: Any,
    target_style: ParameterStyle,
    expected_sql_pattern: str,
    expected_param_format: type,
) -> None:
    """Test Phase 2 execution format conversion."""
    converted_sql, converted_params = converter.convert_placeholder_style(sql, parameters, target_style)

    assert expected_sql_pattern in converted_sql
    assert isinstance(converted_params, expected_param_format)


def test_convert_static_embedding(converter: ParameterConverter) -> None:
    """Test STATIC style parameter embedding."""
    sql = "SELECT * FROM users WHERE id = ? AND active = ?"
    parameters = [123, True]

    converted_sql, converted_params = converter.convert_placeholder_style(sql, parameters, ParameterStyle.STATIC)

    assert "123" in converted_sql
    assert "TRUE" in converted_sql
    assert "?" not in converted_sql
    assert converted_params is None


def test_convert_static_embedding_parameter_reuse(converter: ParameterConverter) -> None:
    """Test STATIC style parameter embedding with parameter reuse."""

    sql = "SELECT $1, $2, $1, $3, $1"
    parameters = [100, 200, 300]

    converted_sql, converted_params = converter.convert_placeholder_style(sql, parameters, ParameterStyle.STATIC)

    expected = "SELECT 100, 200, 100, 300, 100"
    assert converted_sql == expected
    assert converted_params is None

    sql_named = "SELECT :value, :other, :value"
    params_named = {"value": "hello", "other": 42}

    converted_sql_named, converted_params_named = converter.convert_placeholder_style(
        sql_named, params_named, ParameterStyle.STATIC
    )

    expected_named = "SELECT 'hello', 42, 'hello'"
    assert converted_sql_named == expected_named
    assert converted_params_named is None


def test_convert_parameter_format_preservation(converter: ParameterConverter) -> None:
    """Test parameter format preservation (list vs tuple vs dict)."""
    sql = "SELECT * FROM users WHERE id = ? AND name = ?"

    tuple_params = (123, "john")
    _, converted_params = converter.convert_placeholder_style(sql, tuple_params, ParameterStyle.QMARK)

    assert isinstance(converted_params, (list, tuple))
    assert len(converted_params) == 2


def test_convert_executemany_handling(converter: ParameterConverter) -> None:
    """Test execute_many parameter handling."""
    sql = "INSERT INTO users (id, name) VALUES (?, ?)"
    many_parameters = [[1, "alice"], [2, "bob"], [3, "charlie"]]

    converted_sql, converted_params = converter.convert_placeholder_style(
        sql, many_parameters, ParameterStyle.QMARK, is_many=True
    )

    assert "?" in converted_sql
    assert converted_params == many_parameters


@pytest.fixture
def processor() -> ParameterProcessor:
    """Create a ParameterProcessor instance."""
    return ParameterProcessor()


@pytest.fixture
def basic_config() -> ParameterStyleConfig:
    """Create a basic parameter style configuration."""
    return ParameterStyleConfig(ParameterStyle.QMARK)


@pytest.fixture
def advanced_config() -> ParameterStyleConfig:
    """Create an advanced parameter style configuration."""
    return ParameterStyleConfig(
        default_parameter_style=ParameterStyle.NAMED_COLON,
        supported_parameter_styles={ParameterStyle.NAMED_COLON, ParameterStyle.QMARK},
        default_execution_parameter_style=ParameterStyle.QMARK,
        type_coercion_map={bool: lambda x: 1 if x else 0},
        output_transformer=lambda sql, params: (sql.upper(), params),
    )


def test_process_no_parameters(processor: ParameterProcessor, basic_config: ParameterStyleConfig) -> None:
    """Test processing SQL with no parameters (fast path)."""
    sql = "SELECT * FROM users"

    final_sql, final_params = processor.process(sql, None, basic_config)

    assert final_sql == sql
    assert final_params is None


def test_process_type_wrapping(processor: ParameterProcessor, basic_config: ParameterStyleConfig) -> None:
    """Test type wrapping in parameter processing."""
    sql = "SELECT * FROM users WHERE active = ?"
    parameters = [True]

    final_sql, final_params = processor.process(sql, parameters, basic_config)

    assert final_sql == sql
    assert len(final_params) == 1


def test_process_type_coercion(processor: ParameterProcessor, advanced_config: ParameterStyleConfig) -> None:
    """Test type coercion mapping."""
    sql = "SELECT * FROM users WHERE active = :active"
    parameters = {"active": True}

    _, final_params = processor.process(sql, parameters, advanced_config, "postgres")

    if isinstance(final_params, dict):
        value = final_params["active"]

        if hasattr(value, "value"):
            assert value.value == 1 or value.value is True
        else:
            assert value == 1 or value is True
    elif isinstance(final_params, (list, tuple)):
        found_coerced = False
        for param in final_params:
            if hasattr(param, "value"):
                if param.value == 1 or param.value is True:
                    found_coerced = True
                    break
            elif param == 1 or param is True:
                found_coerced = True
                break
        assert found_coerced


def test_process_output_transformation(processor: ParameterProcessor, advanced_config: ParameterStyleConfig) -> None:
    """Test final output transformation."""
    sql = "select * from users where id = :id"
    parameters = {"id": 123}

    final_sql, final_params = processor.process(sql, parameters, advanced_config, "postgres")

    assert final_sql.isupper()
    assert "SELECT" in final_sql

    if isinstance(final_params, dict):
        assert final_params["id"] == 123
    elif isinstance(final_params, (list, tuple)):
        assert 123 in final_params


def test_process_full_pipeline(processor: ParameterProcessor) -> None:
    """Test complete processing pipeline with complex scenario."""

    config = ParameterStyleConfig(
        default_parameter_style=ParameterStyle.NAMED_PYFORMAT,
        default_execution_parameter_style=ParameterStyle.QMARK,
        type_coercion_map={bool: lambda x: 1 if x else 0, Decimal: lambda x: float(x)},
    )

    sql = "SELECT * FROM orders WHERE active = %(active)s AND total > %(total)s"
    parameters = {"active": True, "total": Decimal("99.99")}

    final_sql, final_params = processor.process(sql, parameters, config, "mysql")

    assert "?" in final_sql
    assert "%(active)s" not in final_sql
    assert "%(total)s" not in final_sql

    if final_params is None or (isinstance(final_params, dict) and len(final_params) == 0):
        pass
    elif isinstance(final_params, list):
        assert len(final_params) > 0
    elif isinstance(final_params, dict):
        assert len(final_params) > 0
    elif isinstance(final_params, tuple):
        assert len(final_params) > 0


def test_list_parameter_preservation(converter: ParameterConverter) -> None:
    """Test that list parameters are properly handled."""
    sql = "INSERT INTO users (id, name, active) VALUES (?, ?, ?)"
    parameters = [1, "alice", True]

    _, converted_params = converter.convert_placeholder_style(sql, parameters, ParameterStyle.QMARK)

    assert isinstance(converted_params, list)
    assert converted_params == parameters


def test_tuple_parameter_handling(converter: ParameterConverter) -> None:
    """Test that tuple parameters are handled correctly."""
    sql = "INSERT INTO users (id, name) VALUES (?, ?)"
    parameters = (1, "alice")

    _, converted_params = converter.convert_placeholder_style(sql, parameters, ParameterStyle.QMARK)

    assert isinstance(converted_params, (list, tuple))
    assert len(converted_params) == 2


def test_dict_parameter_handling(converter: ParameterConverter) -> None:
    """Test that dictionary parameters work with named styles."""
    sql = "INSERT INTO users (id, name) VALUES (:id, :name)"
    parameters = {"id": 1, "name": "alice"}

    _, converted_params = converter.convert_placeholder_style(sql, parameters, ParameterStyle.NAMED_COLON)

    assert isinstance(converted_params, dict)
    assert converted_params == parameters


@pytest.mark.parametrize(
    "database,input_style,output_style,sql_pattern,param_pattern",
    [
        ("sqlite", ParameterStyle.NAMED_COLON, ParameterStyle.QMARK, "?", list),
        ("postgresql", ParameterStyle.QMARK, ParameterStyle.NUMERIC, "$1", list),
        ("mysql", ParameterStyle.QMARK, ParameterStyle.POSITIONAL_PYFORMAT, "%s", list),
        ("oracle", ParameterStyle.QMARK, ParameterStyle.POSITIONAL_COLON, ":1", dict),
        ("sqlserver", ParameterStyle.QMARK, ParameterStyle.NAMED_AT, "@param", dict),
        ("postgresql", ParameterStyle.QMARK, ParameterStyle.NAMED_DOLLAR, "$param", dict),
    ],
)
def test_database_specific_parameter_conversion(
    converter: ParameterConverter,
    database: str,
    input_style: ParameterStyle,
    output_style: ParameterStyle,
    sql_pattern: str,
    param_pattern: type,
) -> None:
    """Test parameter conversion for specific database requirements."""

    assert database is not None
    assert param_pattern is not None

    sql = "SELECT * FROM users WHERE id = :id"
    parameters = {"id": 123}

    if input_style != ParameterStyle.NAMED_COLON:
        sql, parameters = converter.convert_placeholder_style(sql, parameters, input_style)

    final_sql, final_params = converter.convert_placeholder_style(sql, parameters, output_style)

    assert sql_pattern in final_sql

    assert final_params is not None


def test_mixed_style_detection(validator: ParameterValidator) -> None:
    """Test detection of mixed parameter styles."""
    sql = "SELECT * FROM users WHERE id = ? AND name = :name AND email = %(email)s"
    parameters = validator.extract_parameters(sql)

    assert len(parameters) == 3
    styles = {p.style for p in parameters}
    assert ParameterStyle.QMARK in styles
    assert ParameterStyle.NAMED_COLON in styles
    assert ParameterStyle.NAMED_PYFORMAT in styles


def test_mixed_style_normalization() -> None:
    """Test normalization of mixed parameter styles."""
    converter = ParameterConverter()
    sql = "SELECT * FROM users WHERE id = ? AND name = :name AND status = %(status)s"

    normalized_sql, _ = converter.normalize_sql_for_parsing(sql, "mysql")

    assert "?" in normalized_sql
    assert ":name" in normalized_sql
    assert "%(status)s" not in normalized_sql
    assert ":param_" in normalized_sql


def test_parameter_caching() -> None:
    """Test that parameter extraction is cached."""
    validator = ParameterValidator()
    sql = "SELECT * FROM users WHERE id = ? AND name = :name"

    params1 = validator.extract_parameters(sql)

    params2 = validator.extract_parameters(sql)

    assert params1 is params2


def test_singledispatch_type_wrapping_performance() -> None:
    """Test that singledispatch provides efficient type-based dispatch."""

    bool_result = wrap_with_type(True)
    decimal_result = wrap_with_type(Decimal("123.45"))
    string_result = wrap_with_type("test")

    assert isinstance(bool_result, TypedParameter)
    assert isinstance(decimal_result, TypedParameter)

    assert string_result == "test"
    assert not isinstance(string_result, TypedParameter)


def test_hash_map_placeholder_generation() -> None:
    """Test that placeholder generation uses O(1) hash map lookups."""
    converter = ParameterConverter()

    supported_styles = [
        ParameterStyle.QMARK,
        ParameterStyle.NUMERIC,
        ParameterStyle.POSITIONAL_PYFORMAT,
        ParameterStyle.NAMED_COLON,
        ParameterStyle.NAMED_PYFORMAT,
        ParameterStyle.NAMED_AT,
    ]

    for style in supported_styles:
        sql = "SELECT * FROM users WHERE id = :param_0"
        parameters = ["test_value"]

        converted_sql, converted_params = converter.convert_placeholder_style(sql, parameters, style)

        assert converted_sql is not None
        assert converted_params is not None


def test_empty_sql_handling(validator: ParameterValidator) -> None:
    """Test handling of empty SQL strings."""
    parameters = validator.extract_parameters("")
    assert len(parameters) == 0


def test_null_parameter_handling(converter: ParameterConverter) -> None:
    """Test handling of null parameters."""
    sql = "SELECT * FROM users WHERE deleted_at = ?"
    parameters = [None]

    converted_sql, converted_params = converter.convert_placeholder_style(sql, parameters, ParameterStyle.STATIC)

    assert "NULL" in converted_sql
    assert "?" not in converted_sql
    assert converted_params is None


def test_complex_data_types(converter: ParameterConverter) -> None:
    """Test handling of complex data types."""
    sql = "INSERT INTO products (data) VALUES (?)"
    complex_data = {
        "name": "Product",
        "price": Decimal("99.99"),
        "available": True,
        "tags": ["electronics", "gadget"],
        "created": datetime(2023, 1, 1, 12, 0, 0),
    }
    parameters = [complex_data]

    _, converted_params = converter.convert_placeholder_style(sql, parameters, ParameterStyle.QMARK)

    assert isinstance(converted_params, list)
    assert len(converted_params) == 1

    assert converted_params[0] == complex_data


def test_parameter_ordinal_assignment(validator: ParameterValidator) -> None:
    """Test that parameter ordinals are assigned correctly."""
    sql = "SELECT * FROM users WHERE id = ? AND name = ? AND email = ?"
    parameters = validator.extract_parameters(sql)

    assert len(parameters) == 3
    assert parameters[0].ordinal == 0
    assert parameters[1].ordinal == 1
    assert parameters[2].ordinal == 2


def test_large_parameter_count(validator: ParameterValidator) -> None:
    """Test handling of SQL with many parameters."""

    placeholders = ", ".join("?" for _ in range(50))
    sql = f"INSERT INTO test_table (col1, col2, ...) VALUES ({placeholders})"

    parameters = validator.extract_parameters(sql)
    assert len(parameters) == 50

    for i, param in enumerate(parameters):
        assert param.ordinal == i


@pytest.mark.parametrize(
    "obj,expected",
    [
        ([1, 2, 3], True),
        ((1, 2, 3), True),
        ({1, 2, 3}, True),
        ({"a": 1}, False),
        ("string", False),
        (b"bytes", False),
        (123, False),
        (None, False),
    ],
)
def test_is_iterable_parameters(obj: Any, expected: bool) -> None:
    """Test is_iterable_parameters helper function."""
    assert is_iterable_parameters(obj) == expected


def test_sqlite_compatibility(validator: ParameterValidator) -> None:
    """Test SQLite parameter style compatibility."""

    incompatible = validator.get_sqlglot_incompatible_styles("sqlite")
    assert ParameterStyle.POSITIONAL_COLON in incompatible
    assert ParameterStyle.QMARK not in incompatible
    assert ParameterStyle.NAMED_COLON not in incompatible


def test_postgresql_compatibility(validator: ParameterValidator) -> None:
    """Test PostgreSQL parameter style compatibility."""

    incompatible = validator.get_sqlglot_incompatible_styles("postgres")
    assert incompatible == {ParameterStyle.POSITIONAL_COLON}


def test_mysql_compatibility(validator: ParameterValidator) -> None:
    """Test MySQL parameter style compatibility."""

    incompatible = validator.get_sqlglot_incompatible_styles("mysql")
    assert ParameterStyle.POSITIONAL_PYFORMAT in incompatible
    assert ParameterStyle.NAMED_PYFORMAT in incompatible
    assert ParameterStyle.POSITIONAL_COLON in incompatible


def test_oracle_compatibility(validator: ParameterValidator) -> None:
    """Test Oracle parameter style compatibility."""

    incompatible = validator.get_sqlglot_incompatible_styles("oracle")
    assert ParameterStyle.POSITIONAL_COLON in incompatible
    assert ParameterStyle.POSITIONAL_PYFORMAT in incompatible
    assert ParameterStyle.NAMED_PYFORMAT in incompatible


def test_dollar_numeric_vs_named_disambiguation() -> None:
    """Test differentiation between $1 (numeric) and $name (named)."""
    validator = ParameterValidator()
    sql = "SELECT * FROM users WHERE id = $1 AND name = $username"
    parameters = validator.extract_parameters(sql)

    assert len(parameters) == 2

    dollar_1_param = next(p for p in parameters if p.placeholder_text == "$1")
    dollar_username_param = next(p for p in parameters if p.placeholder_text == "$username")

    assert dollar_1_param.style == ParameterStyle.NUMERIC
    assert dollar_username_param.style == ParameterStyle.NAMED_DOLLAR
    assert dollar_1_param.name == "1"
    assert dollar_username_param.name == "username"


def test_positional_colon_oracle_style() -> None:
    """Test Oracle-style positional colon parameters (:1, :2, :3)."""
    validator = ParameterValidator()
    sql = "SELECT * FROM users WHERE id = :1 AND name = :2 AND active = :3"
    parameters = validator.extract_parameters(sql)

    assert len(parameters) == 3
    assert all(p.style == ParameterStyle.POSITIONAL_COLON for p in parameters)
    assert parameters[0].placeholder_text == ":1"
    assert parameters[1].placeholder_text == ":2"
    assert parameters[2].placeholder_text == ":3"
    assert parameters[0].name == "1"
    assert parameters[1].name == "2"
    assert parameters[2].name == "3"


def test_preserve_parameter_names_in_conversion(converter: ParameterConverter) -> None:
    """Test that parameter names are preserved during conversion."""
    sql = "SELECT * FROM users WHERE name = :user_name AND email = :user_email"
    parameters = {"user_name": "alice", "user_email": "alice@example.com"}

    converted_sql, converted_params = converter.convert_placeholder_style(
        sql, parameters, ParameterStyle.NAMED_PYFORMAT
    )

    assert "%(user_name)s" in converted_sql
    assert "%(user_email)s" in converted_sql
    assert isinstance(converted_params, dict)
    assert converted_params["user_name"] == "alice"
    assert converted_params["user_email"] == "alice@example.com"


def test_duplicate_named_parameters_named_colon_to_numeric(converter: ParameterConverter) -> None:
    """Test conversion from named colon parameters with duplicates to numeric style.

    This reproduces the issue described in the bug report where duplicate named
    parameters cause incorrect parameter counting.
    """
    # SQL with duplicate :embedding parameter (appears twice)
    sql = "SELECT id, name, 1 - (embedding <=> :embedding) AS similarity FROM items WHERE 1 - (embedding <=> :embedding) > :threshold ORDER BY similarity DESC LIMIT :limit"

    parameters = {"embedding": [0.1, 0.2, 0.3], "threshold": 0.5, "limit": 10}

    converted_sql, converted_params = converter.convert_placeholder_style(sql, parameters, ParameterStyle.NUMERIC)

    # Should have exactly 3 parameters, not 4
    assert isinstance(converted_params, (list, tuple))
    assert len(converted_params) == 3

    # Check the SQL has correct numeric placeholders
    assert "$1" in converted_sql
    assert "$2" in converted_sql
    assert "$3" in converted_sql
    assert "$4" not in converted_sql  # Should not have a 4th parameter

    # Check parameter values are correct
    assert converted_params[0] == [0.1, 0.2, 0.3]  # embedding value appears once
    assert converted_params[1] == 0.5  # threshold
    assert converted_params[2] == 10  # limit


def test_duplicate_named_parameters_various_styles(converter: ParameterConverter) -> None:
    """Test duplicate parameter handling with various parameter styles."""
    test_cases = [
        {
            "style": ParameterStyle.NAMED_AT,
            "sql": "SELECT * FROM table WHERE col1 = @param AND col2 = @param",
            "expected_placeholders": ["@param"],
        },
        {
            "style": ParameterStyle.NAMED_DOLLAR,
            "sql": "SELECT * FROM table WHERE col1 = $param AND col2 = $param",
            "expected_placeholders": ["$param"],
        },
        {
            "style": ParameterStyle.NAMED_PYFORMAT,
            "sql": "SELECT * FROM table WHERE col1 = %(param)s AND col2 = %(param)s",
            "expected_placeholders": ["%(param)s"],
        },
    ]

    for case in test_cases:
        parameters = {"param": "test_value"}

        converted_sql, converted_params = converter.convert_placeholder_style(
            case["sql"],  # type: ignore[arg-type]
            parameters,
            ParameterStyle.NUMERIC,
        )

        # Should convert to single numeric parameter
        assert isinstance(converted_params, (list, tuple))
        assert len(converted_params) == 1
        assert converted_params[0] == "test_value"

        # Should have $1 twice in the SQL
        assert converted_sql.count("$1") == 2
        assert "$2" not in converted_sql


def test_duplicate_parameters_mixed_with_unique(converter: ParameterConverter) -> None:
    """Test duplicate parameters mixed with unique parameters."""
    sql = "SELECT :a, :b, :a, :c, :b"
    parameters = {"a": 1, "b": 2, "c": 3}

    converted_sql, converted_params = converter.convert_placeholder_style(sql, parameters, ParameterStyle.NUMERIC)

    # Should have exactly 3 unique parameters
    assert isinstance(converted_params, (list, tuple))
    assert len(converted_params) == 3

    # Check the correct values are extracted
    assert 1 in converted_params  # a
    assert 2 in converted_params  # b
    assert 3 in converted_params  # c

    # Check SQL has correct numeric placeholders in the right positions
    # Original: :a, :b, :a, :c, :b
    # Should become: $1, $2, $1, $3, $2
    expected_positions = ["$1", "$2", "$1", "$3", "$2"]

    # Extract placeholder positions from converted SQL
    import re

    placeholders_in_sql = [match.group() for match in re.finditer(r"\$\d+", converted_sql)]

    assert placeholders_in_sql == expected_positions


def test_duplicate_parameters_qmark_to_numeric(converter: ParameterConverter) -> None:
    """Test duplicate qmark parameters conversion (edge case)."""
    # This is a different case - qmark parameters are positional so duplicates would be different values
    sql = "SELECT * FROM table WHERE col1 = ? AND col2 = ?"
    parameters = [1, 2]

    converted_sql, converted_params = converter.convert_placeholder_style(sql, parameters, ParameterStyle.NUMERIC)

    # Should have 2 parameters as they're positional
    assert isinstance(converted_params, (list, tuple))
    assert len(converted_params) == 2
    assert list(converted_params) == [1, 2]

    assert "$1" in converted_sql
    assert "$2" in converted_sql


def test_vector_similarity_search_example(converter: ParameterConverter) -> None:
    """Test the exact example from the bug report."""
    sql = """SELECT
    id,
    name,
    1 - (embedding <=> :embedding) as similarity
FROM
    items
WHERE
    1 - (embedding <=> :embedding) > :threshold
ORDER BY
    similarity DESC
LIMIT
    :limit"""

    parameters = {"embedding": [0.1, 0.2, 0.3], "threshold": 0.5, "limit": 10}

    _converted_sql, converted_params = converter.convert_placeholder_style(sql, parameters, ParameterStyle.NUMERIC)

    # Should have exactly 3 parameters despite :embedding appearing twice
    assert isinstance(converted_params, (list, tuple))
    assert len(converted_params) == 3

    # Verify parameter values
    assert [0.1, 0.2, 0.3] in converted_params
    assert 0.5 in converted_params
    assert 10 in converted_params


def test_parameter_processor_duplicate_handling(processor: ParameterProcessor) -> None:
    """Test the full parameter processor with duplicate parameters."""
    config = ParameterStyleConfig(
        default_parameter_style=ParameterStyle.NAMED_COLON, default_execution_parameter_style=ParameterStyle.NUMERIC
    )

    sql = "SELECT :param1, :param2, :param1 WHERE id = :param2"
    parameters = {"param1": "value1", "param2": "value2"}

    _processed_sql, processed_params = processor.process(sql, parameters, config, dialect="postgres")

    # Should have exactly 2 unique parameters
    assert isinstance(processed_params, (list, tuple))
    assert len(processed_params) == 2
    assert "value1" in processed_params
    assert "value2" in processed_params
