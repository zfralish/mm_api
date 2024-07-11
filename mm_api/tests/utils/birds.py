import random
from datetime import datetime
from typing import Any

import faker
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient

from mm_api.schema.bird import BirdCreate, BirdRead
from mm_api.schema.falconer import FalconerRead
from mm_api.schema.feeding import FeedingBase
from mm_api.schema.hunt import HuntBase
from mm_api.schema.training import TrainingBase
from mm_api.schema.weight import WeightCreate

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


# async def create_nest_bird(
#     fastapi_app: FastAPI,
#     client: AsyncClient,
#     bird: BirdRead,
#     weights: List[WeightCreate],
#     trainingings: List[TrainingBase],
#     feedings: List[FeedingBase],
#     hunts: List[HuntBase],
# ) -> tuple[BirdRead, Any]:
#     url = fastapi_app.url_path_for("create_bird")
#     weights_enc = jsonable_encoder(
#         weights,
#     )
#     trainings_enc = jsonable_encoder(
#         trainingings,
#     )
#     feedings_enc = jsonable_encoder(
#         feedings,
#     )
#     hunts_enc = jsonable_encoder(
#         hunts,
#     )
#     resp = await client.post(
#         url,
#         json=test_bird,
#     )

#     return BirdRead(**resp.json()), resp
