from sqlalchemy.orm import Session
from ..models import WastageCondition
from ..schemas import WastageConditionCreate

# Create a new wastage condition
def create_wastage_condition(db: Session, wastage: WastageConditionCreate):
    db_wastage = WastageCondition(
        category=wastage.category,
        wastage_condition=wastage.wastage_condition,
        wastage_factor=wastage.wastage_factor
    )
    db.add(db_wastage)
    db.commit()
    db.refresh(db_wastage)
    return db_wastage

# Get all wastage conditions
def get_wastage_conditions(db: Session, skip: int = 0, limit: int = 10):
    return db.query(WastageCondition).offset(skip).limit(limit).all()

# Get wastage condition by ID
def get_wastage_condition_by_id(db: Session, wastage_factor_id: int):
    return db.query(WastageCondition).filter(WastageCondition.wastage_factor_id == wastage_factor_id).first()

# Update wastage condition by ID
def update_wastage_condition(db: Session, wastage_factor_id: int, category: str, wastage_condition: str, wastage_factor: float):
    db_wastage = db.query(WastageCondition).filter(WastageCondition.wastage_factor_id == wastage_factor_id).first()
    if db_wastage:
        db_wastage.category=category
        db_wastage.wastage_condition=wastage_condition
        db_wastage.wastage_factor=wastage_factor
        db.commit()
        db.refresh(db_wastage)
    return db_wastage

# Delete wastage condition by ID
def delete_wastage_condition(db: Session, wastage_factor_id: int):
    db_wastage = db.query(WastageCondition).filter(WastageCondition.wastage_factor_id == wastage_factor_id).first()
    if db_wastage:
        db.delete(db_wastage)
        db.commit()
    return db_wastage
