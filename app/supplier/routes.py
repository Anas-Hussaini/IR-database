from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud
from .. import schemas
from ..database import get_db

# Create an APIRouter instance for supplier-related routes
router = APIRouter(
    prefix="/suppliers",  # all routes in this router will be prefixed with /suppliers
    tags=["suppliers"],  # Tagging the endpoints for grouping in the docs
)

# Create a new supplier
@router.post("/", response_model=schemas.Supplier)
def create_supplier(supplier: schemas.SupplierCreate, db: Session = Depends(get_db)):
    return crud.create_supplier(db=db, supplier=supplier)

# Get all suppliers
@router.get("/", response_model=list[schemas.Supplier])
def get_suppliers(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_suppliers(db=db, skip=skip, limit=limit)

# Get a supplier by ID
@router.get("/{supplier_id}", response_model=schemas.Supplier)
def get_supplier(supplier_id: str, db: Session = Depends(get_db)):
    db_supplier = crud.get_supplier_by_id(db=db, supplier_id=supplier_id)
    if db_supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return db_supplier

# Update supplier by ID
@router.put("/{supplier_id}", response_model=schemas.Supplier)
def update_supplier(supplier_id: str, name: str, warehouse: str, contact_number: str, po_box: str, vendor_address: str, db: Session = Depends(get_db)):
    db_supplier = crud.update_supplier(db=db, supplier_id=supplier_id, name=name, warehouse=warehouse, contact_number=contact_number, po_box=po_box, vendor_address=vendor_address)
    if db_supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return db_supplier

# Delete supplier by ID
@router.delete("/{supplier_id}", response_model=schemas.Supplier)
def delete_supplier(supplier_id: str, db: Session = Depends(get_db)):
    db_supplier = crud.delete_supplier(db=db, supplier_id=supplier_id)
    if db_supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return db_supplier
