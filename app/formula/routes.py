from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud
from .. import schemas
from ..database import get_db

# Create an APIRouter instance for formula-related routes
router = APIRouter(
    prefix="/formulae",  # all routes in this router will be prefixed with /formulas
    tags=["formulae"],  # Tagging the endpoints for grouping in the docs
)

# Create a new formula
@router.post("/", response_model=schemas.Formula)
def create_formula(formula: schemas.FormulaCreate, db: Session = Depends(get_db)):
    return crud.create_formula(db=db, formula=formula)

# Get all formulas
@router.get("/", response_model=list[schemas.Formula])
def get_formulas(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_formulas(db=db, skip=skip, limit=limit)

# Get a formula by category
@router.get("/{category}", response_model=schemas.Formula)
def get_formula(category: str, db: Session = Depends(get_db)):
    db_formula = crud.get_formula_by_category(db=db, category=category)
    if db_formula is None:
        raise HTTPException(status_code=404, detail="Formula not found")
    return db_formula

# Update formula by category
@router.put("/{category}", response_model=schemas.Formula)
def update_formula(category: str, equation: str, wastage_factor: float, db: Session = Depends(get_db)):
    db_formula = crud.update_formula(db=db, category=category, equation=equation, wastage_factor=wastage_factor)
    if db_formula is None:
        raise HTTPException(status_code=404, detail="Formula not found")
    return db_formula

# Delete formula by category
@router.delete("/{category}", response_model=schemas.Formula)
def delete_formula(category: str, db: Session = Depends(get_db)):
    db_formula = crud.delete_formula(db=db, category=category)
    if db_formula is None:
        raise HTTPException(status_code=404, detail="Formula not found")
    return db_formula
