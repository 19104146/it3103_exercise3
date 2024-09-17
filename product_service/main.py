from decimal import ROUND_DOWN, Decimal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
from typing_extensions import List


class BaseProduct(BaseModel):
    name: str
    price: Decimal = Field(gt=0)

    @validator("price")
    def validate_price(cls, v: Decimal):
        return v.quantize(Decimal("0.01"), rounding=ROUND_DOWN)

    class Config:
        json_encoders = {Decimal: lambda v: str(v)}


class Product(BaseProduct):
    id: int = Field(gt=0)


app = FastAPI()

products: List[Product] = [
    Product(id=1, name="LEGO Set", price=Decimal("3391.78")),
]


@app.get("/products", response_model=List[Product])
def list_products():
    return products


@app.post("/products", response_model=Product, status_code=201)
def create_product(new_product: Product) -> Product:
    if any(product.id == new_product.id for product in products):
        raise HTTPException(status_code=409, detail="Product already exists")
    products.append(new_product)
    return new_product


@app.get("/products/{product_id}", response_model=Product)
def read_product(product_id: int) -> Product:
    product = next((product for product in products if product.id == product_id), None)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.put("/products/{product_id}", response_model=Product, status_code=201)
def update_product(product_id: int, updated_product: BaseProduct) -> Product:
    product_index = find_product_index(product_id)
    updated_product_with_id = Product(id=product_id, name=updated_product.name, price=updated_product.price)
    products[product_index] = updated_product_with_id
    return updated_product_with_id


def find_product_index(product_id: int) -> int:
    product_index = next((index for index, product in enumerate(products) if product.id == product_id), None)
    if product_index is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product_index


@app.delete("/products/{product_id}", response_model=Product)
def delete_product(product_id: int) -> Product:
    product_index = find_product_index(product_id)
    return products.pop(product_index)
