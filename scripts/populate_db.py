import asyncio
import httpx
from faker import Faker

API_URL = "http://localhost:8000/api/v1/cars/bulk"  # Replace with your API URL
NUM_VEHICLES = 400

fake = Faker()

def generate_fake_cars(num: int) -> list[dict]:
    """Generate a list of fake car data."""
    car_companies = [
        "Toyota", "Ford", "Chevrolet", "Honda", "Nissan",
        "BMW", "Mercedes-Benz", "Volkswagen", "Hyundai", "Kia"
    ]  # Add more real-world car companies as needed

    cars = []
    for _ in range(num):
        car = {
            "brand": fake.random_element(elements=car_companies),
            "model": fake.word(),
            "year": fake.random_int(min=1990, max=2023),
            "engine": f"{fake.random_int(min=1, max=5)}.{fake.random_int(min=0, max=9)}L",
            "fuel_type": fake.random_element(elements=["Gasoline", "Diesel", "Electric", "Hybrid"]),
            "color": fake.color_name(),
            "mileage": fake.random_int(min=0, max=300000),
            "doors": fake.random_int(min=2, max=5),
            "transmission": fake.random_element(elements=["Manual", "Automatic"]),
            "price": round(fake.pyfloat(min_value=5000, max_value=100000, right_digits=2), 2),
        }
        cars.append(car)
    return cars

async def populate_database():
    """Populate the database with fake car data using the API."""
    cars_data = generate_fake_cars(NUM_VEHICLES)
    async with httpx.AsyncClient() as client:
        response = await client.post(API_URL, json=cars_data)
        if response.status_code == 201:
            print(f"Successfully added {NUM_VEHICLES} cars to the database.")
        else:
            print(f"Failed to add cars. Status code: {response.status_code}, Response: {response.text}")

if __name__ == "__main__":
    asyncio.run(populate_database())