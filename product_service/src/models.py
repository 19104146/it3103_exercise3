from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_serializer,
)
from typing_extensions import Any, Dict


class BaseProduct(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        strict=True,
        json_encoders={Decimal: lambda v: str(v)},
    )

    name: str = Field(..., min_length=1, max_length=100)
    price: Decimal = Field(..., decimal_places=2, gt=0, strict=False)


class ProductRead(BaseProduct):
    id: int = Field(..., gt=0)

    @model_serializer(when_used="json")
    def ser_model(self) -> Dict[str, Any]:
        attributes = self.dict()
        return {"id": attributes.pop("id"), **attributes}


class ProductWrite(BaseProduct):
    pass
