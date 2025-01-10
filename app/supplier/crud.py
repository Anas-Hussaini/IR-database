from sqlalchemy.orm import Session
from ..models import Supplier
from ..schemas import SupplierCreate
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a new supplier
def create_supplier(db: Session, supplier: SupplierCreate):
    """
    Create a new supplier in the database.

    Args:
        db (Session): The database session.
        supplier (SupplierCreate): The supplier data to be created.

    Returns:
        Supplier: The created supplier object.
    """
    try:
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
        logger.info("Successfully created a new supplier with ID: %s", db_supplier.supplier_id)
        return db_supplier
    except Exception as e:
        logger.error("Error occurred while creating supplier: %s", e)
        raise

# Get all suppliers
def get_suppliers(db: Session, skip: int = 0, limit: int = 10):
    """
    Retrieve all suppliers from the database with pagination.

    Args:
        db (Session): The database session.
        skip (int): The number of suppliers to skip.
        limit (int): The number of suppliers to retrieve.

    Returns:
        List[Supplier]: A list of supplier objects.
    """
    try:
        suppliers = db.query(Supplier).offset(skip).limit(limit).all()
        logger.info("Retrieved %d suppliers from the database.", len(suppliers))
        return suppliers
    except Exception as e:
        logger.error("Error occurred while fetching suppliers: %s", e)
        raise

# Get supplier by ID
def get_supplier_by_id(db: Session, supplier_id: str):
    """
    Retrieve a supplier by its ID.

    Args:
        db (Session): The database session.
        supplier_id (str): The ID of the supplier to retrieve.

    Returns:
        Supplier: The supplier object if found.
    """
    try:
        db_supplier = db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()
        if db_supplier is None:
            logger.warning("Supplier not found with ID: %s", supplier_id)
            return None
        logger.info("Retrieved supplier with ID: %s", supplier_id)
        return db_supplier
    except Exception as e:
        logger.error("Error occurred while fetching supplier by ID: %s", e)
        raise

# Update supplier by ID
def update_supplier(db: Session, supplier_id:str, name: str, warehouse: str, contact_number: str, po_box: str, vendor_address: str):
    """
    Update an existing supplier by its ID.

    Args:
        db (Session): The database session.
        supplier_id (str): The ID of the supplier to update.
        name (str): The new name.
        warehouse (str): The new warehouse.
        contact_number (str): The new contact number.
        po_box (str): The new PO box.
        vendor_address (str): The new vendor address.

    Returns:
        Supplier: The updated supplier object if successful.
    """
    try:
        db_supplier = db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()
        if db_supplier:
            db_supplier.name = name
            db_supplier.warehouse = warehouse
            db_supplier.contact_number = contact_number
            db_supplier.po_box = po_box
            db_supplier.vendor_address = vendor_address
            db.commit()
            db.refresh(db_supplier)
            logger.info("Updated supplier with ID: %s", supplier_id)
            return db_supplier
        else:
            logger.warning("Supplier not found with ID: %s", supplier_id)
            return None
    except Exception as e:
        logger.error("Error occurred while updating supplier by ID: %s", e)
        raise

# Delete supplier by ID
def delete_supplier(db: Session, supplier_id: str):
    """
    Delete a supplier by its ID from the database.

    Args:
        db (Session): The database session.
        supplier_id (str): The ID of the supplier to delete.

    Returns:
        Supplier: The deleted supplier object if successful.
    """
    try:
        db_supplier = db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()
        if db_supplier:
            db.delete(db_supplier)
            db.commit()
            logger.info("Deleted supplier with ID: %s", supplier_id)
            return db_supplier
        else:
            logger.warning("Supplier not found with ID: %s", supplier_id)
            return None
    except Exception as e:
        logger.error("Error occurred while deleting supplier by ID: %s", e)
        raise
