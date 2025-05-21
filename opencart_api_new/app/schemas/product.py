from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

# Schemas for request/response
class ProductOptionValueBase(BaseModel):
    option_value_id: int
    quantity: int
    subtract: bool
    price: float
    price_prefix: str
    
    class Config:
        from_attributes = True

class ProductOptionBase(BaseModel):
    option_id: int
    value: str
    required: bool
    option_values: List[ProductOptionValueBase] = []
    
    class Config:
        from_attributes = True

class ProductImageBase(BaseModel):
    image: Optional[str] = None
    sort_order: int = 0
    
    class Config:
        from_attributes = True

class ProductAttributeBase(BaseModel):
    attribute_id: int
    text: str
    
    class Config:
        from_attributes = True

class ProductDescriptionBase(BaseModel):
    language_id: int
    name: str
    description: str
    meta_title: str
    meta_description: str
    meta_keyword: str
    tag: str = ""
    
    class Config:
        from_attributes = True

class ProductSpecificationBase(BaseModel):
    machine_name: str
    price: str
    image: str
    
    class Config:
        from_attributes = True

# Product Request Models
class ProductCreate(BaseModel):
    model: str
    sku: str = ""
    upc: str = ""
    ean: str = ""
    jan: str = ""
    isbn: str = ""
    mpn: str = ""
    location: str = ""
    quantity: int = 0
    stock_status_id: int = 0
    image: Optional[str] = None
    manufacturer_id: int = 0
    shipping: bool = True
    price: float = 0.0
    points: int = 0
    tax_class_id: int = 0
    date_available: Optional[datetime] = None
    weight: float = 0.0
    weight_class_id: int = 0
    length: float = 0.0
    width: float = 0.0
    height: float = 0.0
    length_class_id: int = 0
    subtract: bool = True
    minimum: int = 1
    sort_order: int = 0
    status: bool = True
    descriptions: List[ProductDescriptionBase]
    images: List[ProductImageBase] = []
    categories: List[int] = []
    attributes: List[ProductAttributeBase] = []
    options: List[ProductOptionBase] = []
    specifications: List[ProductSpecificationBase] = []
    
    class Config:
        from_attributes = True

class ProductUpdate(BaseModel):
    model: Optional[str] = None
    sku: Optional[str] = None
    image: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[float] = None
    status: Optional[bool] = None
    descriptions: Optional[List[ProductDescriptionBase]] = None
    
    class Config:
        from_attributes = True

# Product Response Models
class ProductInList(BaseModel):
    product_id: int
    model: str
    name: str
    price: float
    quantity: int
    status: bool
    image: Optional[str] = None
    
    class Config:
        from_attributes = True

class ProductDetail(BaseModel):
    product_id: int
    model: str
    sku: str
    upc: str
    ean: str
    jan: str
    isbn: str
    mpn: str
    location: str
    quantity: int
    stock_status_id: int
    image: Optional[str] = None
    manufacturer_id: int
    shipping: bool
    price: float
    points: int
    tax_class_id: int
    date_available: Optional[datetime] = None
    weight: float
    weight_class_id: int
    length: float
    width: float
    height: float
    length_class_id: int
    subtract: bool
    minimum: int
    sort_order: int
    status: bool
    viewed: int
    date_added: datetime
    date_modified: datetime
    descriptions: List[ProductDescriptionBase]
    images: List[ProductImageBase]
    options: List[ProductOptionBase]
    attributes: List[ProductAttributeBase]
    specifications: List[ProductSpecificationBase]
    
    class Config:
        from_attributes = True