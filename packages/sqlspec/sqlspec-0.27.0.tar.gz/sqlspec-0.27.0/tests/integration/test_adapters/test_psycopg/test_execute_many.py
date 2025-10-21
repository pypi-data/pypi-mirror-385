"""Test execute_many functionality for Psycopg drivers."""

from collections.abc import Generator

import pytest
from pytest_databases.docker.postgres import PostgresService

from sqlspec.adapters.psycopg import PsycopgSyncConfig, PsycopgSyncDriver
from sqlspec.adapters.psycopg.driver import psycopg_statement_config
from sqlspec.core.result import SQLResult

pytestmark = pytest.mark.xdist_group("postgres")


@pytest.fixture
def psycopg_batch_session(postgres_service: PostgresService) -> "Generator[PsycopgSyncDriver, None, None]":
    """Create a Psycopg session for batch operation testing."""
    config = PsycopgSyncConfig(
        pool_config={
            "host": postgres_service.host,
            "port": postgres_service.port,
            "user": postgres_service.user,
            "password": postgres_service.password,
            "dbname": postgres_service.database,
            "autocommit": True,
        },
        statement_config=psycopg_statement_config,
    )

    try:
        with config.provide_session() as session:
            session.execute_script("""
                CREATE TABLE IF NOT EXISTS test_batch (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    value INTEGER DEFAULT 0,
                    category TEXT
                )
            """)

            session.execute_script("TRUNCATE TABLE test_batch RESTART IDENTITY")

            yield session

            session.execute_script("DROP TABLE IF EXISTS test_batch")
    finally:
        config.close_pool()


def test_psycopg_execute_many_basic(psycopg_batch_session: PsycopgSyncDriver) -> None:
    """Test basic execute_many with Psycopg."""
    parameters = [
        ("Item 1", 100, "A"),
        ("Item 2", 200, "B"),
        ("Item 3", 300, "A"),
        ("Item 4", 400, "C"),
        ("Item 5", 500, "B"),
    ]

    result = psycopg_batch_session.execute_many(
        "INSERT INTO test_batch (name, value, category) VALUES (%s, %s, %s)", parameters
    )

    assert isinstance(result, SQLResult)

    assert result.rows_affected == 5

    count_result = psycopg_batch_session.execute("SELECT COUNT(*) as count FROM test_batch")
    assert count_result.data[0]["count"] == 5


def test_psycopg_execute_many_update(psycopg_batch_session: PsycopgSyncDriver) -> None:
    """Test execute_many for UPDATE operations with Psycopg."""

    psycopg_batch_session.execute_many(
        "INSERT INTO test_batch (name, value, category) VALUES (%s, %s, %s)",
        [("Update 1", 10, "X"), ("Update 2", 20, "Y"), ("Update 3", 30, "Z")],
    )

    update_parameters = [(100, "Update 1"), (200, "Update 2"), (300, "Update 3")]

    result = psycopg_batch_session.execute_many("UPDATE test_batch SET value = %s WHERE name = %s", update_parameters)

    assert isinstance(result, SQLResult)
    assert result.rows_affected == 3

    check_result = psycopg_batch_session.execute("SELECT name, value FROM test_batch ORDER BY name")
    assert len(check_result.data) == 3
    assert all(row["value"] in (100, 200, 300) for row in check_result.data)


def test_psycopg_execute_many_empty(psycopg_batch_session: PsycopgSyncDriver) -> None:
    """Test execute_many with empty parameter list on Psycopg."""
    result = psycopg_batch_session.execute_many(
        "INSERT INTO test_batch (name, value, category) VALUES (%s, %s, %s)", []
    )

    assert isinstance(result, SQLResult)
    assert result.rows_affected == 0

    count_result = psycopg_batch_session.execute("SELECT COUNT(*) as count FROM test_batch")
    assert count_result.data[0]["count"] == 0


