from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncConnection

from src.services import create_car
from src.database import get_db_connection
from src.schemas import CarCreate, CarResponse
from src.exceptions import CarCreationError

router = APIRouter()

@router.post("/cars", response_model=CarResponse, status_code=201)
async def add_car(
    car_data: CarCreate,
    connection: AsyncConnection = Depends(get_db_connection)
):
    car = await create_car(car_data.model_dump(), connection)
    if not car:
        raise CarCreationError()
    return car