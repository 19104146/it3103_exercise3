from fastapi import Body, FastAPI, HTTPException, Path, status
from typing_extensions import List

from database import next_id, products
from helpers import get_product
from models import ProductRead, ProductWrite

app = FastAPI()


@app.get("/products", response_model=List[ProductRead])
def list_products() -> List[ProductRead]:
    return products


@app.post(
    "/products",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
)
def create_product(product: ProductWrite = Body(...)) -> ProductRead:
    global next_id
    new_product = ProductRead(id=next_id, **product.dict())
    products.append(new_product)
    next_id += 1
    return new_product


@app.get("/products/{product_id}", response_model=ProductRead)
def read_product(product_id: int = Path(..., gt=0)) -> ProductRead:
    if product := get_product(product_id):
        return product
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Product not found",
    )


@app.put(
    "/products/{product_id}",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
)
def update_product(
    product_id: int = Path(..., gt=0),
    product: ProductWrite = Body(...),
):
    if existing_product := get_product(product_id):
        updated_product = existing_product.copy(update=product.dict())
        index = products.index(existing_product)
        products[index] = updated_product
        return updated_product
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Product not found",
    )


@app.delete("/products/{product_id}", response_model=ProductRead)
def delete_product(product_id: int = Path(..., gt=0)):
    if product := get_product(product_id):
        products.remove(product)
        return product
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Product not found",
    )