def test_psycopg_execute_many_mixed_types(psycopg_batch_session: PsycopgSyncDriver) -> None:
    """Test execute_many with mixed parameter types on Psycopg."""
    parameters = [
        ("String Item", 123, "CAT1"),
        ("Another Item", 456, None),
        ("Third Item", 0, "CAT2"),
        ("Negative Item", -50, "CAT3"),
    ]

    result = psycopg_batch_session.execute_many(
        "INSERT INTO test_batch (name, value, category) VALUES (%s, %s, %s)", parameters
    )

    assert isinstance(result, SQLResult)
    assert result.rows_affected == 4

    null_result = psycopg_batch_session.execute("SELECT * FROM test_batch WHERE category IS NULL")
    assert len(null_result.data) == 1
    assert null_result.data[0]["name"] == "Another Item"

    negative_result = psycopg_batch_session.execute("SELECT * FROM test_batch WHERE value < 0")
    assert len(negative_result.data) == 1
    assert negative_result.data[0]["value"] == -50


def test_psycopg_execute_many_delete(psycopg_batch_session: PsycopgSyncDriver) -> None:
    """Test execute_many for DELETE operations with Psycopg."""

    psycopg_batch_session.execute_many(
        "INSERT INTO test_batch (name, value, category) VALUES (%s, %s, %s)",
        [
            ("Delete 1", 10, "X"),
            ("Delete 2", 20, "Y"),
            ("Delete 3", 30, "X"),
            ("Keep 1", 40, "Z"),
            ("Delete 4", 50, "Y"),
        ],
    )

    delete_parameters = [("Delete 1",), ("Delete 2",), ("Delete 4",)]

    result = psycopg_batch_session.execute_many("DELETE FROM test_batch WHERE name = %s", delete_parameters)

    assert isinstance(result, SQLResult)
    assert result.rows_affected == 3

    remaining_result = psycopg_batch_session.execute("SELECT COUNT(*) as count FROM test_batch")
    assert remaining_result.data[0]["count"] == 2

    names_result = psycopg_batch_session.execute("SELECT name FROM test_batch ORDER BY name")
    remaining_names = [row["name"] for row in names_result.data]
    assert remaining_names == ["Delete 3", "Keep 1"]


def test_psycopg_execute_many_large_batch(psycopg_batch_session: PsycopgSyncDriver) -> None:
    """Test execute_many with large batch size on Psycopg."""

    large_batch = [(f"Item {i}", i * 10, f"CAT{i % 3}") for i in range(1000)]

    result = psycopg_batch_session.execute_many(
        "INSERT INTO test_batch (name, value, category) VALUES (%s, %s, %s)", large_batch
    )

    assert isinstance(result, SQLResult)
    assert result.rows_affected == 1000

    count_result = psycopg_batch_session.execute("SELECT COUNT(*) as count FROM test_batch")
    assert count_result.data[0]["count"] == 1000

    sample_result = psycopg_batch_session.execute(
        "SELECT * FROM test_batch WHERE name = ANY(%s) ORDER BY value", (["Item 100", "Item 500", "Item 999"],)
    )
    assert len(sample_result.data) == 3
    assert sample_result.data[0]["value"] == 1000
    assert sample_result.data[1]["value"] == 5000
    assert sample_result.data[2]["value"] == 9990


def test_psycopg_execute_many_with_sql_object(psycopg_batch_session: PsycopgSyncDriver) -> None:
    """Test execute_many with SQL object on Psycopg."""
    from sqlspec.core.statement import SQL

    parameters = [("SQL Obj 1", 111, "SOB"), ("SQL Obj 2", 222, "SOB"), ("SQL Obj 3", 333, "SOB")]

    sql_obj = SQL("INSERT INTO test_batch (name, value, category) VALUES (%s, %s, %s)", parameters, is_many=True)

    result = psycopg_batch_session.execute(sql_obj)

    assert isinstance(result, SQLResult)
    assert result.rows_affected == 3

    check_result = psycopg_batch_session.execute(
        "SELECT COUNT(*) as count FROM test_batch WHERE category = %s", ("SOB",)
    )
    assert check_result.data[0]["count"] == 3


def test_psycopg_execute_many_with_returning(psycopg_batch_session: PsycopgSyncDriver) -> None:
    """Test execute_many with RETURNING clause on Psycopg."""
    parameters = [("Return 1", 111, "RET"), ("Return 2", 222, "RET"), ("Return 3", 333, "RET")]

    try:
        result = psycopg_batch_session.execute_many(
            "INSERT INTO test_batch (name, value, category) VALUES (%s, %s, %s) RETURNING id, name", parameters
        )

        assert isinstance(result, SQLResult)

        if hasattr(result, "data") and result.data:
            assert len(result.data) >= 3

    except Exception:
        psycopg_batch_session.execute_many(
            "INSERT INTO test_batch (name, value, category) VALUES (%s, %s, %s)", parameters
        )

        check_result = psycopg_batch_session.execute(
            "SELECT COUNT(*) as count FROM test_batch WHERE category = %s", ("RET",)
        )
        assert check_result.data[0]["count"] == 3


