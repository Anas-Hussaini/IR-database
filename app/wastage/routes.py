from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud  
from .. import schemas  
from ..database import get_db 

# Create an APIRouter instance for wastage condition-related routes
router = APIRouter(
    prefix="/wastage_conditions",  # all routes in this router will be prefixed with /wastage-conditions
    tags=["wastage_conditions"],  # Tagging the endpoints for grouping in the docs
)

# Create a new wastage condition
@router.post("/", response_model=schemas.WastageCondition)
def create_wastage_condition(condition: schemas.WastageConditionCreate, db: Session = Depends(get_db)):
    return crud.create_wastage_condition(db=db, condition=condition)

# Get all wastage conditions
@router.get("/", response_model=list[schemas.WastageCondition])
def get_wastage_conditions(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_wastage_conditions(db=db, skip=skip, limit=limit)

# Get a wastage condition by ID
@router.get("/{wastage_factor_id}", response_model=schemas.WastageCondition)
def get_wastage_condition(wastage_factor_id: int, db: Session = Depends(get_db)):
    db_condition = crud.get_wastage_condition_by_id(db=db, wastage_factor_id=wastage_factor_id)
    if db_condition is None:
        raise HTTPException(status_code=404, detail="Wastage condition not found")
    return db_condition

# Update wastage condition by ID
@router.put("/{wastage_factor_id}", response_model=schemas.WastageCondition)
def update_wastage_condition(
    wastage_factor_id: int, 
    category: str, 
    wastage_condition: str,
    wastage_percentage: float, 
    db: Session = Depends(get_db)
):
    db_condition = crud.update_wastage_condition(
        db=db, 
        wastage_factor_id=wastage_factor_id, 
        category=category,
        wastage_condition=wastage_condition, 
        wastage_percentage=wastage_percentage
    )
    if db_condition is None:
        raise HTTPException(status_code=404, detail="Wastage condition not found")
    return db_condition

# Delete wastage condition by ID
@router.delete("/{wastage_factor_id}", response_model=schemas.WastageCondition)
def delete_wastage_condition(wastage_factor_id: int, db: Session = Depends(get_db)):
    db_condition = crud.delete_wastage_condition(db=db, wastage_factor_id=wastage_factor_id)
    if db_condition is None:
        raise HTTPException(status_code=404, detail="Wastage condition not found")
    return db_condition
