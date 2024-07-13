import pytest
from faker import Faker
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from mm_api.schema.bird import BirdRead
from mm_api.schema.falconer import FalconerRead
from mm_api.schema.hunt import HuntBase
from mm_api.schema.training import TrainingBase
from mm_api.schema.weight import WeightCreate
from mm_api.tests.utils.birds import create_bird
from mm_api.tests.utils.generations import create_feeding

fake = Faker()


@pytest.mark.anyio
async def test_create_bird(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    falconer: FalconerRead,
) -> None:
    bird, response = await create_bird(fastapi_app, client, falconer)
    assert response.status_code == status.HTTP_201_CREATED, response.text
    assert response.json()["id"] == str(bird.id), response.text


@pytest.mark.anyio
async def test_get_bird(
    fastapi_app: FastAPI,
    client: AsyncClient,
    bird: BirdRead,
) -> None:
    url = fastapi_app.url_path_for("get_bird", bird_id=bird.id)
    response = await client.get(url)
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["id"] == str(bird.id)
    assert response_data["name"] == bird.name


@pytest.mark.anyio
async def test_get_bids_by_falconer_id(
    fastapi_app: FastAPI,
    authed_client: AsyncClient,
    falconer: FalconerRead,
) -> None:
    bird1, resp1 = await create_bird(fastapi_app, authed_client, falconer)
    assert resp1.status_code == status.HTTP_201_CREATED, resp1.text
    bird2, resp2 = await create_bird(fastapi_app, authed_client, falconer)
    assert resp2.status_code == status.HTTP_201_CREATED, resp2.text

    url = fastapi_app.url_path_for("get_birds_by_falconer_id")
    response = await authed_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert len(response_data) == 2


# @pytest.mark.anyio
# async def test_dashboard_info(
#     fastapi_app: FastAPI,
#     client: AsyncClient,
#     bird: BirdRead,
# ) -> None:
#     weights = []
#     for _ in range(10):
#         weight = WeightCreate(
#             id=uuid.uuid4(),
#             bird_id=bird.id,
#             weight=100,
#             w_time=fake.date_time_this_year(),
#         )
#         weights.append(weight)
#     url = fastapi_app.url_path_for("create_bulk_weight")
#     response = await client.post(url, json=jsonable_encoder(weights))
#     assert response.status_code == status.HTTP_201_CREATED, response.text
#
#     trainings = []
#     for _ in range(10):
#         training = TrainingBase(
#             bird_id=bird.id,
#             start_weight_id=weights[0].id,
#             end_weight_id=weights[1].id,
#             start_time=fake.date_time_this_year(),
#             end_time=fake.date_time_this_year(),
#             notes="Training the bird.",
#             training_type="flying",
#             performance=5,
#         )
#         trainings.append(training)
#     url = fastapi_app.url_path_for("create_bulk_training")
#     response = await client.post(url, json=jsonable_encoder(trainings))
#     assert response.status_code == status.HTTP_201_CREATED, response.text
#
#     hunts = []
#     for _ in range(10):
#         hunt = HuntBase(
#             bird_id=bird.id,
#             start_weight_id=weights[0].id,
#             end_weight_id=weights[1].id,
#             prey_type="rabbit",
#             prey_count=5,
#             start_time=fake.date_time_this_year(),
#             end_time=fake.date_time_this_year(),
#             notes="Hunted 5 rabbits.",
#         )
#         hunts.append(hunt)
#
#     url = fastapi_app.url_path_for("create_bulk_hunt")
#     response = await client.post(url, json=jsonable_encoder(hunts))
#     assert response.status_code == status.HTTP_201_CREATED, response.text
#
#     feedings = []
#     for _ in range(10):
#         feeding = create_feeding(
#             amount=100,
#             start_weight=weights[1].id,  # type: ignore
#             end_weight=weights[0].id,  # type: ignore
#             bird_id=bird.id,
#             time=fake.date_time_this_year(),
#         )
#         feedings.append(feeding)
#
#     url = fastapi_app.url_path_for("create_bulk_feeding")
#     response = await client.post(url, json=jsonable_encoder(feedings))
#     assert response.status_code == status.HTTP_201_CREATED, response.text
#
#     url = fastapi_app.url_path_for("get_dashboard_info", bird_id=bird.id)
#     response = await client.get(url)
#     assert response.status_code == status.HTTP_200_OK
#     response_data = response.json()
#     assert len(response_data["trainings"]) == 10
#     assert len(response_data["hunts"]) == 10
#     assert len(response_data["feedings"]) == 10
#     assert len(response_data["weights"]) == 10
