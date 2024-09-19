from functools import cache

import requests
from fastapi import Depends, HTTPException, status
from requests.exceptions import HTTPError, RequestException
from typing_extensions import Any, Dict, Optional, Union

from database import orders
from models import (
    CustomerDetail,
    Item,
    ItemDetail,
    OrderDetail,
    OrderRead,
    ProductDetail,
    ServiceUnavailableError,
)


@cache
def get_settings() -> Dict[str, str]:
    return {
        "customer_service_url": "http://customer_service:3002",
        "product_service_url": "http://product_service:3001",
    }


def get_order(order_id: int) -> Optional[OrderRead]:
    return next((o for o in orders if o.id == order_id), None)


# HTTP-related Functions
def fetch(url: str, detail: str) -> Dict[str, Any]:
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        if isinstance(e, HTTPError) and e.response.status_code == 404:
            raise HTTPException(status_code=404, detail=detail)
        raise ServiceUnavailableError(f"Error fetching data: {str(e)}")


def get_customer_detail(
    customer_id: int,
    settings: Dict = Depends(get_settings),
) -> CustomerDetail:
    try:
        customer = fetch(
            f"{settings['customer_service_url']}/customers/{customer_id}",
            "Customer does not exist",
        )
        return CustomerDetail(**customer)
    except ServiceUnavailableError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )


def get_product_detail(
    product_id: int,
    settings: Dict = Depends(get_settings),
) -> ProductDetail:
    try:
        product = fetch(
            f"{settings['product_service_url']}/products/{product_id}",
            "Product does not exist",
        )
        return ProductDetail(**product)
    except ServiceUnavailableError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )


def get_item_detail(
    item: Union[Item, Dict[str, int]], settings: Dict
) -> ItemDetail:
    product_key = (
        item.product_key if isinstance(item, Item) else item["product_key"]
    )
    quantity = item.quantity if isinstance(item, Item) else item["quantity"]
    product = get_product_detail(product_key, settings)
    return ItemDetail(product=product, quantity=quantity)


def get_order_detail(order: OrderRead, settings: Dict) -> OrderDetail:
    customer = get_customer_detail(order.customer_key, settings)
    items = [get_item_detail(item, settings) for item in order.items]
    return OrderDetail(id=order.id, customer=customer, items=items)
