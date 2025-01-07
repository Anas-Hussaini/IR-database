from sqlalchemy.orm import Session
from ..models import Product
from ..schemas import ProductCreate

# Create a new product
def create_product(db: Session, product: ProductCreate):
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
    return db_product

# Get all products
def get_products(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Product).offset(skip).limit(limit).all()

# Get product by ID
def get_product_by_id(db: Session, product_id: str):
    return db.query(Product).filter(Product.product_id == product_id).first()

# Update product by ID
def update_product(db: Session, product_id: str, description: str, unit: str, category: str, unit_price: float, supplier: str, colour: str):
    db_product = db.query(Product).filter(Product.product_id == product_id).first()
    if db_product:
        db_product.description=description
        db_product.unit=unit
        db_product.category=category
        db_product.unit_price=unit_price
        db_product.supplier=supplier
        db_product.colour=colour
        db.commit()
        db.refresh(db_product)
    return db_product

# Delete product by ID
def delete_product(db: Session, product_id: str):
    db_product = db.query(Product).filter(Product.product_id == product_id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
    return db_product
