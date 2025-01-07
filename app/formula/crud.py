from sqlalchemy.orm import Session
from ..models import Formula
from ..schemas import FormulaCreate

# Create a new formula
def create_formula(db: Session, formula: FormulaCreate):
    db_formula = Formula(
        category=formula.category,
        equation=formula.equation,
        wastage_factor=formula.wastage_factor
    )
    db.add(db_formula)
    db.commit()
    db.refresh(db_formula)
    return db_formula

# Get all formulas
def get_formulas(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Formula).offset(skip).limit(limit).all()

# Get formula by category
def get_formula_by_category(db: Session, category: str):
    return db.query(Formula).filter(Formula.category == category).first()

# Update formula by category
def update_formula(db: Session, category: str, equation: str, wastage_factor:float):
    db_formula = db.query(Formula).filter(Formula.category == category).first()
    if db_formula:
        db_formula.equation = equation
        db_formula.wastage_factor = wastage_factor
        db.commit()
        db.refresh(db_formula)
    return db_formula

# Delete formula by category
def delete_formula(db: Session, category: str):
    db_formula = db.query(Formula).filter(Formula.category == category).first()
    if db_formula:
        db.delete(db_formula)
        db.commit()
    return db_formula
