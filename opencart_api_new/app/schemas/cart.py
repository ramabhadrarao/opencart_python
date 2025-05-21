from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class CartItemBase(BaseModel):
    product_id: int
    quantity: int
    option: Dict[str, Any] = {}  # Product options as JSON
    recurring_id: int = 0
    
    class Config:
        from_attributes = True

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: Optional[int] = None
    option: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

class CartItem(CartItemBase):
    cart_id: int
    date_added: datetime
    
    # Additional fields not in DB but populated for API response
    product_name: Optional[str] = None
    product_image: Optional[str] = None
    price: Optional[float] = None
    total: Optional[float] = None
    
    class Config:
        from_attributes = True

class CartSummary(BaseModel):
    items: List[CartItem]
    total_items: int
    total_price: float
    
    class Config:
        from_attributes = True