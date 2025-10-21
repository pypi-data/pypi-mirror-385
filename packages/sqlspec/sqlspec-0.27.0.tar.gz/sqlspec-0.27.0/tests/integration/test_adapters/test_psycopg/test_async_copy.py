"""Integration tests for psycopg async driver COPY operations."""

from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
from pytest_databases.docker.postgres import PostgresService

from sqlspec.adapters.psycopg import PsycopgAsyncConfig, PsycopgAsyncDriver
from sqlspec.core.result import SQLResult

pytestmark = pytest.mark.xdist_group("postgres")


@pytest.fixture
async def psycopg_async_session(postgres_service: PostgresService) -> AsyncGenerator[PsycopgAsyncDriver, None]:
    """Create a psycopg async session with test table."""
    config = PsycopgAsyncConfig(
        pool_config={
            "conninfo": f"postgresql://{postgres_service.user}:{postgres_service.password}@{postgres_service.host}:{postgres_service.port}/{postgres_service.database}",
            "autocommit": True,
        }
    )

    pool = await config.create_pool()
    config.pool_instance = pool

    try:
        async with config.provide_session() as session:
            await session.execute_script("""
                CREATE TABLE IF NOT EXISTS test_table_async (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    value INTEGER DEFAULT 0
                )
            """)
            yield session

            try:
                await session.execute_script("DROP TABLE IF EXISTS test_table_async")
            except Exception:
                pass
    finally:
        await config.close_pool()


async def test_psycopg_async_copy_operations_positional(psycopg_async_session: PsycopgAsyncDriver) -> None:
    """Test PostgreSQL COPY operations with async psycopg driver using positional parameters."""

    await psycopg_async_session.execute_script("""
        DROP TABLE IF EXISTS copy_test_async;
        CREATE TABLE copy_test_async (
            id INTEGER,
            name TEXT,
            value INTEGER
        )
    """)

    copy_data = "1\ttest1\t100\n2\ttest2\t200\n"
    result = await psycopg_async_session.execute("COPY copy_test_async FROM STDIN WITH (FORMAT text)", copy_data)
    assert isinstance(result, SQLResult)
    assert result.rows_affected >= 0

    verify_result = await psycopg_async_session.execute("SELECT * FROM copy_test_async ORDER BY id")
    assert isinstance(verify_result, SQLResult)
    assert verify_result.data is not None
    assert len(verify_result.data) == 2
    assert verify_result.data[0]["name"] == "test1"
    assert verify_result.data[1]["value"] == 200

    await psycopg_async_session.execute_script("DROP TABLE copy_test_async")


async def test_psycopg_async_copy_operations_keyword(psycopg_async_session: PsycopgAsyncDriver) -> None:
    """Test PostgreSQL COPY operations with async psycopg driver using keyword parameters."""

    await psycopg_async_session.execute_script("""
        DROP TABLE IF EXISTS copy_test_async_kw;
        CREATE TABLE copy_test_async_kw (
            id INTEGER,
            name TEXT,
            value INTEGER
        )
    """)

    copy_data = "3\ttest3\t300\n4\ttest4\t400\n"
    result = await psycopg_async_session.execute("COPY copy_test_async_kw FROM STDIN WITH (FORMAT text)", copy_data)
    assert isinstance(result, SQLResult)
    assert result.rows_affected >= 0

    verify_result = await psycopg_async_session.execute("SELECT * FROM copy_test_async_kw ORDER BY id")
    assert isinstance(verify_result, SQLResult)
    assert verify_result.data is not None
    assert len(verify_result.data) == 2
    assert verify_result.data[0]["name"] == "test3"
    assert verify_result.data[1]["value"] == 400

    await psycopg_async_session.execute_script("DROP TABLE copy_test_async_kw")


async def test_psycopg_async_copy_csv_format_positional(psycopg_async_session: PsycopgAsyncDriver) -> None:
    """Test PostgreSQL COPY operations with CSV format using async driver and positional parameters."""

    await psycopg_async_session.execute_script("""
        CREATE TABLE copy_csv_async_pos (
            id INTEGER,
            name TEXT,
            value INTEGER
        )
    """)

    csv_data = "3,test3,300\n4,test4,400\n5,test5,500\n"
    result = await psycopg_async_session.execute("COPY copy_csv_async_pos FROM STDIN WITH (FORMAT csv)", csv_data)
    assert isinstance(result, SQLResult)
    assert result.rows_affected == 3

    select_result = await psycopg_async_session.execute("SELECT * FROM copy_csv_async_pos ORDER BY id")
    assert isinstance(select_result, SQLResult)
    assert select_result.data is not None
    assert len(select_result.data) == 3
    assert select_result.data[0]["name"] == "test3"
    assert select_result.data[2]["value"] == 500

    await psycopg_async_session.execute_script("DROP TABLE copy_csv_async_pos")


async def test_psycopg_async_copy_csv_format_keyword(psycopg_async_session: PsycopgAsyncDriver) -> None:
    """Test PostgreSQL COPY operations with CSV format using async driver and keyword parameters."""

    await psycopg_async_session.execute_script("""
        CREATE TABLE copy_csv_async_kw (
            id INTEGER,
            name TEXT,
            value INTEGER
        )
    """)

    csv_data = "6,test6,600\n7,test7,700\n8,test8,800\n"
    result = await psycopg_async_session.execute("COPY copy_csv_async_kw FROM STDIN WITH (FORMAT csv)", csv_data)
    assert isinstance(result, SQLResult)
    assert result.rows_affected == 3

    select_result = await psycopg_async_session.execute("SELECT * FROM copy_csv_async_kw ORDER BY id")
    assert isinstance(select_result, SQLResult)
    assert select_result.data is not None
    assert len(select_result.data) == 3
    assert select_result.data[0]["name"] == "test6"
    assert select_result.data[2]["value"] == 800

    await psycopg_async_session.execute_script("DROP TABLE copy_csv_async_kw")
