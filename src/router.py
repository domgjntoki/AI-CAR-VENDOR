from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncConnection

from src.database import get_db_connection
from src.exceptions import CarCreationError
from src.schemas import CarCreate, CarResponse
from src.services import create_car, create_multiple_cars

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
