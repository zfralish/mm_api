import pytest
from faker import Faker
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from mm_api.schema.bird import BirdRead
from mm_api.schema.falconer import FalconerRead
from mm_api.schema.hunt import HuntBase, HuntRead
from mm_api.schema.weight import WeightRead

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
    hunt = HuntBase(
        bird_id=bird.id,
        start_weight_id=weight.id,
        end_weight_id=end_weight.id,
        prey_type="rabbit",
        prey_count=5,
        start_time=fake.date_time_this_year(),
        end_time=fake.date_time_this_year(),
        notes="Hunted 5 rabbits.",
    )
    url = fastapi_app.url_path_for("create_hunt")
    response = await client.post(url, json=jsonable_encoder(hunt))
    assert response.status_code == status.HTTP_201_CREATED, response.text


@pytest.mark.anyio
async def test_get_hunt(
    fastapi_app: FastAPI,
    client: AsyncClient,
    hunt: HuntRead,
) -> None:
    url = fastapi_app.url_path_for("get_hunt", hunt_id=hunt.id)
    response = await client.get(url)
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["id"] == str(hunt.id)


@pytest.mark.anyio
async def test_bulk_create_hunt(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    bird: BirdRead,
    weight: WeightRead,
    end_weight: WeightRead,
) -> None:
    hunts = []
    for _ in range(10):
        hunt = HuntBase(
            bird_id=bird.id,
            start_weight_id=weight.id,
            end_weight_id=end_weight.id,
            prey_type="rabbit",
            prey_count=5,
            start_time=fake.date_time_this_year(),
            end_time=fake.date_time_this_year(),
            notes="Hunted 5 rabbits.",
        )
        hunts.append(hunt)
    url = fastapi_app.url_path_for("create_bulk_hunt")
    response = await client.post(url, json=jsonable_encoder(hunts))
    assert response.status_code == status.HTTP_201_CREATED, response.text
