from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing_extensions import List


class Customer(BaseModel):
    id: int = Field(gt=0)
    name: str


app = FastAPI()

customers: List[Customer] = [
    Customer(id=1, name="Ean Velayo"),
]


@app.get("/customers", response_model=List[Customer])
def list_customers() -> List[Customer]:
    return customers


@app.post("/customers", response_model=Customer, status_code=201)
def create_customer(new_customer: Customer) -> Customer:
    if any(customer.id == new_customer.id for customer in customers):
        raise HTTPException(status_code=409, detail="Customer already exists")

    customers.append(new_customer)
    return new_customer


@app.get("/customers/{customer_id}", response_model=Customer)
def read_customer(customer_id: int) -> Customer:
    customer = next((customer for customer in customers if customer.id == customer_id), None)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@app.put("/customers/{customer_id}", response_model=Customer, status_code=201)
def update_customer(customer_id: int, updated_customer: Customer) -> Customer:
    customer_index = find_customer_index(customer_id)
    customers[customer_index] = updated_customer
    return updated_customer


def find_customer_index(customer_id: int) -> int:
    customer_index = next((index for index, customer in enumerate(customers) if customer.id == customer_id), None)
    if customer_index is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer_index


@app.delete("/customers/{customer_id}", response_model=Customer)
def delete_customer(customer_id: int) -> Customer:
    customer_index = find_customer_index(customer_id)
    return customers.pop(customer_index)
