from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncConnection

from src.database import cars, fetch_all, fetch_one
from src.schemas import CarResponse


async def create_car(car_data: dict, connection: AsyncConnection) -> CarResponse | None:
    query = insert(cars).values(**car_data).returning(cars)
    result = await fetch_one(query, connection, commit_after=True)
    return CarResponse(**result) if result else None


async def create_multiple_cars(
    cars_data: list[dict], connection: AsyncConnection
) -> list[dict] | None:
    query = insert(cars).values(cars_data).returning(cars)
    results = await fetch_all(query, connection, commit_after=True)
    return results if results else None
