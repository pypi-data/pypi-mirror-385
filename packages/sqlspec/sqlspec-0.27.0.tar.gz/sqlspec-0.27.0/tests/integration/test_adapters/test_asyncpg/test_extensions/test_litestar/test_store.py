"""Integration tests for AsyncPG session store."""

import asyncio
from collections.abc import AsyncGenerator
from datetime import timedelta

import pytest
from pytest_databases.docker.postgres import PostgresService

from sqlspec.adapters.asyncpg.config import AsyncpgConfig
from sqlspec.adapters.asyncpg.litestar.store import AsyncpgStore

pytestmark = [pytest.mark.xdist_group("postgres"), pytest.mark.asyncpg, pytest.mark.integration]


@pytest.fixture
async def asyncpg_store(postgres_service: PostgresService) -> "AsyncGenerator[AsyncpgStore, None]":
    """Create AsyncPG store with test database."""
    config = AsyncpgConfig(
        pool_config={
            "host": postgres_service.host,
            "port": postgres_service.port,
            "user": postgres_service.user,
            "password": postgres_service.password,
            "database": postgres_service.database,
        },
        extension_config={"litestar": {"session_table": "test_sessions"}},
    )
    store = AsyncpgStore(config)
    try:
        await store.create_table()
        yield store
        await store.delete_all()
    finally:
        if config.pool_instance:
            await config.close_pool()


async def test_store_create_table(asyncpg_store: AsyncpgStore) -> None:
    """Test table creation."""
    assert asyncpg_store.table_name == "test_sessions"


async def test_store_set_and_get(asyncpg_store: AsyncpgStore) -> None:
    """Test basic set and get operations."""
    test_data = b"test session data"
    await asyncpg_store.set("session_123", test_data)

    result = await asyncpg_store.get("session_123")
    assert result == test_data


async def test_store_get_nonexistent(asyncpg_store: AsyncpgStore) -> None:
    """Test getting a non-existent session returns None."""
    result = await asyncpg_store.get("nonexistent")
    assert result is None


async def test_store_set_with_string_value(asyncpg_store: AsyncpgStore) -> None:
    """Test setting a string value (should be converted to bytes)."""
    await asyncpg_store.set("session_str", "string data")

    result = await asyncpg_store.get("session_str")
    assert result == b"string data"


async def test_store_delete(asyncpg_store: AsyncpgStore) -> None:
    """Test delete operation."""
    await asyncpg_store.set("session_to_delete", b"data")

    assert await asyncpg_store.exists("session_to_delete")

    await asyncpg_store.delete("session_to_delete")

    assert not await asyncpg_store.exists("session_to_delete")
    assert await asyncpg_store.get("session_to_delete") is None


async def test_store_delete_nonexistent(asyncpg_store: AsyncpgStore) -> None:
    """Test deleting a non-existent session is a no-op."""
    await asyncpg_store.delete("nonexistent")


async def test_store_expiration_with_int(asyncpg_store: AsyncpgStore) -> None:
    """Test session expiration with integer seconds."""
    await asyncpg_store.set("expiring_session", b"data", expires_in=1)

    assert await asyncpg_store.exists("expiring_session")

    await asyncio.sleep(1.1)

    result = await asyncpg_store.get("expiring_session")
    assert result is None
    assert not await asyncpg_store.exists("expiring_session")


async def test_store_expiration_with_timedelta(asyncpg_store: AsyncpgStore) -> None:
    """Test session expiration with timedelta."""
    await asyncpg_store.set("expiring_session", b"data", expires_in=timedelta(seconds=1))

    assert await asyncpg_store.exists("expiring_session")

    await asyncio.sleep(1.1)

    result = await asyncpg_store.get("expiring_session")
    assert result is None


async def test_store_no_expiration(asyncpg_store: AsyncpgStore) -> None:
    """Test session without expiration persists."""
    await asyncpg_store.set("permanent_session", b"data")

    expires_in = await asyncpg_store.expires_in("permanent_session")
    assert expires_in is None

    assert await asyncpg_store.exists("permanent_session")


async def test_store_expires_in(asyncpg_store: AsyncpgStore) -> None:
    """Test expires_in returns correct time."""
    await asyncpg_store.set("timed_session", b"data", expires_in=10)

    expires_in = await asyncpg_store.expires_in("timed_session")
    assert expires_in is not None
    assert 8 <= expires_in <= 10


