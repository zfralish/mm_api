import asyncio
from datetime import datetime
from uuid import UUID, uuid4

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

fake = Faker()
_engine = create_async_engine(str(settings.db_url))
SessionLocal = sessionmaker(bind=_engine, class_=AsyncSession, expire_on_commit=False)  # type: ignore


async def seed_data() -> None:
    async with _engine.begin() as connection:
        async with AsyncSession(connection, expire_on_commit=False) as session:
            logger.info("Seeding data")
            falconer = create_falconer()
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


def create_bird(falconer_id: str) -> BirdCreate:
    return BirdCreate(
        id=uuid4(),
        falconer_id=falconer_id,
        species=fake.random_element(
            elements=("peregrine", "goshawk", "kestrel", "red-tailed hawk"),
        ),
        name=fake.first_name(),
        gender=fake.random_element(elements=("male", "female")),
        trap_date=datetime(2023, 1, 1, 12, 34, 56),
    )


def create_weight(bird_id: UUID, time: datetime, weight: float) -> WeightCreate:
    return WeightCreate(
        id=uuid4(),
        bird_id=bird_id,  # type: ignore
        weight=weight,
        w_time=time,
    )


def create_feeding(
    bird_id: UUID,
    amount: float,
    time: datetime,
    start_weight: UUID,
    end_weight: UUID,
) -> FeedingBase:
    return FeedingBase(
        bird_id=bird_id,  # type: ignore
        amount=amount,
        f_time=time,
        food_type=fake.random_element(elements=("mice", "quail", "sparrow")),
        start_weight_id=start_weight,  # type: ignore
        end_weight_id=end_weight,  # type: ignore
    )


def create_trainings(
    bird_id: UUID,
    gender: str,
) -> tuple[list[TrainingBase], list[WeightCreate], list[FeedingBase], datetime]:
    weight = (
        np.random.uniform(900, 1200)
        if gender == "female"
        else np.random.uniform(700, 1000)
    )
    weight = round(weight, 2)

    trainings = []
    weights = []
    feedings = []
    date = datetime(2023, 9, 1, 12, 0, 0)
    day = 1
    hours = 12
    minutes = 0

    for i in range(1, 14):
        start_time = date.replace(day=day, hour=hours, minute=minutes)
        start_weight = create_weight(bird_id, start_time, weight)
        amount_fed = np.random.uniform(0.09 * weight, 0.11 * weight)
        end_time = start_time.replace(hour=hours + 1)
        end_weight = create_weight(bird_id, end_time, weight + amount_fed)
        feeding = create_feeding(
            bird_id,
            amount_fed,
            start_time,
            start_weight.id,  # type: ignore
            end_weight.id,  # type: ignore
        )
        training = TrainingBase(
            bird_id=bird_id,  # type: ignore
            start_time=start_time,
            end_time=end_time,
            performance=np.random.randint(1, 10),
            training_type=fake.random_element(
                elements=("hop-ups", "creance", "free-flight"),
            ),
            notes=fake.text(),
        )
        weight = end_weight.weight - np.random.uniform(0.09 * weight, 0.11 * weight)
        weights.append(start_weight)
        weights.append(end_weight)
        feedings.append(feeding)
        trainings.append(training)
        date = end_time
        day += 1

    return trainings, weights, feedings, date


def create_hunts(
    bird_id: UUID,
    incoming_weight: float,
    incoming_date: datetime,
) -> tuple[list[HuntBase], list[WeightCreate], list[FeedingBase]]:
    hunts = []
    weights = []
    feedings = []
    date = incoming_date
    weight = incoming_weight
    hours = 12

    for i in range(1, 14):
        start_time = date.replace(day=date.day + 1, hour=hours, minute=0)
        start_weight = create_weight(bird_id, start_time, weight)
        prey_count = np.random.randint(1, 8)
        amount_fed = np.random.uniform(0.09 * weight, 0.11 * weight)
        end_time = start_time.replace(hour=start_time.hour + 1)
        end_weight = create_weight(bird_id, end_time, start_weight.weight + amount_fed)
        feeding = create_feeding(
            bird_id,
            amount_fed,
            start_time,
            start_weight.id,  # type: ignore
            end_weight.id,  # type: ignore
        )
        hunt = HuntBase(
            bird_id=bird_id,  # type: ignore
            start_time=start_time,
            end_time=end_time,
            start_weight_id=start_weight.id,
            prey_type=fake.random_element(elements=("sparrow", "quail", "rabbit")),
            prey_count=prey_count,
            notes=fake.text(),
        )
        weights.append(start_weight)
        weights.append(end_weight)
        feedings.append(feeding)
        hunts.append(hunt)
        weight = end_weight.weight - np.random.uniform(0.09 * weight, 0.11 * weight)
        date = end_time

    return hunts, weights, feedings


if __name__ == "__main__":
    asyncio.run(seed_data())
