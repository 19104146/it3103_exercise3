from decimal import ROUND_DOWN, Decimal

from pydantic import BaseModel, ConfigDict, Field, model_serializer, validator
from typing_extensions import Any, Dict


class BaseProduct(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        strict=True,
        json_encoders={Decimal: lambda v: str(v)},
    )

    name: str = Field(..., min_length=1, max_length=100)
    price: Decimal = Field(..., gt=0, strict=False)

    @validator("price")
    def validate_price(cls, v: Decimal):
        return v.quantize(Decimal("0.01"), rounding=ROUND_DOWN)


class ProductRead(BaseProduct):
    id: int = Field(..., gt=0)

    @model_serializer(when_used="json")
    def ser_model(self) -> Dict[str, Any]:
        attributes = self.dict()
        return {"id": attributes.pop("id"), **attributes}


class ProductWrite(BaseProduct):
    pass
