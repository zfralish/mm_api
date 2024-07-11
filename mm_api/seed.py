import asyncio
from uuid import uuid4

import numpy as np
from faker import Faker
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from mm_api.db.dao.bird_dao import BirdDAO
from mm_api.db.dao.falconer_dao import FalconerDAO
from mm_api.db.dao.feeding_dao import FeedingDAO
from mm_api.db.dao.hunt_dao import HuntDAO
from mm_api.db.dao.training_dao import TrainingDAO
from mm_api.db.dao.weight_dao import WeightDAO
from mm_api.schema.bird import BirdCreate
from mm_api.schema.falconer import FalconerCreate
from mm_api.schema.feeding import FeedingBase
from mm_api.schema.hunt import HuntBase
from mm_api.schema.training import TrainingBase
from mm_api.schema.weight import WeightCreate
from mm_api.settings import settings
from mm_api.tests.utils.generations import create_hunts, create_trainings

fake = Faker()
_engine = create_async_engine(str(settings.db_url))
SessionLocal = sessionmaker(bind=_engine, class_=AsyncSession, expire_on_commit=False)  # type: ignore


async def seed_data() -> None:
    async with _engine.begin() as connection:
        async with AsyncSession(connection, expire_on_commit=False) as session:
            logger.info("Seeding data")
            falconer = create_falconer()
            falconer.id = "user_2ifMt89Ay39uwvtLQUijf7OGCq5"
            logger.info("Creating falconer {}", falconer.id)

            falconer_dao = FalconerDAO(session=session)
            bird_dao = BirdDAO(session=session)
            weight_dao = WeightDAO(session=session)
            feeding_dao = FeedingDAO(session=session)
            training_dao = TrainingDAO(session=session)
            hunt_dao = HuntDAO(session=session)

            await falconer_dao.create(falconer)

            for i in range(1, 6):
                bird = create_bird(falconer.id)  # type: ignore
                trainings, weights, feedings, date = create_trainings(
                    bird.id,  # type: ignore
                    bird.gender,
                )
                hunts, hunt_weights, hunt_feedings = create_hunts(
                    bird.id,  # type: ignore
                    weights[-1].weight,
                    date,
                )
                weights.extend(hunt_weights)
                feedings.extend(hunt_feedings)

                await bird_dao.create(bird)
                for w in weights:
                    await weight_dao.create(w)
                for f in feedings:
                    await feeding_dao.create(f)
                for t in trainings:
                    await training_dao.create(t)
                for h in hunts:
                    await hunt_dao.create(h)


def create_falconer() -> FalconerCreate:
    uid = str(uuid4())
    logger.info("{}", uid)
    return FalconerCreate(
        id=uid,
        name=fake.name(),
        permit_class=fake.random_element(elements=("apprentice", "general", "master")),
        permit_number=str(fake.random_number(digits=6)),
    )


if __name__ == "__main__":
    asyncio.run(seed_data())