async def test_store_expires_in_expired(asyncpg_store: AsyncpgStore) -> None:
    """Test expires_in returns 0 for expired session."""
    await asyncpg_store.set("expired_session", b"data", expires_in=1)

    await asyncio.sleep(1.1)

    expires_in = await asyncpg_store.expires_in("expired_session")
    assert expires_in == 0


async def test_store_cleanup(asyncpg_store: AsyncpgStore) -> None:
    """Test delete_expired removes only expired sessions."""
    await asyncpg_store.set("active_session", b"data", expires_in=60)
    await asyncpg_store.set("expired_session_1", b"data", expires_in=1)
    await asyncpg_store.set("expired_session_2", b"data", expires_in=1)
    await asyncpg_store.set("permanent_session", b"data")

    await asyncio.sleep(1.1)

    count = await asyncpg_store.delete_expired()
    assert count == 2

    assert await asyncpg_store.exists("active_session")
    assert await asyncpg_store.exists("permanent_session")
    assert not await asyncpg_store.exists("expired_session_1")
    assert not await asyncpg_store.exists("expired_session_2")


async def test_store_upsert(asyncpg_store: AsyncpgStore) -> None:
    """Test updating existing session (UPSERT)."""
    await asyncpg_store.set("session_upsert", b"original data")

    result = await asyncpg_store.get("session_upsert")
    assert result == b"original data"

    await asyncpg_store.set("session_upsert", b"updated data")

    result = await asyncpg_store.get("session_upsert")
    assert result == b"updated data"


async def test_store_upsert_with_expiration_change(asyncpg_store: AsyncpgStore) -> None:
    """Test updating session expiration."""
    await asyncpg_store.set("session_exp", b"data", expires_in=60)

    expires_in = await asyncpg_store.expires_in("session_exp")
    assert expires_in is not None
    assert expires_in > 50

    await asyncpg_store.set("session_exp", b"data", expires_in=10)

    expires_in = await asyncpg_store.expires_in("session_exp")
    assert expires_in is not None
    assert expires_in <= 10


async def test_store_renew_for(asyncpg_store: AsyncpgStore) -> None:
    """Test renewing session expiration on get."""
    await asyncpg_store.set("session_renew", b"data", expires_in=5)

    await asyncio.sleep(3)

    expires_before = await asyncpg_store.expires_in("session_renew")
    assert expires_before is not None
    assert expires_before <= 2

    result = await asyncpg_store.get("session_renew", renew_for=10)
    assert result == b"data"

    expires_after = await asyncpg_store.expires_in("session_renew")
    assert expires_after is not None
    assert expires_after > 8


async def test_store_large_data(asyncpg_store: AsyncpgStore) -> None:
    """Test storing large session data (>1MB)."""
    large_data = b"x" * (1024 * 1024 + 100)

    await asyncpg_store.set("large_session", large_data)

    result = await asyncpg_store.get("large_session")
    assert result is not None
    assert result == large_data
    assert len(result) > 1024 * 1024


async def test_store_delete_all(asyncpg_store: AsyncpgStore) -> None:
    """Test delete_all removes all sessions."""
    await asyncpg_store.set("session1", b"data1")
    await asyncpg_store.set("session2", b"data2")
    await asyncpg_store.set("session3", b"data3")

    assert await asyncpg_store.exists("session1")
    assert await asyncpg_store.exists("session2")
    assert await asyncpg_store.exists("session3")

    await asyncpg_store.delete_all()

    assert not await asyncpg_store.exists("session1")
    assert not await asyncpg_store.exists("session2")
    assert not await asyncpg_store.exists("session3")


async def test_store_exists(asyncpg_store: AsyncpgStore) -> None:
    """Test exists method."""
    assert not await asyncpg_store.exists("test_session")

    await asyncpg_store.set("test_session", b"data")

    assert await asyncpg_store.exists("test_session")


async def test_store_context_manager(asyncpg_store: AsyncpgStore) -> None:
    """Test store can be used as async context manager."""
    async with asyncpg_store:
        await asyncpg_store.set("ctx_session", b"data")

    result = await asyncpg_store.get("ctx_session")
    assert result == b"data"
