import uuid

import pytest
from faker import Faker
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from mm_api.schema.bird import BirdRead
from mm_api.schema.falconer import FalconerRead
from mm_api.schema.weight import WeightCreate, WeightRead

fake = Faker()


@pytest.mark.anyio
async def test_create_weight(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    bird: BirdRead,
) -> None:
    weight = WeightCreate(
        id=uuid.uuid4(),
        bird_id=bird.id,
        weight=100,
        w_time=fake.date_time_this_year(),
    )
    url = fastapi_app.url_path_for("create_weight")
    response = await client.post(url, json=jsonable_encoder(weight))
    assert response.status_code == status.HTTP_201_CREATED, response.text


@pytest.mark.anyio
async def test_bulk_create_weight(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    bird: BirdRead,
) -> None:
    weights = []
    for _ in range(10):
        weight = WeightCreate(
            id=uuid.uuid4(),
            bird_id=bird.id,
            weight=100,
            w_time=fake.date_time_this_year(),
        )
        weights.append(weight)
    url = fastapi_app.url_path_for("create_bulk_weight")
    response = await client.post(url, json=jsonable_encoder(weights))
    assert response.status_code == status.HTTP_201_CREATED, response.text


@pytest.mark.anyio
async def test_get_weight(
    fastapi_app: FastAPI,
    client: AsyncClient,
    weight: WeightRead,
) -> None:
    url = fastapi_app.url_path_for("get_weight", weight_id=weight.id)
    response = await client.get(url)
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["id"] == str(weight.id)


@pytest.mark.anyio
async def test_filter_weight_by_date(
    fastapi_app: FastAPI,
    client: AsyncClient,
    weight: WeightRead,
) -> None:
    url = fastapi_app.url_path_for("filter_weight_by_date", bird_id=weight.bird_id)
    response = await client.get(url, params={"days": 31})
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert len(response_data) == 1
    assert response_data[0]["id"] == str(weight.id)
    assert response_data[0]["bird_id"] == str(weight.bird_id)


@pytest.mark.anyio
async def test_filter_weight_by_date_passed(
    fastapi_app: FastAPI,
    client: AsyncClient,
    weight: WeightRead,
) -> None:
    url = fastapi_app.url_path_for("filter_weight_by_date", bird_id=weight.bird_id)
    response = await client.get(url, params={"days": 1})
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert len(response_data) == 0
