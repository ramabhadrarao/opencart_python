from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class UserActivityBase(BaseModel):
    session_id: str
    customer_id: Optional[int] = None
    user_type: str = "guest"
    ip_address: str
    user_agent: Optional[str] = None
    url: str
    referer: Optional[str] = None
    page_title: Optional[str] = None
    query_params: Optional[str] = None
    time_spent: Optional[int] = None
    event_type: str
    event_data: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    
    class Config:
        from_attributes = True

class UserActivity(UserActivityBase):
    activity_id: int
    date_added: datetime
    
    class Config:
        from_attributes = True

class SearchQueryBase(BaseModel):
    session_id: str
    customer_id: Optional[int] = None
    keyword: str
    category_id: Optional[int] = None
    filter_data: Optional[str] = None
    results_count: Optional[int] = None
    
    class Config:
        from_attributes = True

class SearchQuery(SearchQueryBase):
    search_id: int
    date_added: datetime
    
    class Config:
        from_attributes = True

class ProductViewBase(BaseModel):
    product_id: int
    session_id: str
    customer_id: Optional[int] = None
    source: Optional[str] = None
    time_spent: Optional[int] = None
    
    class Config:
        from_attributes = True

class ProductView(ProductViewBase):
    view_id: int
    date_added: datetime
    
    class Config:
        from_attributes = True

class SessionTrackingBase(BaseModel):
    session_id: str
    customer_id: Optional[int] = None
    user_type: str = "guest"
    ip_address: str
    user_agent: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    device_type: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    referring_site: Optional[str] = None
    
    class Config:
        from_attributes = True

class SessionTracking(SessionTrackingBase):
    first_visit: datetime
    last_activity: datetime
    visit_count: int
    
    class Config:
        from_attributes = True