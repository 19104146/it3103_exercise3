from typing_extensions import Optional

from database import customers
from models import CustomerRead


def get_customer(customer_id: int) -> Optional[CustomerRead]:
    return next((c for c in customers if c.id == customer_id), None)
