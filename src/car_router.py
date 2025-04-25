from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncConnection

from src.database import get_db_connection
from src.exceptions import (
    CarCreationError,
    CarDeletionError,
    CarNotFoundError,
    CarUpdateError,
)
from src.schemas import CarCreate, CarFilter, CarResponse, CarUpdate
from src.services import (
    create_car,
    create_multiple_cars,
    delete_car,
    get_all_cars,
    get_car_by_id,
    get_filtered_cars,
    update_car,
)

router = APIRouter(
    prefix="/api/v1",
    tags=["cars"],
)


@router.post("/cars", response_model=CarResponse, status_code=201)
async def add_car(
    car_data: CarCreate, connection: AsyncConnection = Depends(get_db_connection)
):
    car = await create_car(car_data.model_dump(), connection)
    if not car:
        raise CarCreationError()
    return car


@router.post("/cars/bulk", response_model=list[CarResponse], status_code=201)
async def add_multiple_cars(
    cars_data: list[CarCreate], connection: AsyncConnection = Depends(get_db_connection)
):
    cars = await create_multiple_cars(
        [car.model_dump() for car in cars_data], connection
    )
    if not cars:
        raise CarCreationError(detail="Failed to create cars")
    return cars


@router.get("/cars", response_model=list[CarResponse])
async def list_cars(connection: AsyncConnection = Depends(get_db_connection)):
    return await get_all_cars(connection)


@router.get("/cars/{car_id}", response_model=CarResponse)
async def retrieve_car(
    car_id: int, connection: AsyncConnection = Depends(get_db_connection)
):
    car = await get_car_by_id(car_id, connection)
    if not car:
        raise CarNotFoundError()
    return car


@router.patch("/cars/{car_id}", response_model=CarResponse)
async def modify_car(
    car_id: int,
    car_data: CarUpdate,
    connection: AsyncConnection = Depends(get_db_connection),
):
    updated_car = await update_car(
        car_id, car_data.model_dump(exclude_unset=True), connection
    )
    if not updated_car:
        raise CarUpdateError()
    return updated_car


@router.delete("/cars/{car_id}", status_code=204)
async def remove_car(
    car_id: int, connection: AsyncConnection = Depends(get_db_connection)
):
    try:
        await delete_car(car_id, connection)
    except Exception:
        raise CarDeletionError()


@router.post("/cars/filter", response_model=list[CarResponse])
async def filter_cars(
    filters: CarFilter = Body(...),
    connection: AsyncConnection = Depends(get_db_connection),
):
    return await get_filtered_cars(filters.model_dump(exclude_none=True), connection)
