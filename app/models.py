from sqlalchemy import Integer, Column, String, Float
from .database import Base

class Product(Base):
    __tablename__ = "products" # Name of the table
    
    product_id = Column(String, primary_key=True)
    description = Column(String, nullable=False)
    unit = Column(String, nullable=False)
    category = Column(String, nullable=False)
    unit_price = Column(Float, default=0, nullable=False)
    supplier = Column(String, nullable=False)
    colour = Column(String, nullable=False)

class Supplier(Base):
    __tablename__ = "suppliers" # Name of the table
    
    supplier_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    warehouse = Column(String, nullable=False)
    contact_number = Column(String, nullable=False)
    po_box = Column(String, nullable=False)
    vendor_address = Column(String, nullable=False)

class Formula(Base):
    __tablename__ = "formulae" # Name of the table
    
    category = Column(String, primary_key=True)
    equation = Column(String, nullable=False)
    wastage_factor = Column(Float, nullable=False)

class WastageCondition(Base):
    __tablename__ = 'wastage_conditions'
    
    wastage_factor_id = Column(Integer, primary_key=True)
    category = Column(String, nullable=False)
    wastage_condition = Column(String, nullable=False)
    wastage_factor = Column(Float, nullable=False)

