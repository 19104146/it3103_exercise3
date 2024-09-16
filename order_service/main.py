from typing import List

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class OrderItem(BaseModel):
    product_key: int
    quantity: int


class Order(BaseModel):
    id: int
    customer_key: int
    order_items: List[OrderItem]


orders: List[Order] = [
    Order(
        id=1, customer_key=1, order_items=[OrderItem(product_key=2, quantity=5), OrderItem(product_key=1, quantity=3)]
    ),
    Order(id=2, customer_key=2, order_items=[OrderItem(product_key=1, quantity=3)]),
]


@app.get("/orders", response_model=List[dict])
def list_orders():
    order_details = []

    for o in orders:
        order_detail = {}
        order_detail["id"] = o.id

        response = requests.get(f"http://localhost:3002/customers/{o.customer_key}")
        if not response.ok:
            raise HTTPException(status_code=response.status_code, detail="Customer not found")
        customer = response.json()
        order_detail["customer"] = customer

        order_item_details = []
        for oi in o.order_items:
            response = requests.get(f"http://localhost:3001/products/{oi.product_key}")
            if not response.ok:
                raise HTTPException(status_code=response.status_code, detail="Product not found")
            product = response.json()
            product["quantity"] = oi.quantity
            order_item_details.append({"product": product})

        order_detail["order_items"] = order_item_details
        order_details.append(order_detail)

    return order_details


@app.post("/orders", response_model=Order)
def create_order(order: Order):
    if any(o.id == order.id for o in orders):
        raise HTTPException(status_code=409, detail="Order already exists")

    response = requests.get("http://localhost:3002/customers")
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail="Unable to fetch customers")
    customers = response.json()
    if not any(c["id"] == order.customer_key for c in customers):
        raise HTTPException(status_code=404, detail="Customer not found")

    response = requests.get("http://localhost:3001/products")
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail="Unable to fetch products")
    products = response.json()
    product_keys = {p["id"] for p in products}
    for item in order.order_items:
        if item.product_key not in product_keys:
            raise HTTPException(status_code=404, detail="Product not found")

    orders.append(order)
    return order

@app.delete("/orders/{order_id}")
def delete_order(order_id: int):
    index = next((i for i, o in enumerate(orders) if o.id == order_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Order notsssss found")
    return orders.pop(index)

