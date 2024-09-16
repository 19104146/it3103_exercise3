from typing import List, Optional

from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from pydantic import BaseModel

app = FastAPI()


class Product(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float


products: List[Product] = []


@app.get("/products", response_model=List[Product])
def list_products():
    return products


@app.post("/products", response_model=int, status_code=201)
def create_product(product: Product):
    if any(p.id == product.id for p in products):
        raise HTTPException(status_code=400, detail="Product with this ID already exists")
    products.append(product)
    return product.id


@app.get("/products/{product_id}", response_model=Product)
def read_product(product_id: int):
    product = next((p for p in products if p.id == product_id), None)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.put("/products/{product_id}", response_model=Product, status_code=201)
def update_product(product_id: int, product: Product):
    index = next((i for i, p in enumerate(products) if p.id == product_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Product not found")
    products[index] = product
    return products[index]


@app.delete("/products/{product_id}", response_model=Product)
def delete_product(product_id: int):
    index = next((i for i, p in enumerate(products) if p.id == product_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return products.pop(index)
