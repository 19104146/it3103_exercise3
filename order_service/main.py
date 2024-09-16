import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing_extensions import Any


class OrderItem(BaseModel):
    product_key: int
    quantity: int


class Order(BaseModel):
    order_id: int
    customer_key: int
    order_items: list[OrderItem]


class CustomerDetail(BaseModel):
    name: str


class ProductDetail(BaseModel):
    name: str
    price: float


class OrderItemDetail(BaseModel):
    product: ProductDetail
    quantity: int


class OrderDetail(BaseModel):
    order_id: int
    customer: CustomerDetail
    order_items: list[OrderItemDetail]


app = FastAPI()
orders: list[Order] = [
    Order(
        order_id=1,
        customer_key=1,
        order_items=[
            OrderItem(product_key=1, quantity=1),
        ],
    ),
]


def fetch(url: str, detail: str) -> dict[str, Any]:
    response = requests.get(url)
    if not response.ok:
        if response.status_code == 404:
            raise HTTPException(status_code=response.status_code, detail=detail)
        raise HTTPException(status_code=response.status_code)

    try:
        return response.json()
    except ValueError:
        raise HTTPException(status_code=500, detail="Invalid JSON response")


def get_customer(customer_key: int) -> CustomerDetail:
    customer = fetch(f"http://localhost:3002/customers/{customer_key}", "Customer not found")
    return CustomerDetail(name=customer["username"])


def get_product(product_key: int) -> ProductDetail:
    product = fetch(f"http://localhost:3001/products/{product_key}", "Product not found")
    return ProductDetail(**product)


@app.get("/orders", response_model=list[OrderDetail])
def list_orders() -> list[OrderDetail]:
    def get_order_items(order):
        products = [get_product(order_item.product_key) for order_item in order.order_items]
        return [
            OrderItemDetail(product=product, quantity=order_item.quantity)
            for product, order_item in zip(products, order.order_items)
        ]

    return [
        OrderDetail(
            order_id=order.order_id,
            customer=get_customer(order.customer_key),
            order_items=get_order_items(order),
        )
        for order in orders
    ]


@app.post("/orders", response_model=Order, status_code=201)
def create_order(order: Order):
    return


@app.get("/orders/{order_id}", response_model=OrderDetail)
def read_order(order_id: int):
    return


@app.put("/orders/{order_id}", response_model=Order, status_code=201)
def update_order(order_id: int, order: Order):
    return


@app.delete("/orders/{order_id}", response_model=Order)
def delete_order(order_id: int):
    return
