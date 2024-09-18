from pydantic import BaseModel, Field


class CustomerRead(BaseModel):
    id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=747)

    class Config:
        from_attributes = True


class CustomerWrite(BaseModel):
    name: str = Field(..., min_length=1, max_length=747)
