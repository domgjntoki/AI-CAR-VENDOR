from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncConnection

from src.database import get_db_connection
from src.exceptions import CarNotFoundError, CarUpdateError, CarDeletionError, CarCreationError
from src.schemas import CarCreate, CarResponse, CarUpdate, CarFilter
from src.services import (
    create_car,
    create_multiple_cars,
    get_car_by_id,
    get_all_cars,
    update_car,
    delete_car, get_filtered_cars,
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
async def retrieve_car(car_id: int, connection: AsyncConnection = Depends(get_db_connection)):
    car = await get_car_by_id(car_id, connection)
    if not car:
        raise CarNotFoundError()
    return car


@router.patch("/cars/{car_id}", response_model=CarResponse)
async def modify_car(
    car_id: int, car_data: CarUpdate, connection: AsyncConnection = Depends(get_db_connection)
):
    updated_car = await update_car(car_id, car_data.model_dump(exclude_unset=True), connection)
    if not updated_car:
        raise CarUpdateError()
    return updated_car


@router.delete("/cars/{car_id}", status_code=204)
async def remove_car(car_id: int, connection: AsyncConnection = Depends(get_db_connection)):
    try:
        await delete_car(car_id, connection)
    except Exception:
        raise CarDeletionError()


@router.get("/cars")
async def filter_cars(
    brand: str | None = Query(None),
    year: int | None = Query(None),
    fuel_type: str | None = Query(None),
    connection: AsyncConnection = Depends(get_db_connection),
):
    filters = {}
    if brand:
        filters["brand"] = brand
    if year:
        filters["year"] = year
    if fuel_type:
        filters["fuel_type"] = fuel_type

    cars = await get_all_cars(connection, filters)
    return {"results": cars}

from fastapi import Body

@router.post("/cars/filter", response_model=list[CarResponse])
async def filter_cars(
    filters: CarFilter = Body(...),
    connection: AsyncConnection = Depends(get_db_connection),
):
    return await get_filtered_cars(filters.model_dump(exclude_none=True), connection)