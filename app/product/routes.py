from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud
from .. import schemas
from ..database import get_db
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create an APIRouter instance for product-related routes
router = APIRouter(
    prefix="/products",  # all routes in this router will be prefixed with /products
    tags=["products"],  # Tagging the endpoints for grouping in the docs
)

# Create a new product
@router.post("/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    """
    Create a new product.

    Args:
        product (schemas.ProductCreate): The product data to be created.
        db (Session): The database session.

    Returns:
        schemas.Product: The created product object.
    """
    try:
        created_product = crud.create_product(db=db, product=product)
        logger.info("Successfully created a new product with ID: %s", created_product.product_id)
        return created_product
    except Exception as e:
        logger.error("Error occurred while creating product: %s", e)
        raise

# Get all products
@router.get("/", response_model=list[schemas.Product])
def get_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Retrieve all products from the database with pagination.

    Args:
        skip (int): The number of products to skip.
        limit (int): The number of products to retrieve.
        db (Session): The database session.

    Returns:
        List[schemas.Product]: A list of product objects.
    """
    try:
        products = crud.get_products(db=db, skip=skip, limit=limit)
        logger.info("Retrieved %d products from the database.", len(products))
        return products
    except Exception as e:
        logger.error("Error occurred while fetching products: %s", e)
        raise

# Get a product by ID
@router.get("/get_product_by_category", response_model=schemas.Product)
def get_product(product_id: str, db: Session = Depends(get_db)):
    """
    Retrieve a product by its ID.

    Args:
        product_id (str): The ID of the product to retrieve.
        db (Session): The database session.

    Returns:
        schemas.Product: The product object if found.
    """
    try:
        db_product = crud.get_product_by_id(db=db, product_id=product_id)
        if db_product is None:
            logger.warning("Product not found with ID: %s", product_id)
            raise HTTPException(status_code=404, detail="Product not found")
        logger.info("Retrieved product with ID: %s", product_id)
        return db_product
    except Exception as e:
        logger.error("Error occurred while fetching product by ID: %s", e)
        raise

# Update product by ID
@router.put("/update_product_by_category", response_model=schemas.Product)
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
    """
    Update an existing product by its ID.

    Args:
        product_id (str): The ID of the product to update.
        description (str): The new description.
        unit (str): The new unit.
        category (str): The new category.
        unit_price (float): The new unit price.
        supplier (str): The new supplier.
        colour (str): The new colour.
        db (Session): The database session.

    Returns:
        schemas.Product: The updated product object if successful.
    """
    try:
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
            logger.warning("Product not found with ID: %s", product_id)
            raise HTTPException(status_code=404, detail="Product not found")
        logger.info("Updated product with ID: %s", product_id)
        return db_product
    except Exception as e:
        logger.error("Error occurred while updating product by ID: %s", e)
        raise

# Delete product by ID
@router.delete("/delete_product_by_category", response_model=schemas.Product)
def delete_product(product_id: str, db: Session = Depends(get_db)):
    """
    Delete a product by its ID from the database.

    Args:
        product_id (str): The ID of the product to delete.
        db (Session): The database session.

    Returns:
        schemas.Product: The deleted product object if successful.
    """
    try:
        db_product = crud.delete_product(db=db, product_id=product_id)
        if db_product is None:
            logger.warning("Product not found with ID: %s", product_id)
            raise HTTPException(status_code=404, detail="Product not found")
        logger.info("Deleted product with ID: %s", product_id)
        return db_product
    except Exception as e:
        logger.error("Error occurred while deleting product by ID: %s", e)
        raise
