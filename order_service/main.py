from decimal import ROUND_DOWN, Decimal
from functools import lru_cache

import requests
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
from requests import HTTPError, RequestException
from typing_extensions import Any, Dict, List


class Item(BaseModel):
    product_key: int
    quantity: int = Field(gt=0)


class Order(BaseModel):
    id: int = Field(gt=0)
    customer_key: int = Field(gt=0)
    items: List[Item]

    @validator("items")
    def validate_items(cls, v: Item):
        if not v:
            raise ValueError("Order must contain at least one item")
        return v


class CustomerDetail(BaseModel):
    name: str


class ProductDetail(BaseModel):
    name: str
    price: Decimal = Field(gt=0)

    @validator("price")
    def validate_price(cls, v: Decimal):
        return v.quantize(Decimal("0.01"), rounding=ROUND_DOWN)

    class Config:
        json_encoders = {Decimal: lambda v: str(v)}


class ItemDetail(BaseModel):
    product: ProductDetail
    quantity: int = Field(gt=0)


class OrderDetail(BaseModel):
    id: int = Field(gt=0)
    customer: CustomerDetail
    items: List[ItemDetail]


class ServiceUnavailableError(Exception):
    pass


app = FastAPI()

orders: List[Order] = [
    Order(
        id=1,
        customer_key=1,
        items=[
            Item(product_key=1, quantity=1),
        ],
    ),
]


@lru_cache()
def get_settings():
    return {
        "product_service_url": "http://product_service:3001",
        "customer_service_url": "http://customer_service:3002",
    }


def fetch(url: str, detail: str) -> Dict[str, Any]:
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except RequestException as error:
        if isinstance(error, HTTPError) and error.response.status_code == 404:
            raise HTTPException(status_code=404, detail=detail)
        raise ServiceUnavailableError(f"Error fetching data: {str(error)}")


def get_customer(customer_key: int, settings: Dict = Depends(get_settings)) -> CustomerDetail:
    try:
        customer = fetch(f"{settings['customer_service_url']}/customers/{customer_key}", "Customer does not exist")
        return CustomerDetail(name=customer["name"])
    except ServiceUnavailableError as error:
        raise HTTPException(status_code=503, detail=str(error))


def get_product(product_key: int, settings: Dict = Depends(get_settings)) -> ProductDetail:
    try:
        product = fetch(f"{settings['product_service_url']}/products/{product_key}", "Product does not exist")
        product["price"] = Decimal(str(product["price"]))
        return ProductDetail(**product)
    except ServiceUnavailableError as error:
        raise HTTPException(status_code=503, detail=str(error))


@app.get("/orders", response_model=List[OrderDetail])
def list_orders(settings: dict = Depends(get_settings)) -> List[OrderDetail]:
    try:
        return [get_order_detail(order, settings) for order in orders]
    except ServiceUnavailableError as error:
        raise HTTPException(status_code=503, detail=str(error))


def get_order_detail(order: Order, settings: Dict) -> OrderDetail:
    customer = get_customer(order.customer_key, settings)
    items = [get_item_detail(item, settings) for item in order.items]
    return OrderDetail(id=order.id, customer=customer, items=items)


def get_item_detail(item: Item, settings: Dict) -> ItemDetail:
    product = get_product(item.product_key, settings)
    return ItemDetail(product=product, quantity=item.quantity)


@app.post("/orders", response_model=Order, status_code=201)
def create_order(new_order: Order, settings: Dict = Depends(get_settings)) -> Order:
    if any(order.id == new_order.id for order in orders):
        raise HTTPException(status_code=409, detail="Order already exists")

    try:
        get_customer(new_order.customer_key, settings)
        for item in new_order.items:
            get_product(item.product_key, settings)
    except ServiceUnavailableError as error:
        raise HTTPException(status_code=503, detail=str(error))

    orders.append(new_order)
    return new_order


@app.get("/orders/{order_id}", response_model=OrderDetail)
def read_order(order_id: int, settings: Dict = Depends(get_settings)):
    order = find_order(order_id)
    try:
        return get_order_detail(order, settings)
    except ServiceUnavailableError as error:
        raise HTTPException(status_code=503, detail=str(error))


def find_order(order_id: int) -> Order:
    order = next((order for order in orders if order.id == order_id), None)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


def find_order_index(order_id: int) -> int:
    order_index = next((index for index, order in enumerate(orders) if order.id == order_id), None)
    if order_index is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order_index


@app.put("/orders/{order_id}", response_model=Order)
def update_order(order_id: int, updated_order: Order, settings: Dict = Depends(get_settings)):
    order_index = find_order_index(order_id)

    try:
        get_customer(updated_order.customer_key, settings)
        for item in updated_order.items:
            get_product(item.product_key, settings)
    except ServiceUnavailableError as error:
        raise HTTPException(status_code=503, detail=str(error))

    orders[order_index] = updated_order
    return update_order


@app.delete("/orders/{order_id}", response_model=Order)
def delete_order(order_id: int) -> Order:
    order_index = find_order_index(order_id)
    return orders.pop(order_index)
