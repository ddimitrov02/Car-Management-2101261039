from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

class Garage(BaseModel):
    id: int
    name: str
    location: str
    city: str
    capacity: int

class Car(BaseModel):
    id: int
    make: str
    model: str
    production_year: int
    license_plate: str
    garage_ids: List[int]

class MaintenanceRequest(BaseModel):
    id: int
    car_id: int
    service_type: str
    scheduled_date: str
    garage_id: int

garages = []
cars = []
maintenance_requests = []

# Управление на сервизите
@app.post("/garages", status_code=201)
def create_garage(garage: Garage):
    garages.append(garage)
    return garage

@app.get("/garages", response_model=List[Garage])
def get_garages(city: Optional[str] = None):
    if city:
        return [garage for garage in garages if garage.city == city]
    return garages

@app.get("/garages/{garage_id}", response_model=Garage)
def get_garage_by_id(garage_id: int):
    garage = next((g for g in garages if g.id == garage_id), None)
    if not garage:
        raise HTTPException(status_code=404, detail="Сервизът не е намерен")
    return garage

@app.put("/garages/{garage_id}", response_model=Garage)
def update_garage(garage_id: int, updated_garage: Garage):
    index = next((i for i, g in enumerate(garages) if g.id == garage_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Сервизът не е намерен")
    garages[index] = updated_garage
    return updated_garage

@app.delete("/garages/{garage_id}", status_code=204)
def delete_garage(garage_id: int):
    global garages
    garages = [g for g in garages if g.id != garage_id]
    return

# Управление на автомобилите
@app.post("/cars", status_code=201)
def create_car(car: Car):
    cars.append(car)
    return car

@app.get("/cars", response_model=List[Car])
def get_cars(make: Optional[str] = None, garage_id: Optional[int] = None, from_year: Optional[int] = None, to_year: Optional[int] = None):
    result = cars
    if make:
        result = [car for car in result if car.make == make]
    if garage_id:
        result = [car for car in result if garage_id in car.garage_ids]
    if from_year:
        result = [car for car in result if car.production_year >= from_year]
    if to_year:
        result = [car for car in result if car.production_year <= to_year]
    return result

@app.get("/cars/{car_id}", response_model=Car)
def get_car_by_id(car_id: int):
    car = next((c for c in cars if c.id == car_id), None)
    if not car:
        raise HTTPException(status_code=404, detail="Автомобилът не е намерен")
    return car

@app.put("/cars/{car_id}", response_model=Car)
def update_car(car_id: int, updated_car: Car):
    index = next((i for i, c in enumerate(cars) if c.id == car_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Автомобилът не е намерен")
    cars[index] = updated_car
    return updated_car

@app.delete("/cars/{car_id}", status_code=204)
def delete_car(car_id: int):
    global cars
    cars = [c for c in cars if c.id != car_id]
    return

# Управление на заявките за поддръжка
@app.post("/maintenance", status_code=201)
def create_maintenance_request(request: MaintenanceRequest):
    # Проверка дали сервизът съществува и дали има свободни места
    garage = next((g for g in garages if g.id == request.garage_id), None)
    if not garage:
        raise HTTPException(status_code=404, detail="Сервизът не е намерен")
    # Проверка за дублиране на заявки
    conflicts = [r for r in maintenance_requests if r.garage_id == request.garage_id and r.scheduled_date == request.scheduled_date]
    if len(conflicts) >= garage.capacity:
        raise HTTPException(status_code=400, detail="Няма свободни места в сервиза за избраната дата")
    maintenance_requests.append(request)
    return request

@app.get("/maintenance", response_model=List[MaintenanceRequest])
def get_maintenance_requests(car_id: Optional[int] = None, garage_id: Optional[int] = None, start_date: Optional[str] = None, end_date: Optional[str] = None):
    result = maintenance_requests
    if car_id:
        result = [req for req in result if req.car_id == car_id]
    if garage_id:
        result = [req for req in result if req.garage_id == garage_id]
    if start_date:
        result = [req for req in result if req.scheduled_date >= start_date]
    if end_date:
        result = [req for req in result if req.scheduled_date <= end_date]
    return result

@app.get("/maintenance/{request_id}", response_model=MaintenanceRequest)
def get_maintenance_request_by_id(request_id: int):
    request = next((r for r in maintenance_requests if r.id == request_id), None)
    if not request:
        raise HTTPException(status_code=404, detail="Не е намерена заявка за поддръжка")
    return request

@app.put("/maintenance/{request_id}", response_model=MaintenanceRequest)
def update_maintenance_request(request_id: int, updated_request: MaintenanceRequest):
    index = next((i for i, r in enumerate(maintenance_requests) if r.id == request_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Не е намерена заявка за поддръжка")
    garage = next((g for g in garages if g.id == updated_request.garage_id), None)
    if not garage:
        raise HTTPException(status_code=404, detail="Не е намерен сервиз")
    conflicts = [r for r in maintenance_requests if r.garage_id == updated_request.garage_id and r.scheduled_date == updated_request.scheduled_date and r.id != request_id]
    if len(conflicts) >= garage.capacity:
        raise HTTPException(status_code=400, detail="Няма свободни места в сервиза за избраната дата")
    maintenance_requests[index] = updated_request
    return updated_request

@app.delete("/maintenance/{request_id}", status_code=204)
def delete_maintenance_request(request_id: int):
    global maintenance_requests
    maintenance_requests = [r for r in maintenance_requests if r.id != request_id]
    return
