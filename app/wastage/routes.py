from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud  # Module where CRUD operations are defined
from .. import schemas  # Module containing data models
from ..database import get_db  # Dependency for database session

# Create an APIRouter instance for wastage condition-related routes
router = APIRouter(
    prefix="/wastage_conditions",  # Prefix for all routes in this router
    tags=["wastage_conditions"],  # Tagging endpoints for API documentation
)

# Create a new wastage condition
@router.post("/", response_model=schemas.WastageCondition)
def create_wastage_condition(wastage_condition: schemas.WastageConditionCreate, db: Session = Depends(get_db)):
    return crud.create_wastage_condition(db=db, wastage=wastage_condition)

# Get all wastage conditions with pagination
@router.get("/", response_model=list[schemas.WastageCondition])
def get_wastage_conditions(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_wastage_conditions(db=db, skip=skip, limit=limit)

# Get a wastage condition by ID
@router.get("/get_wastage_factor_by_id", response_model=schemas.WastageCondition)
def get_wastage_condition(wastage_factor_id: int, db: Session = Depends(get_db)):
    db_condition = crud.get_wastage_condition_by_id(db=db, wastage_factor_id=wastage_factor_id)
    if db_condition is None:
        raise HTTPException(status_code=404, detail="Wastage condition not found")
    return db_condition

# Update wastage condition by ID
@router.put("/update_wastage_factor_by_id", response_model=schemas.WastageCondition)
def update_wastage_condition(
    wastage_factor_id: int, 
    category: str, 
    wastage_condition: str,
    db: Session = Depends(get_db)
):
    db_condition = crud.update_wastage_condition(
        db=db, 
        wastage_factor_id=wastage_factor_id, 
        category=category,
        wastage_condition=wastage_condition
    )
    if db_condition is None:
        raise HTTPException(status_code=404, detail="Wastage condition not found")
    return db_condition

# Delete wastage condition by ID
@router.delete("/delete_wastage_factor_by_id", response_model=schemas.WastageCondition)
def delete_wastage_condition(wastage_factor_id: int, db: Session = Depends(get_db)):
    db_condition = crud.delete_wastage_condition(db=db, wastage_factor_id=wastage_factor_id)
    if db_condition is None:
        raise HTTPException(status_code=404, detail="Wastage condition not found")
    return db_condition
