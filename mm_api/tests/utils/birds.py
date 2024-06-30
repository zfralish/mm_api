import random
from datetime import datetime
from typing import Any

import faker
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient

from mm_api.schema.bird import BirdCreate, BirdRead
from mm_api.schema.falconer import FalconerRead

fake = faker.Faker()


async def create_bird(
    fastapi_app: FastAPI,
    client: AsyncClient,
    falconer: FalconerRead,
) -> tuple[BirdRead, Any]:
    url = fastapi_app.url_path_for("create_bird")
    test_bird = jsonable_encoder(
        BirdCreate(
            falconer_id=falconer.id,
            name=fake.name(),
            gender=random.choice(["male", "female"]),
            species=random.choice(["Red-Tailed Hawk", "Goshawk"]),
            trap_date=datetime.now(),
            id=fake.uuid4(),  # type: ignore
        ),
    )
    resp = await client.post(
        url,
        json=test_bird,
    )

    return BirdRead(**resp.json()), resp
