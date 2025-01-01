import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
from config import dotenv_path
from .crud import connect_to_db, execute_query

# Load environment variables
load_dotenv(dotenv_path=dotenv_path, override=True)
DB_PASSWORD = os.environ["DB_PASSWORD"]

# Configure logging
LOG_FILE = "database.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)

# FastAPI instance
app = FastAPI()

# Models
class TableSchema(BaseModel):
    db_name: str
    table_name: str
    columns: dict
    primary_key: str = None

class ProductQuery(BaseModel):
    db_name: str
    table_name: str
    product_id: str

class DatabaseName(BaseModel):
    db_name: str

@app.get("/")
async def root():
    """Root endpoint to check API status."""
    logging.info("DATABASE Root endpoint accessed")
    return {"message": "FAST API Insured Roofs DATABASE trial", "data": 2024}

@app.post("/create-database/")
def create_database(db_name: str):
    """Create a new database."""
    conn = connect_to_db()
    try:
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        execute_query(conn, f"CREATE DATABASE {db_name};")
        return {"message": f"Database '{db_name}' created successfully."}
    finally:
        conn.close()

@app.get("/list-databases/")
def list_databases():
    """List all databases."""
    conn = connect_to_db()
    try:
        query = "SELECT datname FROM pg_database WHERE datistemplate = false;"
        databases = execute_query(conn, query, fetch=True)
        return {"databases": [db[0] for db in databases]}
    finally:
        conn.close()

@app.post("/create-table/")
def create_table(schema: TableSchema):
    """Create a table in the specified database."""
    conn = connect_to_db(schema.db_name)
    try:
        columns_definition = ", ".join([f"{col} {dtype}" for col, dtype in schema.columns.items()])
        if schema.primary_key:
            columns_definition += f", PRIMARY KEY ({schema.primary_key})"
        query = f"CREATE TABLE {schema.table_name} ({columns_definition});"
        execute_query(conn, query)
        return {"message": f"Table '{schema.table_name}' created successfully."}
    finally:
        conn.close()

@app.post("/list-tables/")
def list_tables(schema: DatabaseName):
    """List tables and their columns in a database."""
    conn = connect_to_db(schema.db_name)
    try:
        query = """
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position;
        """
        result = execute_query(conn, query, fetch=True)
        tables = {}
        for table_name, column_name, data_type in result:
            tables.setdefault(table_name, []).append({"column_name": column_name, "data_type": data_type})
        return {"tables": tables}
    finally:
        conn.close()

@app.post("/insert-row-in-table/")
def insert_data(schema: TableSchema, data: dict):
    """Insert a row into a specified table."""
    conn = connect_to_db(schema.db_name)
    try:
        columns = ", ".join(data.keys())
        values = ", ".join([f"%s" for _ in data.values()])
        query = f"INSERT INTO {schema.table_name} ({columns}) VALUES ({values});"
        execute_query(conn, query, params=tuple(data.values()))
        return {"message": f"Data inserted successfully into '{schema.table_name}'."}
    finally:
        conn.close()

@app.delete("/delete-row-in-table/")
def delete_row(db_name: str, table_name: str, product_id: str):
    """Delete a row from a table."""
    conn = connect_to_db(db_name)
    try:
        query = f"DELETE FROM {table_name} WHERE product_id = %s;"
        execute_query(conn, query, params=(product_id,))
        return {"message": f"Row with product_id = {product_id} deleted successfully."}
    finally:
        conn.close()

@app.post("/fetch-product/")
def fetch_product(query: ProductQuery):
    """Fetch a product by ID."""
    conn = connect_to_db(query.db_name)
    try:
        sql_query = f"SELECT * FROM {query.table_name} WHERE product_id = %s;"
        rows = execute_query(conn, sql_query, params=(query.product_id,), fetch=True)
        if not rows:
            raise HTTPException(status_code=404, detail=f"Product with ID {query.product_id} not found.")
        column_names = [desc[0] for desc in conn.cursor().description]
        return {"product": dict(zip(column_names, rows[0]))}
    finally:
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="127.0.0.1", 
        port=8000,
        # reload=True
    )




### Usage Table Creation with localhost/docs ###
# {
#     "db_name": "insured_roofs_database",
#     "table_name": "products",
#     "columns": {
#         "product_id": "text",
#         "description": "text",
#         "unit": "text",
#         "category": "text",
#         "unit_price": "numeric",
#         "supplier": "text",
#         "colour": "text"
#     },
#     "primary_key": "product_id"
# }



### Usage Table Data Insert with localhost/docs ###
# {
#   "schema": {
#     "db_name": "insured_roofs_database",
#     "table_name": "products1",
#     "columns": {
#         "product_id": "text",
#         "description": "text",
#         "unit": "text",
#         "category": "text",
#         "unit_price": "numeric",
#         "supplier": "text",
#         "colour": "text"
#     },
#     "primary_key": "product_id"
#   },
#   "data": {
#         "product_id": "GAFSARMOCHKHHKDA",
#         "description": "GAF MO SEAL-A-RIDGE CHARCOAL MOBILE PLASTIC WRAPPER 25LF/BDL",
#         "unit": "BDL",
#         "category": "Caps",
#         "unit_price": "61.6000",
#         "supplier": "BEACON BUILDING PRODUCTS",
#         "colour": "Charcoal"
#   }
# }