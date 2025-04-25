from pydantic import BaseModel, Field
from typing import Optional

class CarCreate(BaseModel):
    brand: str = Field(..., max_length=50)
    model: str = Field(..., max_length=50)
    year: int
    engine: Optional[str] = Field(None, max_length=20)
    fuel_type: Optional[str] = Field(None, max_length=20)
    color: Optional[str] = Field(None, max_length=30)
    mileage: Optional[int]
    doors: Optional[int]
    transmission: Optional[str] = Field(None, max_length=20)
    price: Optional[float]

class CarResponse(CarCreate):
    id: int