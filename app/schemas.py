from pydantic import BaseModel

# Product Schemas

class ProductCreate(BaseModel):
    product_id: str
    description: str
    unit: str
    category: str
    unit_price: float
    supplier: str
    colour: str


class Product(BaseModel):
    product_id: str
    description: str
    unit: str
    category: str
    unit_price: float
    supplier: str
    colour: str

    class Config:
        from_attributes = True


# Supplier Schemas

class SupplierCreate(BaseModel):
    supplier_id: str
    name: str
    warehouse: str
    contact_number: str
    po_box: str
    vendor_address: str

class Supplier(BaseModel):
    # created_at: Optional[datetime] = None
    # updated_at: Optional[datetime] = None
    supplier_id: str
    name: str
    warehouse: str
    contact_number: str
    po_box: str
    vendor_address: str

    class Config:
        from_attributes = True


# Formula Schemas

class FormulaCreate(BaseModel):
    category: str
    equation: str
    wastage_factor: float
    is_colour: bool

class Formula(BaseModel):
    # created_at: Optional[datetime] = None
    # updated_at: Optional[datetime] = None
    category: str
    equation: str
    wastage_factor: float
    is_colour: bool

    class Config:
        from_attributes = True

# Wastage-Conditions Schemas

class WastageConditionCreate(BaseModel):
    wastage_factor_id: int
    category: str
    wastage_condition: str
    wastage_factor: float

class WastageCondition(BaseModel):
    # created_at: Optional[datetime] = None
    # updated_at: Optional[datetime] = None
    wastage_factor_id: int
    category: str
    wastage_condition: str
    wastage_factor: float

    class Config:
        from_attributes = True
        
