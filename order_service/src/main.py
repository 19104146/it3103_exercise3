from fastapi import Body, Depends, FastAPI, HTTPException, Path, status
from typing_extensions import Dict, List

from database import next_id, orders
from helpers import (
    get_customer_detail,
    get_order,
    get_order_detail,
    get_product_detail,
    get_settings,
)
from models import (
    Item,
    OrderDetail,
    OrderRead,
    OrderWrite,
    ServiceUnavailableError,
)

app = FastAPI()


@app.get("/orders", response_model=List[OrderDetail])
def list_orders(settings: Dict = Depends(get_settings)) -> List[OrderDetail]:
    try:
        return [get_order_detail(order, settings) for order in orders]
    except ServiceUnavailableError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )


@app.post(
    "/orders",
    response_model=OrderRead,
    status_code=status.HTTP_201_CREATED,
)
def create_order(
    order: OrderWrite = Body(...),
    settings: Dict = Depends(get_settings),
) -> OrderRead:
    try:
        get_customer_detail(order.customer_key, settings)
        for item in order.items:
            get_product_detail(item.product_key, settings)
    except ServiceUnavailableError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )

    global next_id

    new_order = OrderRead(
        id=next_id,
        customer_key=order.customer_key,
        items=[Item(**item.dict()) for item in order.items],
    )

    orders.append(new_order)
    next_id += 1
    return new_order


@app.get("/orders/{order_id}", response_model=OrderDetail)
def read_order(
    order_id: int = Path(..., gt=0),
    settings: Dict = Depends(get_settings),
) -> OrderDetail:
    if order := get_order(order_id):
        try:
            return get_order_detail(order, settings)
        except ServiceUnavailableError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(e),
            )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Order not found",
    )


@app.put("/orders/{order_id}", response_model=OrderRead)
def update_order(
    order_id: int = Path(..., gt=0),
    order: OrderWrite = Body(...),
    settings: Dict = Depends(get_settings),
) -> OrderRead:
    try:
        get_customer_detail(order.customer_key, settings)
        for item in order.items:
            get_product_detail(item.product_key, settings)
    except ServiceUnavailableError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )

    if existing_order := get_order(order_id):
        updated_items = [Item(**item.dict()) for item in order.items]

        updated_order = OrderRead(
            id=existing_order.id,
            customer_key=order.customer_key,
            items=updated_items,
        )

        index = orders.index(existing_order)
        orders[index] = updated_order
        return updated_order
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Order not found",
    )


@app.delete("/orders/{order_id}", response_model=OrderRead)
def delete_order(order_id: int = Path(..., gt=0)) -> OrderRead:
    if order := get_order(order_id):
        orders.remove(order)
        return order
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Order not found",
    )
