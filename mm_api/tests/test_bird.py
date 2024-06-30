import pytest
from faker import Faker
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from mm_api.schema.bird import BirdRead
from mm_api.schema.falconer import FalconerRead
from mm_api.tests.utils.birds import create_bird

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
    client: AsyncClient,
    falconer: FalconerRead,
) -> None:
    bird1, resp1 = await create_bird(fastapi_app, client, falconer)
    assert resp1.status_code == status.HTTP_201_CREATED, resp1.text
    bird2, resp2 = await create_bird(fastapi_app, client, falconer)
    assert resp2.status_code == status.HTTP_201_CREATED, resp2.text

    url = fastapi_app.url_path_for("get_birds_by_falconer_id", falconer_id=falconer.id)
    response = await client.get(url)
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert len(response_data) == 2
