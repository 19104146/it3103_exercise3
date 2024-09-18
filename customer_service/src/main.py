from fastapi import Body, FastAPI, HTTPException, Path, status
from typing_extensions import List

from database import customers, next_id
from helpers import get_customer
from models import CustomerRead, CustomerWrite

app = FastAPI()


@app.get("/customers", response_model=List[CustomerRead])
def list_customers() -> List[CustomerRead]:
    return customers


@app.post(
    "/customers",
    response_model=CustomerRead,
    status_code=status.HTTP_201_CREATED,
)
def create_customer(customer: CustomerWrite = Body(...)) -> CustomerRead:
    global next_id
    new_customer = CustomerRead(id=next_id, **customer.dict())
    customers.append(new_customer)
    next_id += 1
    return new_customer


@app.get("/customers/{customer_id}", response_model=CustomerRead)
def read_customer(customer_id: int = Path(..., gt=0)) -> CustomerRead:
    if customer := get_customer(customer_id):
        return customer
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
    )


@app.put(
    "/customers/{customer_id}",
    response_model=CustomerRead,
    status_code=status.HTTP_201_CREATED,
)
def update_customer(
    customer_id: int = Path(..., gt=0), customer: CustomerWrite = Body(...)
) -> CustomerRead:
    if existing_customer := get_customer(customer_id):
        updated_customer = existing_customer.copy(update=customer.dict())
        index = customers.index(existing_customer)
        customers[index] = updated_customer
        return updated_customer
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
    )


@app.delete("/customers/{customer_id}", response_model=CustomerRead)
def delete_customer(customer_id: int = Path(..., gt=0)):
    if customer := get_customer(customer_id):
        customers.remove(customer)
        return customer
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
    )
