import datetime
import uuid
from typing import Any, AsyncGenerator

import pytest
from faker import Faker
from fakeredis import FakeServer
from fakeredis.aioredis import FakeConnection
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
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
from mm_api.schema.bird import BirdNestedChildren, BirdRead
from mm_api.schema.falconer import FalconerCreate, FalconerRead
from mm_api.schema.feeding import FeedingBase, FeedingRead
from mm_api.schema.hunt import HuntBase, HuntRead
from mm_api.schema.training import TrainingBase, TrainingRead
from mm_api.schema.weight import WeightCreate, WeightRead
from mm_api.services.redis.dependency import get_redis_pool
from mm_api.settings import settings
from mm_api.tests.utils.birds import create_bird
from mm_api.tests.utils.dependency_overrides import override_auth_dependency
from mm_api.tests.utils.generations import (
    create_feeding,
    create_hunts,
    create_trainings,
)
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

    await create_database(True)

    engine = create_async_engine(str(settings.db_url_test))
    async with engine.begin() as conn:
        await conn.run_sync(meta.create_all)

    try:
        yield engine
    finally:
        await engine.dispose()
        await drop_database(True)


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


@pytest.fixture
async def weight(
    fastapi_app: FastAPI,
    client: AsyncClient,
    bird: BirdRead,
) -> AsyncGenerator[WeightRead, None]:
    weight = WeightCreate(
        id=uuid.uuid4(),
        bird_id=bird.id,
        weight=1000,
        w_time=datetime.datetime.now() - datetime.timedelta(days=1),
    )
    url = fastapi_app.url_path_for("create_weight")
    resp = await client.post(url, json=jsonable_encoder(weight))
    yield WeightRead(**resp.json())


@pytest.fixture
async def end_weight(
    fastapi_app: FastAPI,
    client: AsyncClient,
    bird: BirdRead,
) -> AsyncGenerator[WeightRead, None]:
    weight = WeightCreate(
        id=uuid.uuid4(),
        bird_id=bird.id,
        weight=1000,
        w_time=datetime.datetime.now(),
    )
    url = fastapi_app.url_path_for("create_weight")
    resp = await client.post(url, json=jsonable_encoder(weight))
    yield WeightRead(**resp.json())


@pytest.fixture
async def feeding(
    fastapi_app: FastAPI,
    client: AsyncClient,
    bird: BirdRead,
    weight: WeightRead,
    end_weight: WeightRead,
) -> AsyncGenerator[FeedingRead, None]:
    feeding = create_feeding(
        amount=100,
        start_weight=weight.id,
        end_weight=end_weight.id,
        bird_id=bird.id,
        time=fake.date_time_this_month(),
    )
    url = fastapi_app.url_path_for("create_feeding")
    response = await client.post(url, json=jsonable_encoder(feeding))
    yield FeedingRead(**response.json())


@pytest.fixture
async def hunt(
    fastapi_app: FastAPI,
    client: AsyncClient,
    bird: BirdRead,
    feeding: FeedingRead,
) -> AsyncGenerator[HuntRead, None]:
    hunt = HuntBase(
        bird_id=bird.id,
        start_weight_id=feeding.start_weight_id,
        end_weight_id=feeding.end_weight_id,
        prey_type="squirrel",
        prey_count=6,
        start_time=fake.date_time_this_year(),
        end_time=fake.date_time_this_year(),
        notes="killing some stuff",
    )
    url = fastapi_app.url_path_for("create_hunt")
    response = await client.post(url, json=jsonable_encoder(hunt))
    yield HuntRead(**response.json())


@pytest.fixture
async def training(
    fastapi_app: FastAPI,
    client: AsyncClient,
    bird: BirdRead,
    weight: WeightRead,
    end_weight: WeightRead,
) -> AsyncGenerator[TrainingRead, None]:
    training = TrainingBase(
        bird_id=bird.id,
        training_type="free_flight",
        notes="",
        performance=0,
        start_weight_id=weight.id,
        end_weight_id=end_weight.id,
        start_time=fake.date_time_this_year(),
        end_time=fake.date_time_this_year(),
    )
    url = fastapi_app.url_path_for("create_training")
    response = await client.post(url, json=jsonable_encoder(training))
    yield TrainingRead(**response.json())


# @pytest.fixture
# async def nested_bird(
#     fastapi_app: FastAPI,
#     client: AsyncClient,
#     bird: BirdRead,
# ) -> AsyncGenerator[BirdNestedChildren, None]:
#     agg_weight, agg_feeding = [], []
#     trainings, weights, feedings, date = create_trainings(
#                         bird.id,  # type: ignore
#                         bird.gender,
#                     )
#     trainings = [TrainingBase(**training.dict()) for training in trainings]
#     agg_weight.append([WeightCreate(**weight.dict()) for weight in weights])
#     agg_feeding.append([FeedingBase(**feeding.dict()) for feeding in feedings])
#     hunts, hunt_weights, hunt_feedings = create_hunts(
#         bird.id,  # type: ignore
#         weights[-1].weight,
#         date,
#     )
#     agg_weight.append([WeightCreate(**weight.dict()) for weight in hunt_weights])
#     agg_feeding.append([FeedingBase(**feeding.dict()) for feeding in hunt_feedings])
