import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()

DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_USER = os.getenv("DB_USER")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")

# Database configuration
DB_CONFIG = {
    "dbname": DB_NAME,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "host": DB_HOST,
    "port": 5432
}

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

def create_table(cursor, table_name, columns):
    """
    Create a table in the database if it doesn't exist.
    """
    # Define column types based on the model
    column_definitions = {
        "product_id": "TEXT",
        "description": "TEXT",
        "unit": "TEXT",
        "category": "TEXT",
        "unit_price": "FLOAT",
        "supplier": "TEXT",
        "colour": "TEXT",
        "supplier_id": "TEXT",
        "name": "TEXT",
        "warehouse": "TEXT",
        "contact_number": "TEXT",
        "po_box": "TEXT",
        "vendor_address": "TEXT",
        "equation": "TEXT",
        "wastage_factor": "FLOAT",
        "wastage_factor_id": "SERIAL PRIMARY KEY",
        "wastage_condition": "TEXT"
    }

    columns_def = ", ".join([f"{col} {column_definitions[col]}" for col in columns])
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        {columns_def}
    );
    """
    cursor.execute(create_table_query)

def insert_data(cursor, table_name, df, columns):
    """
    Insert data into the table while handling foreign key relationships.
    """
    # Filter the DataFrame to match the table's columns
    df = df[columns]

    # Handle foreign key references for 'products' and 'wastage_conditions'
    if table_name == "products":
        # Ensure that the category and supplier exist in their respective tables
        for _, row in df.iterrows():
            # Check if category exists in formulae table
            category_exists_query = "SELECT 1 FROM formulae WHERE category = %s"
            cursor.execute(category_exists_query, (row['category'],))
            if cursor.fetchone() is None:
                # Insert the category into formulae if it does not exist
                insert_category_query = """
                    INSERT INTO formulae (category, equation, wastage_factor) 
                    VALUES (%s, %s, %s)
                """
                cursor.execute(insert_category_query, (row['category'], "default_equation", 1.0))  # Use default values if needed

            # Check if supplier exists in suppliers table
            supplier_exists_query = "SELECT 1 FROM suppliers WHERE supplier_id = %s"
            cursor.execute(supplier_exists_query, (row['supplier'],))
            if cursor.fetchone() is None:
                # Insert the supplier if it does not exist
                insert_supplier_query = """
                    INSERT INTO suppliers (supplier_id, name, warehouse, contact_number, po_box, vendor_address) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_supplier_query, (row['supplier'], "default_name", "default_warehouse", "default_contact", "default_po_box", "default_vendor_address"))

    elif table_name == "wastage_conditions":
        # Ensure that category exists in formulae table for wastage_conditions
        for _, row in df.iterrows():
            category_exists_query = "SELECT 1 FROM formulae WHERE category = %s"
            cursor.execute(category_exists_query, (row['category'],))
            if cursor.fetchone() is None:
                # Insert the category into formulae if it does not exist
                insert_category_query = """
                    INSERT INTO formulae (category, equation, wastage_factor) 
                    VALUES (%s, %s, %s)
                """
                cursor.execute(insert_category_query, (row['category'], "default_equation", 1.0))  # Use default values if needed

    # Convert data to match database types where necessary
    if "unit_price" in columns:
        df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    if "wastage_factor" in columns:
        df["wastage_factor"] = pd.to_numeric(df["wastage_factor"], errors="coerce")

    # Create placeholders and columns
    columns_str = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(columns))

    # Prepare query
    insert_query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
    # Use execute_values for batch insertion
    data = [tuple(row) for row in df.to_numpy()]
    cursor.executemany(insert_query, data)


def load_csv(file_path, table_name):
    """
    Load CSV data and assign appropriate column names if missing.
    """
    # Use pre-defined column names for the table
    columns = TABLE_COLUMNS[table_name]

    # Load CSV data without headers and assign column names
    df = pd.read_csv(file_path, header=None)
    df.columns = columns

    return df


def main():
    # CSV file to table mapping
    csv_files = {
        "formulae": "data/Formulae_Database-Sheet1.csv",
        "suppliers": "data/Suppliers_Database-Sheet1.csv",
        "wastage_conditions": "data/Wastage_Factors_Database-Sheet1.csv",
        "products": "data/Product_Database-Sheet1.csv"
    }

    # Connect to PostgreSQL
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        for table_name, file_path in csv_files.items():
            print(f"Processing {file_path} into {table_name}...")

            # Load CSV data with correct column names
            df = load_csv(file_path, table_name)

            # Create table and insert data
            create_table(cursor, table_name, TABLE_COLUMNS[table_name])
            insert_data(cursor, table_name, df, TABLE_COLUMNS[table_name])

            print(f"Data from {file_path} inserted into {table_name}.")

        # Commit changes
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
