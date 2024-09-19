from decimal import Decimal

from typing_extensions import List

from models import ProductRead

next_id = 2
products: List[ProductRead] = [
    ProductRead(id=1, name="LEGO Set", price=Decimal("3391.78")),
]
