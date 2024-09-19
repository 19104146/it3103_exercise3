from pydantic import BaseModel, ConfigDict, Field, model_serializer
from typing_extensions import Any, Dict


class BaseCustomer(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, strict=True)

    name: str = Field(..., min_length=1, max_length=747)


class CustomerRead(BaseCustomer):
    id: int = Field(..., gt=0)

    @model_serializer(when_used="json")
    def ser_model(self) -> Dict[str, Any]:
        attributes = self.dict()
        return {"id": attributes.pop("id"), **attributes}


class CustomerWrite(BaseCustomer):
    pass
