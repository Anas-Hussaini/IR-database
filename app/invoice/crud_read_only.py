from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..config import DATABASE_URL
from ..models import Product, Supplier, Formula

# Database configuration
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def fetch_product(product_id, supplier, colour):
    try:
        return session.query(Product).filter(
            Product.product_id == product_id,
            Product.supplier == supplier,
            Product.colour == colour
        ).first()
    except Exception as e:
        print(f"Error fetching product: {e}")
        return None

def fetch_supplier(name):
    try:
        return session.query(Supplier).filter(Supplier.name == name).first()
    except Exception as e:
        print(f"Error fetching supplier: {e}")
        return None

def fetch_formula(category):
    try:
        return session.query(Formula).filter(Formula.category == category).first()
    except Exception as e:
        print(f"Error fetching formula: {e}")
        return None

def fetch_all_categories():
    try:
        return [row.category for row in session.query(Formula).all()]
    except Exception as e:
        print(f"Error fetching categories: {e}")
        return []

# Example usage
# product_id = "GAFSARMOHI"
# supplier = "BEACON BUILDING PRODUCTS"
# colour = "Hickory"
# product = fetch_product(product_id, supplier, colour)
# if product:
#     print(f"Product ID: {product.product_id}, Supplier: {product.supplier}, Colour: {product.colour}, Category: {product.category}")
#     formula = fetch_formula(category=product.category).equation
#     print(formula)
#     supplier_info = fetch_supplier(product.supplier)
#     if supplier_info:
#         print(f"Supplier ID: {supplier_info.supplier_id}, Name: {supplier_info.name}, Contact: {supplier_info.contact_number}")
#     else:
#         print("No matching supplier found.")
# else:
#     print("No matching product found.")