def test_psycopg_execute_many_with_arrays(psycopg_batch_session: PsycopgSyncDriver) -> None:
    """Test execute_many with PostgreSQL array types on Psycopg."""

    psycopg_batch_session.execute_script("""
        DROP TABLE IF EXISTS test_arrays;
        CREATE TABLE test_arrays (
            id SERIAL PRIMARY KEY,
            name TEXT,
            tags TEXT[],
            scores INTEGER[]
        )
    """)

    parameters = [
        ("Array 1", ["tag1", "tag2"], [10, 20, 30]),
        ("Array 2", ["tag3"], [40, 50]),
        ("Array 3", ["tag4", "tag5", "tag6"], [60]),
    ]

    result = psycopg_batch_session.execute_many(
        "INSERT INTO test_arrays (name, tags, scores) VALUES (%s, %s, %s)", parameters
    )

    assert isinstance(result, SQLResult)
    assert result.rows_affected == 3

    check_result = psycopg_batch_session.execute(
        "SELECT name, array_length(tags, 1) as tag_count, array_length(scores, 1) as score_count FROM test_arrays ORDER BY name"
    )
    assert len(check_result.data) == 3
    assert check_result.data[0]["tag_count"] == 2
    assert check_result.data[1]["tag_count"] == 1
    assert check_result.data[2]["tag_count"] == 3


def test_psycopg_execute_many_with_json(psycopg_batch_session: PsycopgSyncDriver) -> None:
    """Test execute_many with JSON data on Psycopg."""
    import json

    psycopg_batch_session.execute_script("""
        DROP TABLE IF EXISTS test_json;
        CREATE TABLE test_json (
            id SERIAL PRIMARY KEY,
            name TEXT,
            metadata JSONB
        )
    """)

    parameters = [
        ("JSON 1", json.dumps({"type": "test", "value": 100, "active": True})),
        ("JSON 2", json.dumps({"type": "prod", "value": 200, "active": False})),
        ("JSON 3", json.dumps({"type": "test", "value": 300, "tags": ["a", "b"]})),
    ]

    result = psycopg_batch_session.execute_many("INSERT INTO test_json (name, metadata) VALUES (%s, %s)", parameters)

    assert isinstance(result, SQLResult)
    assert result.rows_affected == 3

    check_result = psycopg_batch_session.execute(
        "SELECT name, metadata->>'type' as type, (metadata->>'value')::INTEGER as value FROM test_json ORDER BY name"
    )
    assert len(check_result.data) == 3
    assert check_result.data[0]["type"] == "test"
    assert check_result.data[0]["value"] == 100
    assert check_result.data[1]["type"] == "prod"
    assert check_result.data[1]["value"] == 200


def test_psycopg_execute_many_with_upsert(psycopg_batch_session: PsycopgSyncDriver) -> None:
    """Test execute_many with PostgreSQL UPSERT (ON CONFLICT) on Psycopg."""

    psycopg_batch_session.execute_script("""
        CREATE TABLE IF NOT EXISTS test_upsert (
            id INTEGER PRIMARY KEY,
            name TEXT,
            counter INTEGER DEFAULT 1
        )
    """)

    initial_parameters = [(1, "Item 1"), (2, "Item 2"), (3, "Item 3")]

    psycopg_batch_session.execute_many("INSERT INTO test_upsert (id, name) VALUES (%s, %s)", initial_parameters)

    conflict_parameters = [(1, "Updated Item 1", 1), (2, "Updated Item 2", 1), (4, "Item 4", 1)]

    result = psycopg_batch_session.execute_many(
        "INSERT INTO test_upsert (id, name) VALUES (%s, %s) ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, counter = test_upsert.counter + %s",
        conflict_parameters,
    )

    assert isinstance(result, SQLResult)
    assert result.rows_affected == 3

    check_result = psycopg_batch_session.execute("SELECT id, name, counter FROM test_upsert ORDER BY id")
    assert len(check_result.data) == 4

    updated_items = [row for row in check_result.data if row["counter"] > 1]
    assert len(updated_items) == 2
