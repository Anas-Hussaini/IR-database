from sqlalchemy.orm import Session
from ..models import Supplier
from ..schemas import SupplierCreate

# Create a new supplier
def create_supplier(db: Session, supplier: SupplierCreate):
    db_supplier = Supplier(
        supplier_id=supplier.supplier_id,
        name=supplier.name,
        warehouse=supplier.warehouse,
        contact_number=supplier.contact_number,
        po_box=supplier.po_box,
        vendor_address=supplier.vendor_address
    )
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier

# Get all suppliers
def get_suppliers(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Supplier).offset(skip).limit(limit).all()

# Get supplier by ID
def get_supplier_by_id(db: Session, supplier_id: str):
    return db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()

# Update supplier by ID
def update_supplier(db: Session, supplier_id:str, name: str, warehouse: str, contact_number: str, po_box: str, vendor_address: str):
    db_supplier = db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()
    if db_supplier:
        db_supplier.name=name
        db_supplier.warehouse=warehouse
        db_supplier.contact_number=contact_number
        db_supplier.po_box=po_box
        db_supplier.vendor_address=vendor_address
        db.commit()
        db.refresh(db_supplier)
    return db_supplier

# Delete supplier by ID
def delete_supplier(db: Session, supplier_id: str):
    db_supplier = db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()
    if db_supplier:
        db.delete(db_supplier)
        db.commit()
    return db_supplier





