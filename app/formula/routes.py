from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud
from .. import schemas
from ..database import get_db
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create an APIRouter instance for formula-related routes
router = APIRouter(
    prefix="/formulae",  # all routes in this router will be prefixed with /formulas
    tags=["formulae"],  # Tagging the endpoints for grouping in the docs
)

# Create a new formula
@router.post("/", response_model=schemas.Formula)
def create_formula(formula: schemas.FormulaCreate, db: Session = Depends(get_db)):
    """
    Endpoint to create a new formula.

    Parameters:
        formula (schemas.FormulaCreate): The formula data to be created.
        db (Session): The SQLAlchemy session object.

    Returns:
        Formula: The newly created formula object.
    """
    logger.info("Creating new formula with category: %s", formula.category)
    new_formula = crud.create_formula(db=db, formula=formula)
    return new_formula

# Get all formulas
@router.get("/", response_model=list[schemas.Formula])
def get_formulas(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Endpoint to retrieve all formulas with pagination.

    Parameters:
        skip (int): The number of formulas to skip.
        limit (int): The number of formulas to retrieve.
        db (Session): The SQLAlchemy session object.

    Returns:
        List[Formula]: A list of formula objects.
    """
    logger.info("Fetching formulas with skip: %d, limit: %d", skip, limit)
    formulas = crud.get_formulas(db=db, skip=skip, limit=limit)
    return formulas

# Get a formula by category
@router.get("/{category}", response_model=schemas.Formula)
def get_formula(category: str, db: Session = Depends(get_db)):
    """
    Endpoint to retrieve a formula by its category.

    Parameters:
        category (str): The category of the formula to retrieve.
        db (Session): The SQLAlchemy session object.

    Returns:
        Formula: The formula object if found, otherwise raises HTTPException.
    """
    logger.info("Fetching formula with category: %s", category)
    db_formula = crud.get_formula_by_category(db=db, category=category)
    if db_formula is None:
        logger.warning("Formula not found for category: %s", category)
        raise HTTPException(status_code=404, detail="Formula not found")
    return db_formula

# Update formula by category
@router.put("/{category}", response_model=schemas.Formula)
def update_formula(category: str, equation: str, wastage_factor: float, db: Session = Depends(get_db)):
    """
    Endpoint to update a formula by its category.

    Parameters:
        category (str): The category of the formula to update.
        equation (str): The new equation value.
        wastage_factor (float): The new wastage factor value.
        db (Session): The SQLAlchemy session object.

    Returns:
        Formula: The updated formula object if successful, otherwise raises HTTPException.
    """
    logger.info("Updating formula with category: %s", category)
    db_formula = crud.update_formula(db=db, category=category, equation=equation, wastage_factor=wastage_factor)
    if db_formula is None:
        logger.warning("Formula not found for update with category: %s", category)
        raise HTTPException(status_code=404, detail="Formula not found")
    return db_formula

# Delete formula by category
@router.delete("/{category}", response_model=schemas.Formula)
def delete_formula(category: str, db: Session = Depends(get_db)):
    """
    Endpoint to delete a formula by its category.

    Parameters:
        category (str): The category of the formula to delete.
        db (Session): The SQLAlchemy session object.

    Returns:
        Formula: The deleted formula object if successful, otherwise raises HTTPException.
    """
    logger.info("Deleting formula with category: %s", category)
    db_formula = crud.delete_formula(db=db, category=category)
    if db_formula is None:
        logger.warning("Formula not found for deletion with category: %s", category)
        raise HTTPException(status_code=404, detail="Formula not found")
    return db_formula
