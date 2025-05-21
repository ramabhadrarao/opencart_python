from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

# Order product schemas
class OrderProductBase(BaseModel):
    product_id: int
    name: str
    model: str
    quantity: int
    price: float
    total: float
    tax: float
    reward: int
    
    class Config:
        from_attributes = True

# Order Request Models
class OrderCreate(BaseModel):
    customer_id: int
    firstname: str
    lastname: str
    email: str
    telephone: str
    payment_firstname: str
    payment_lastname: str
    payment_address_1: str
    payment_city: str
    payment_postcode: str
    payment_country: str
    payment_method: str
    payment_code: str
    shipping_firstname: str
    shipping_lastname: str
    shipping_address_1: str
    shipping_city: str
    shipping_postcode: str
    shipping_country: str
    shipping_method: str
    shipping_code: str
    products: List[OrderProductBase]
    comment: str = ""
    
    class Config:
        from_attributes = True

class OrderUpdate(BaseModel):
    order_status_id: Optional[int] = None
    comment: Optional[str] = None
    
    class Config:
        from_attributes = True

# Order Response Models
class OrderInList(BaseModel):
    order_id: int
    firstname: str
    lastname: str
    email: str
    total: float
    order_status_id: int
    date_added: datetime
    
    class Config:
        from_attributes = True

class OrderHistoryItem(BaseModel):
    order_history_id: int
    order_status_id: int
    comment: str
    date_added: datetime
    
    class Config:
        from_attributes = True

class OrderDetail(BaseModel):
    order_id: int
    invoice_no: int
    invoice_prefix: str
    store_id: int
    store_name: str
    store_url: str
    customer_id: int
    firstname: str
    lastname: str
    email: str
    telephone: str
    payment_firstname: str
    payment_lastname: str
    payment_company: str
    payment_address_1: str
    payment_address_2: str
    payment_city: str
    payment_postcode: str
    payment_country: str
    payment_country_id: int
    payment_zone: str
    payment_zone_id: int
    payment_method: str
    payment_code: str
    shipping_firstname: str
    shipping_lastname: str
    shipping_company: str
    shipping_address_1: str
    shipping_address_2: str
    shipping_city: str
    shipping_postcode: str
    shipping_country: str
    shipping_country_id: int
    shipping_zone: str
    shipping_zone_id: int
    shipping_method: str
    shipping_code: str
    comment: str
    total: float
    order_status_id: int
    date_added: datetime
    date_modified: datetime
    products: List[OrderProductBase]
    history: List[OrderHistoryItem]
    
    class Config:
        from_attributes = True