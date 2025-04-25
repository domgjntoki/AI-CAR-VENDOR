from sqlalchemy import and_, delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncConnection

from src.constants import FILTER_MAPPING
from src.database import cars, execute, fetch_all, fetch_one
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


async def get_car_by_id(car_id: int, connection: AsyncConnection) -> CarResponse | None:
    query = select(cars).where(cars.c.id == car_id)
    result = await fetch_one(query, connection)
    return CarResponse(**result) if result else None


async def get_all_cars(connection: AsyncConnection) -> list[CarResponse]:
    query = select(cars)
    results = await fetch_all(query, connection)
    return [CarResponse(**car) for car in results]


async def update_car(
    car_id: int, car_data: dict, connection: AsyncConnection
) -> CarResponse | None:
    query = update(cars).where(cars.c.id == car_id).values(**car_data).returning(cars)
    result = await fetch_one(query, connection, commit_after=True)
    return CarResponse(**result) if result else None


async def delete_car(car_id: int, connection: AsyncConnection) -> None:
    query = delete(cars).where(cars.c.id == car_id)
    await execute(query, connection, commit_after=True)


async def get_filtered_cars(filters: dict, connection: AsyncConnection) -> list[dict]:
    query_filters = []
    for key, value in filters.items():
        if value is not None and key in FILTER_MAPPING and value:
            # Map logical keys (e.g., min_year) to actual column names (e.g., year)
            column_name = key.replace("min_", "").replace(
                "max_", ""
            )  # Extract base column name
            if hasattr(cars.c, column_name):
                column = getattr(cars.c, column_name)
                query_filters.append(FILTER_MAPPING[key](column, value))
            else:
                raise AttributeError(
                    f"Column '{column_name}' does not exist in the 'cars' table."
                )

    query = (
        cars.select().where(and_(*query_filters)) if query_filters else cars.select()
    )
    results = await fetch_all(query, connection)
    return results
