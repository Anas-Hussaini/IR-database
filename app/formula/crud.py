from sqlalchemy.orm import Session
from ..models import Formula
from ..schemas import FormulaCreate
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a new formula
def create_formula(db: Session, formula: FormulaCreate):
    """
    Creates a new formula in the database.

    Parameters:
        db (Session): The SQLAlchemy session object.
        formula (FormulaCreate): The formula data to be created.

    Returns:
        Formula: The created formula object.
    """
    try:
        db_formula = Formula(
            category=formula.category,
            equation=formula.equation,
            wastage_factor=formula.wastage_factor,
            is_colour=formula.is_colour
        )
        db.add(db_formula)
        db.commit()
        db.refresh(db_formula)
        logger.info("Successfully created a new formula with category: %s", formula.category)
        return db_formula
    except Exception as e:
        logger.error("Error occurred while creating formula: %s", e)
        db.rollback()
        raise

# Get all formulas
def get_formulas(db: Session, skip: int = 0, limit: int = 10):
    """
    Retrieves all formulas from the database.

    Parameters:
        db (Session): The SQLAlchemy session object.
        skip (int): The number of records to skip.
        limit (int): The number of records to retrieve.

    Returns:
        List[Formula]: A list of formula objects.
    """
    try:
        formulas = db.query(Formula).offset(skip).limit(limit).all()
        logger.info("Retrieved %d formulas from the database.", len(formulas))
        return formulas
    except Exception as e:
        logger.error("Error occurred while fetching formulas: %s", e)
        raise
    
    from sqlalchemy.orm import Session
from sqlalchemy import distinct
from typing import List

from sqlalchemy.orm import Session
from typing import Tuple, List

def get_categories_with_variation_type(db: Session) -> Tuple[List[str], List[str]]:
    """
    Categorizes categories based on the value of the 'is_colour' column.

    Parameters:
        db (Session): The SQLAlchemy session object.

    Returns:
        Tuple[List[str], List[str]]: 
            - A list of categories where 'is_colour' is True.
            - A list of categories where 'is_colour' is False.
    """
    try:
        logger.info("Categorizing categories based on the 'is_colour' column.")
        
        # Fetch all rows with category and is_colour columns
        rows = db.query(Formula.category, Formula.is_colour).distinct().all()
        
        # Initialize the result lists
        categories_with_colour = []
        categories_with_no_variation = []

        # Categorize based on the value of 'is_colour'
        for category, is_colour in rows:
            if is_colour:  # If 'is_colour' is True
                categories_with_colour.append(category)
            else:  # If 'is_colour' is False
                categories_with_no_variation.append(category)
        
        logger.info("Categorized %d categories with colour and %d without variation.",
                    len(categories_with_colour), len(categories_with_no_variation))
        return categories_with_colour, categories_with_no_variation
    except Exception as e:
        logger.error("Error occurred while categorizing categories: %s", e)
        raise



# Get formula by category
def get_formula_by_category(db: Session, category: str):
    """
    Retrieves a formula by its category.

    Parameters:
        db (Session): The SQLAlchemy session object.
        category (str): The category of the formula to retrieve.

    Returns:
        Formula or None: The formula object if found, otherwise None.
    """
    try:
        formula = db.query(Formula).filter(Formula.category == category).first()
        if formula:
            logger.info("Retrieved formula with category: %s", category)
        else:
            logger.warning("No formula found with category: %s", category)
        return formula
    except Exception as e:
        logger.error("Error occurred while fetching formula by category: %s", e)
        raise

# Update formula by category
def update_formula(db: Session, category: str, equation: str, wastage_factor: float, is_colour: bool):
    """
    Updates an existing formula by its category.

    Parameters:
        db (Session): The SQLAlchemy session object.
        category (str): The category of the formula to update.
        equation (str): The new equation value.
        wastage_factor (float): The new wastage factor value.

    Returns:
        Formula or None: The updated formula object if successful, otherwise None.
    """
    try:
        db_formula = db.query(Formula).filter(Formula.category == category).first()
        if db_formula:
            db_formula.equation = equation
            db_formula.wastage_factor = wastage_factor
            db_formula.is_colour = is_colour
            db.commit()
            db.refresh(db_formula)
            logger.info("Updated formula with category: %s", category)
        else:
            logger.warning("No formula found with category: %s", category)
        return db_formula
    except Exception as e:
        logger.error("Error occurred while updating formula by category: %s", e)
        db.rollback()
        raise

# Delete formula by category
def delete_formula(db: Session, category: str):
    """
    Deletes a formula by its category from the database.

    Parameters:
        db (Session): The SQLAlchemy session object.
        category (str): The category of the formula to delete.

    Returns:
        Formula or None: The deleted formula object if successful, otherwise None.
    """
    try:
        db_formula = db.query(Formula).filter(Formula.category == category).first()
        if db_formula:
            db.delete(db_formula)
            db.commit()
            logger.info("Deleted formula with category: %s", category)
        else:
            logger.warning("No formula found with category: %s", category)
        return db_formula
    except Exception as e:
        logger.error("Error occurred while deleting formula by category: %s", e)
        db.rollback()
        raise
