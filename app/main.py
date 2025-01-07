import logging
from fastapi import FastAPI

# from .invoice import routes as invoice_routes
from .product import routes as product_routes
from .supplier import routes as supplier_routes
from .formula import routes as formula_routes
from .wastage import routes as wastage_condition_routes

from .database import engine
from .models import Base


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Create all tables in the database
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")

app = FastAPI(
    title="Manage Database",
    description="Manage Database docs",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"Database_Management": "Insured_Roofs"}

# app.include_router(invoice_routes.router, prefix="/api", tags=["invoice"])
app.include_router(product_routes.router, prefix="/api", tags=["products"])
app.include_router(supplier_routes.router, prefix="/api", tags=["suppliers"])
app.include_router(formula_routes.router, prefix="/api", tags=["formulae"])
app.include_router(wastage_condition_routes.router, prefix="/api", tags=["wastage_conditions"])


@app.on_event("startup")
async def startup_event():
    logger.info("Application is starting up on port 8000")

