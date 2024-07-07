from typing import Any, AsyncGenerator

import pytest
from faker import Faker
from fakeredis import FakeServer
from fakeredis.aioredis import FakeConnection
from fastapi import FastAPI
from httpx import AsyncClient
from redis.asyncio import ConnectionPool
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from mm_api.db.dependencies import get_db_session
from mm_api.db.models import *  # noqa: WPS433
from mm_api.db.utils import create_database, drop_database
from mm_api.schema.bird import BirdRead
from mm_api.schema.falconer import FalconerCreate, FalconerRead
from mm_api.services.redis.dependency import get_redis_pool
from mm_api.settings import settings
from mm_api.tests.utils.birds import create_bird
from mm_api.tests.utils.dependency_overrides import override_auth_dependency
from mm_api.web.application import get_app
from mm_api.web.dependencies import is_authenticated

fake = Faker()


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """
    Backend for anyio pytest plugin.

    :return: backend name.
    """
    return "asyncio"


@pytest.fixture(scope="session")
async def _engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Create engine and databases.

    :yield: new engine.
    """
    from mm_api.db.meta import meta  # noqa: WPS433

    await create_database()

    engine = create_async_engine(str(settings.db_url))
    async with engine.begin() as conn:
        await conn.run_sync(meta.create_all)

    try:
        yield engine
    finally:
        await engine.dispose()
        await drop_database()


@pytest.fixture
async def dbsession(
    _engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Get session to database.

    Fixture that returns a SQLAlchemy session with a SAVEPOINT, and the rollback to it
    after the test completes.

    :param _engine: current engine.
    :yields: async session.
    """
    connection = await _engine.connect()
    trans = await connection.begin()

    session_maker = async_sessionmaker(
        connection,
        expire_on_commit=False,
    )
    session = session_maker()

    try:
        yield session
    finally:
        await session.close()
        await trans.rollback()
        await connection.close()


@pytest.fixture
async def fake_redis_pool() -> AsyncGenerator[ConnectionPool, None]:
    """
    Get instance of a fake redis.

    :yield: FakeRedis instance.
    """
    server = FakeServer()
    server.connected = True
    pool = ConnectionPool(connection_class=FakeConnection, server=server)

    yield pool

    await pool.disconnect()


@pytest.fixture
def fastapi_app(
    dbsession: AsyncSession,
    fake_redis_pool: ConnectionPool,
) -> FastAPI:
    """
    Fixture for creating FastAPI app.

    :return: fastapi app with mocked dependencies.
    """
    application = get_app()
    application.dependency_overrides[get_db_session] = lambda: dbsession
    application.dependency_overrides[get_redis_pool] = lambda: fake_redis_pool
    return application  # noqa: WPS331


@pytest.fixture
async def client(
    fastapi_app: FastAPI,
    anyio_backend: Any,
) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture that creates client for requesting server.

    :param fastapi_app: the application.
    :yield: client for the app.
    """
    async with AsyncClient(app=fastapi_app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def authed_client(
    fastapi_app: FastAPI,
    anyio_backend: Any,
) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture that creates client for requesting server.

    :param fastapi_app: the application.
    :yield: client for the app.
    """
    fastapi_app.dependency_overrides[is_authenticated] = override_auth_dependency
    async with AsyncClient(app=fastapi_app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def falconer(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> AsyncGenerator[FalconerRead, None]:
    url = fastapi_app.url_path_for("create_falconer")
    test_falconer = FalconerCreate(
        name="Zeke Fralish",
        permit_class="general",
        permit_number="456aaa",
        id="user_2ifMt89Ay39uwvtLQUijf7OGCq5",
    )
    response = await client.post(
        url,
        json=test_falconer.dict(),
    )
    yield FalconerRead(**response.json())


@pytest.fixture
async def bird(
    fastapi_app: FastAPI,
    client: AsyncClient,
    falconer: FalconerRead,
) -> AsyncGenerator[BirdRead, None]:
    bird, resp = await create_bird(fastapi_app, client, falconer)
    yield bird
