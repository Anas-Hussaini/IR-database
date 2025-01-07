from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud
from .. import schemas
from ..database import get_db

# Create an APIRouter instance for product-related routes
router = APIRouter(
    prefix="/products",  # all routes in this router will be prefixed with /products
    tags=["products"],  # Tagging the endpoints for grouping in the docs
)

# Create a new product
@router.post("/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    return crud.create_product(db=db, product=product)

# Get all products
@router.get("/", response_model=list[schemas.Product])
def get_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_products(db=db, skip=skip, limit=limit)

# Get a product by ID
@router.get("/{product_id}", response_model=schemas.Product)
def get_product(product_id: str, db: Session = Depends(get_db)):
    db_product = crud.get_product_by_id(db=db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

# Update product by ID
@router.put("/{product_id}", response_model=schemas.Product)
def update_product(
    product_id: str,
    description: str,
    unit: str,
    category: str,
    unit_price: float, 
    supplier: str, 
    colour: str, 
    db: Session = Depends(get_db)
):
    db_product = crud.update_product(
        db=db, 
        product_id=product_id, 
        description=description, 
        unit=unit, 
        category=category, 
        unit_price=unit_price, 
        supplier=supplier, 
        colour=colour
    )
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

# Delete product by ID
@router.delete("/{product_id}", response_model=schemas.Product)
def delete_product(product_id: str, db: Session = Depends(get_db)):
    db_product = crud.delete_product(db=db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product