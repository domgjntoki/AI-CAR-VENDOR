from sqlalchemy import insert, delete, select, update, and_
from sqlalchemy.ext.asyncio import AsyncConnection

from src.database import cars, fetch_all, fetch_one, execute
from src.schemas import CarResponse, CarFilter


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


async def update_car(car_id: int, car_data: dict, connection: AsyncConnection) -> CarResponse | None:
    query = (
        update(cars)
        .where(cars.c.id == car_id)
        .values(**car_data)
        .returning(cars)
    )
    result = await fetch_one(query, connection, commit_after=True)
    return CarResponse(**result) if result else None


async def delete_car(car_id: int, connection: AsyncConnection) -> None:
    query = delete(cars).where(cars.c.id == car_id)
    await execute(query, connection, commit_after=True)


# Default mapping for common operations
DEFAULT_OPERATIONS = {
    "list": lambda col, value: col.in_(value),
    "int": lambda col, value: col == value,
    "float": lambda col, value: col == value,
}

# Dynamically generate FILTER_MAPPING
FILTER_MAPPING = {
    field_name: DEFAULT_OPERATIONS.get(field.type_.__name__, lambda col, value: col == value)
    for field_name, field in CarFilter.model_fields.items()
}

async def get_filtered_cars(filters: dict, connection: AsyncConnection) -> list[dict]:
    query_filters = []
    for key, value in filters.items():
        if value is not None and key in FILTER_MAPPING:
            query_filters.append(FILTER_MAPPING[key](getattr(cars.c, key), value))

    query = cars.select().where(and_(*query_filters)) if query_filters else cars.select()
    results = await fetch_all(query, connection)
    return results