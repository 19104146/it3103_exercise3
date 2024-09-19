from typing_extensions import List

from models import Item, OrderRead

next_id = 2
orders: List[OrderRead] = [
    OrderRead(
        id=1,
        customer_key=1,
        items=[
            Item(product_key=1, quantity=1),
        ],
    ),
]
