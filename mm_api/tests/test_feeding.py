import pytest
from faker import Faker
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from mm_api.schema.bird import BirdRead
from mm_api.schema.falconer import FalconerRead
from mm_api.schema.feeding import FeedingRead
from mm_api.schema.weight import WeightRead
from mm_api.tests.utils.generations import create_feeding

fake = Faker()


@pytest.mark.anyio
async def test_create_feeding(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    bird: BirdRead,
    weight: WeightRead,
    end_weight: WeightRead,
) -> None:
    feeding = create_feeding(
        amount=100,
        start_weight=weight.id,
        end_weight=end_weight.id,
        bird_id=bird.id,
        time=fake.date_time_this_year(),
    )
    url = fastapi_app.url_path_for("create_feeding")
    response = await client.post(url, json=jsonable_encoder(feeding))
    assert response.status_code == status.HTTP_201_CREATED, response.text


@pytest.mark.anyio
async def test_get_feeding(
    fastapi_app: FastAPI,
    client: AsyncClient,
    feeding: FeedingRead,
) -> None:
    url = fastapi_app.url_path_for("get_feeding", feeding_id=feeding.id)
    response = await client.get(url)
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["id"] == str(feeding.id)


@pytest.mark.anyio
async def test_bulk_create_feeding(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    bird: BirdRead,
    weight: WeightRead,
    end_weight: WeightRead,
) -> None:
    feedings = []
    for _ in range(10):
        feeding = create_feeding(
            amount=100,
            start_weight=weight.id,
            end_weight=end_weight.id,
            bird_id=bird.id,
            time=fake.date_time_this_year(),
        )
        feedings.append(feeding)
    url = fastapi_app.url_path_for("create_bulk_feeding")
    response = await client.post(url, json=jsonable_encoder(feedings))
    assert response.status_code == status.HTTP_201_CREATED, response.text


@pytest.mark.anyio
async def test_filter_feeding_by_date(
    fastapi_app: FastAPI,
    client: AsyncClient,
    feeding: FeedingRead,
) -> None:
    url = fastapi_app.url_path_for("filter_feeding_by_date", bird_id=feeding.bird_id)
    response = await client.get(url, params={"days": 31})
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert len(response_data) == 1
    assert response_data[0]["id"] == str(feeding.id)
    assert response_data[0]["bird_id"] == str(feeding.bird_id)


@pytest.mark.anyio
async def test_filter_feeding_by_date_passed(
    fastapi_app: FastAPI,
    client: AsyncClient,
    feeding: FeedingRead,
) -> None:
    url = fastapi_app.url_path_for("filter_feeding_by_date", bird_id=feeding.bird_id)
    response = await client.get(url, params={"days": 1})
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert len(response_data) == 0
