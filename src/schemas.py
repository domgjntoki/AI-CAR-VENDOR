from typing import Optional

from pydantic import BaseModel, Field


class CarBase(BaseModel):
    brand: str
    model: str
    year: int
    engine: str | None = None
    fuel_type: str | None = None
    color: str | None = None
    mileage: int | None = None
    doors: int | None = None
    transmission: str | None = None
    price: float | None = None


class CarCreate(CarBase):
    pass


class CarUpdate(BaseModel):
    brand: str | None = None
    model: str | None = None
    year: int | None = None
    engine: str | None = None
    fuel_type: str | None = None
    color: str | None = None
    mileage: int | None = None
    doors: int | None = None
    transmission: str | None = None
    price: float | None = None


class CarResponse(CarBase):
    id: int = Field(..., description="Car ID")
