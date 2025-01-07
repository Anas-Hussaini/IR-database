from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from ..config import DATABASE_URL
from ..models import Product, Supplier, Formula

# Database configuration
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def fetch_product(product_id, supplier, colour):
    row = session.query(Product).filter(
        Product.product_id == product_id,
        Product.supplier == supplier,
        Product.colour == colour
    ).first()  # Use .all() for multiple rows
    return row

def fetch_supplier(name):
    row = session.query(Supplier).filter(
        Supplier.name == name
    ).first()  # Use .all() for multiple rows
    return row

def fetch_formula(category):
    row = session.query(Formula).filter(
        Formula.category == category
    ).first()  # Use .all() for multiple rows
    return row

def fetch_all_categories():
    categories=[]
    rows = session.query(Formula).all()
    for row in rows:
        categories.append(row.category)
    return categories



# # Example usage
# product_id = "GAFSARMOHI"
# supplier = "BEACON BUILDING PRODUCTS"
# colour = "Hickory"
# product = fetch_product(product_id, supplier, colour)
# if product:
#     print(f"Product ID: {product.product_id}, Supplier: {product.supplier}, Colour: {product.colour}, Category: {product.category}")
#     formula = fetch_formula(category=product.category).equation
#     print(formula)
#     supplier=fetch_supplier(product.supplier)
#     if supplier:
#         print(f"Supplier ID: {supplier.supplier_id}, Name: {supplier.name}, Contact: {supplier.contact_number}")
#     else:
#         print("No matching supplier found.")
# else:
#     print("No matching product found.")


