import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Product, Supplier, Formula, WastageCondition  # Import your models

load_dotenv()

# Database credentials
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_USER = os.getenv("DB_USER")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")

# SQLAlchemy Database URL
SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"

# Create SQLAlchemy engine and session
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Column definitions for each table
TABLE_COLUMNS = {
    "products": [
        "product_id", "description", "unit", "category", "unit_price", "supplier", "colour"
    ],
    "suppliers": [
        "supplier_id", "name", "warehouse", "contact_number", "po_box", "vendor_address"
    ],
    "formulae": [
        "category", "equation", "wastage_factor"
    ],
    "wastage_conditions": [
        "wastage_factor_id", "category", "wastage_condition", "wastage_factor"
    ]
}

def load_csv(file_path, table_name):
    """
    Load CSV data and assign appropriate column names if missing.
    """
    columns = TABLE_COLUMNS[table_name]
    df = pd.read_csv(file_path, header=None)
    df.columns = columns
    return df

def insert_data(session, table_name, df):
    """
    Insert data into the database using SQLAlchemy ORM.
    """
    if table_name == "products":
        products = [
            Product(
                product_id=row["product_id"],
                description=row["description"],
                unit=row["unit"],
                category=row["category"],
                unit_price=row["unit_price"],
                supplier=row["supplier"],
                colour=row["colour"]
            ) for index, row in df.iterrows()
        ]
        session.add_all(products)

    elif table_name == "suppliers":
        suppliers = [
            Supplier(
                supplier_id=row["supplier_id"],
                name=row["name"],
                warehouse=row["warehouse"],
                contact_number=row["contact_number"],
                po_box=row["po_box"],
                vendor_address=row["vendor_address"]
            ) for index, row in df.iterrows()
        ]
        session.add_all(suppliers)

    elif table_name == "formulae":
        formulae = [
            Formula(
                category=row["category"],
                equation=row["equation"],
                wastage_factor=row["wastage_factor"]
            ) for index, row in df.iterrows()
        ]
        session.add_all(formulae)

    elif table_name == "wastage_conditions":
        wastage_conditions = [
            WastageCondition(
                category=row["category"],
                wastage_condition=row["wastage_condition"],
                wastage_factor=row["wastage_factor"]
            ) for index, row in df.iterrows()
        ]
        session.add_all(wastage_conditions)

    session.commit()

def main():
    # CSV file to table mapping
    csv_files = {
        "suppliers": "data/Suppliers_Database-Sheet1.csv",
        "formulae": "data/Formulae_Database-Sheet1.csv",
        "products": "data/Product_Database-Sheet1.csv",
        "wastage_conditions": "data/Wastage_Factors_Database-Sheet1.csv"
    }

    # Create a new session
    session = SessionLocal()

    try:
        for table_name, file_path in csv_files.items():
            print(f"Processing {file_path} into {table_name}...")
            df = load_csv(file_path, table_name)
            insert_data(session, table_name, df)
            print(f"Data from {file_path} inserted into {table_name}.")

    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    main()
