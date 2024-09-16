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
    Order(id=1, customer_key=1, order_items=[OrderItem(product_key=2, quantity=5)]),
    Order(id=2, customer_key=2, order_items=[OrderItem(product_key=1, quantity=3)]),
]


@app.get("/orders", response_model=List[dict])
def list_orders():
    order_details = []

    for o in orders:
        order_detail = {}

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
