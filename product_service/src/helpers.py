from typing_extensions import Optional

from database import products
from models import ProductRead


def get_product(product_id: int) -> Optional[ProductRead]:
    return next((p for p in products if p.id == product_id), None)
