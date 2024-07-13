import pytest
from faker import Faker
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from mm_api.schema.bird import BirdRead
from mm_api.schema.falconer import FalconerRead
from mm_api.schema.training import TrainingBase, TrainingRead
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
    training = TrainingBase(
        bird_id=bird.id,
        start_weight_id=weight.id,
        end_weight_id=end_weight.id,
        start_time=fake.date_time_this_year(),
        end_time=fake.date_time_this_year(),
        notes="Training the bird.",
        training_type="flying",
        performance=5,
    )
    url = fastapi_app.url_path_for("create_training")
    response = await client.post(url, json=jsonable_encoder(training))
    assert response.status_code == status.HTTP_201_CREATED, response.text


@pytest.mark.anyio
async def test_get_training(
    fastapi_app: FastAPI,
    client: AsyncClient,
    training: TrainingRead,
) -> None:
    url = fastapi_app.url_path_for("get_training", training_id=training.id)
    response = await client.get(url)
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["id"] == str(training.id)


@pytest.mark.anyio
async def test_bulk_create_training(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    bird: BirdRead,
    weight: WeightRead,
    end_weight: WeightRead,
) -> None:
    trainings = []
    for _ in range(10):
        training = TrainingBase(
            bird_id=bird.id,
            start_weight_id=weight.id,
            end_weight_id=end_weight.id,
            start_time=fake.date_time_this_year(),
            end_time=fake.date_time_this_year(),
            notes="Training the bird.",
            training_type="flying",
            performance=5,
        )
        trainings.append(training)
    url = fastapi_app.url_path_for("create_bulk_training")
    response = await client.post(url, json=jsonable_encoder(trainings))
    assert response.status_code == status.HTTP_201_CREATED, response.text


@pytest.mark.anyio
async def test_filter_training_by_date(
    fastapi_app: FastAPI,
    client: AsyncClient,
    training: TrainingRead,
) -> None:
    url = fastapi_app.url_path_for("filter_training_by_date", bird_id=training.bird_id)
    response = await client.get(url, params={"days": 31})
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert len(response_data) == 1
    assert response_data[0]["id"] == str(training.id)
    assert response_data[0]["bird_id"] == str(training.bird_id)


@pytest.mark.anyio
async def test_filter_training_by_date_passed(
    fastapi_app: FastAPI,
    client: AsyncClient,
    training: TrainingRead,
) -> None:
    url = fastapi_app.url_path_for("filter_training_by_date", bird_id=training.bird_id)
    response = await client.get(url, params={"days": 1})
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert len(response_data) == 0
