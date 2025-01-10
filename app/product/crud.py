from sqlalchemy.orm import Session
from ..models import Product
from ..schemas import ProductCreate
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a new product
def create_product(db: Session, product: ProductCreate):
    """
    Creates a new product in the database.

    Parameters:
        db (Session): The SQLAlchemy session object.
        product (ProductCreate): The product data to be created.

    Returns:
        Product: The newly created product object.
    """
    try:
        db_product = Product(
            product_id=product.product_id,
            description=product.description,
            unit=product.unit,
            category=product.category,
            unit_price=product.unit_price,
            supplier=product.supplier,
            colour=product.colour
        )
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        logger.info("Successfully created a new product with ID: %s", product.product_id)
        return db_product
    except Exception as e:
        logger.error("Error occurred while creating product: %s", e)
        db.rollback()
        raise

# Get all products
def get_products(db: Session, skip: int = 0, limit: int = 10):
    """
    Retrieves all products from the database with pagination.

    Parameters:
        db (Session): The SQLAlchemy session object.
        skip (int): The number of products to skip.
        limit (int): The number of products to retrieve.

    Returns:
        List[Product]: A list of product objects.
    """
    try:
        products = db.query(Product).offset(skip).limit(limit).all()
        logger.info("Retrieved %d products from the database.", len(products))
        return products
    except Exception as e:
        logger.error("Error occurred while fetching products: %s", e)
        raise

# Get product by ID
def get_product_by_id(db: Session, product_id: str):
    """
    Retrieves a product by its ID.

    Parameters:
        db (Session): The SQLAlchemy session object.
        product_id (str): The ID of the product to retrieve.

    Returns:
        Product or None: The product object if found, otherwise None.
    """
    try:
        product = db.query(Product).filter(Product.product_id == product_id).first()
        if product:
            logger.info("Retrieved product with ID: %s", product_id)
        else:
            logger.warning("No product found with ID: %s", product_id)
        return product
    except Exception as e:
        logger.error("Error occurred while fetching product by ID: %s", e)
        raise

# Get product by category, supplier, and colour
def get_product_by_category_supplier_colour(db: Session, category: str, supplier_id: int, colour: str):
    """
    Retrieves a product by its category, supplier, and colour.

    Parameters:
        db (Session): The SQLAlchemy session object.
        category (str): The category of the product to retrieve.
        supplier_id (int): The supplier ID of the product to retrieve.
        colour (str): The colour of the product to retrieve.

    Returns:
        Product or None: The product object if found, otherwise None.
    """
    try:
        product = (
            db.query(Product)
            .filter(
                Product.category == category,
                Product.supplier == supplier_id,
                Product.colour == colour
            )
            .first()
        )
        if product:
            logger.info("Retrieved product with category: %s, supplier_id: %d, colour: %s", category, supplier_id, colour)
        else:
            logger.warning("No product found with category: %s, supplier_id: %d, colour: %s", category, supplier_id, colour)
        return product
    except Exception as e:
        logger.error("Error occurred while fetching product by category, supplier, and colour: %s", e)
        raise

# Update product by ID
def update_product(db: Session, product_id: str, description: str, unit: str, category: str, unit_price: float, supplier: str, colour: str):
    """
    Updates an existing product by its ID.

    Parameters:
        db (Session): The SQLAlchemy session object.
        product_id (str): The ID of the product to update.
        description (str): The new description value.
        unit (str): The new unit value.
        category (str): The new category value.
        unit_price (float): The new unit price value.
        supplier (str): The new supplier value.
        colour (str): The new colour value.

    Returns:
        Product or None: The updated product object if successful, otherwise None.
    """
    try:
        db_product = db.query(Product).filter(Product.product_id == product_id).first()
        if db_product:
            db_product.description = description
            db_product.unit = unit
            db_product.category = category
            db_product.unit_price = unit_price
            db_product.supplier = supplier
            db_product.colour = colour
            db.commit()
            db.refresh(db_product)
            logger.info("Updated product with ID: %s", product_id)
        else:
            logger.warning("No product found with ID: %s", product_id)
        return db_product
    except Exception as e:
        logger.error("Error occurred while updating product by ID: %s", e)
        db.rollback()
        raise

# Delete product by ID
def delete_product(db: Session, product_id: str):
    """
    Deletes a product by its ID from the database.

    Parameters:
        db (Session): The SQLAlchemy session object.
        product_id (str): The ID of the product to delete.

    Returns:
        Product or None: The deleted product object if successful, otherwise None.
    """
    try:
        db_product = db.query(Product).filter(Product.product_id == product_id).first()
        if db_product:
            db.delete(db_product)
            db.commit()
            logger.info("Deleted product with ID: %s", product_id)
        else:
            logger.warning("No product found with ID: %s", product_id)
        return db_product
    except Exception as e:
        logger.error("Error occurred while deleting product by ID: %s", e)
        db.rollback()
        raise
