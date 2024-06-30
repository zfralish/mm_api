import pytest
from faker import Faker
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from mm_api.schema.falconer import FalconerCreate, FalconerRead

fake = Faker()


@pytest.mark.anyio
async def test_create_falconer(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests dummy instance creation."""
    url = fastapi_app.url_path_for("create_falconer")
    test_falconer = FalconerCreate(
        name=fake.name(),
        permit_class="general",
        permit_number="456aaa",
        id=str(fake.uuid4()),
    )
    response = await client.post(
        url,
        json=test_falconer.dict(),
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["id"] == test_falconer.id


@pytest.mark.anyio
async def test_get_falconer(
    fastapi_app: FastAPI,
    client: AsyncClient,
    falconer: FalconerRead,
) -> None:

    url = fastapi_app.url_path_for("get_falconer", falconer_id=falconer.id)
    response = await client.get(url)
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["id"] == falconer.id
    assert response_data["name"] == falconer.name
