from typing import List

from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from pydantic import BaseModel


class Customer(BaseModel):
    id: int
    username: str
    email: str
    password: str


customers: List[Customer] = [
    Customer(id=1, username="carlo", email="carlo@gmail.com", password="carlo"),
    Customer(id=2, username="achille", email="achille@gmail.com", password="achille"),
]

app = FastAPI()


@app.get("/customers", response_model=List[Customer])
def list_customers():
    return customers


@app.post("/customers", response_model=Customer, status_code=201)
def create_customer(customer: Customer):
    if any(c.id == customer.id for c in customers):
        raise HTTPException(status_code=400, detail="Customer with this ID already exists")
    customers.append(customer)
    return customer


@app.get("/customers/{customer_id}", response_model=Customer)
def read_customer(customer_id: int):
    customer = next((c for c in customers if c.id == customer_id), None)
    if customer is None:
        raise HTTPException(status_code=404, detail="User not found")
    return customer


@app.put("/customers/{customer_id}", response_model=Customer, status_code=201)
def update_customer(customer_id: int, customer: Customer):
    index = next((i for i, c in enumerate(customers) if c.id == customer_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="User not found")
    customers[index] = customer
    return customers[index]


@app.delete("/customers/{customer_id}", response_model=Customer)
def delete_customer(customer_id: int):
    index = next((i for i, c in enumerate(customers) if c.id == customer_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="User not found")
    return customers.pop(index)
