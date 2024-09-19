from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_serializer,
)
from typing_extensions import Any, Dict, List


# Raw Models
class Item(BaseModel):
    product_key: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


class BaseOrder(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, strict=True)

    customer_key: int = Field(..., gt=0)
    items: List[Item] = Field(..., min_length=1)


class OrderRead(BaseOrder):
    id: int = Field(..., gt=0)

    @model_serializer(when_used="json")
    def ser_model(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "customer_key": self.customer_key,
            "items": [item.model_dump() for item in self.items],
        }


class OrderWrite(BaseOrder):
    pass


# Detailed Models
class CustomerDetail(BaseModel):
    name: str = Field(..., min_length=1, max_length=747)


class ProductDetail(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: Decimal = Field(..., decimal_places=2, gt=0, strict=False)


class ItemDetail(BaseModel):
    product: ProductDetail = Field(...)
    quantity: int = Field(..., gt=0)


class OrderDetail(BaseModel):
    id: int = Field(..., gt=0)
    customer: CustomerDetail = Field(...)
    items: List[ItemDetail] = Field(...)


# Custom Exceptions
class ServiceUnavailableError(Exception):
    pass
