from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncConnection

from src.database import cars, fetch_one
from src.schemas import CarResponse

async def create_car(car_data: dict, connection: AsyncConnection) -> CarResponse | None:
    query = insert(cars).values(**car_data).returning(cars)
    result = await fetch_one(query, connection, commit_after=True)
    return CarResponse(**result) if result else None