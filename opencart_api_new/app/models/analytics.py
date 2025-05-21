from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean
from datetime import datetime
from app.database import Base

class UserActivity(Base):
    """Enhanced user activity tracking table (separate from original OpenCart tables)"""
    __tablename__ = "api_user_activity"

    activity_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(40), nullable=False, index=True)
    customer_id = Column(Integer, nullable=True, index=True)
    user_type = Column(String(20), nullable=False, default="guest")  # guest, customer, admin
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(Text, nullable=True)
    url = Column(Text, nullable=False)
    referer = Column(Text, nullable=True)
    page_title = Column(String(255), nullable=True)
    query_params = Column(Text, nullable=True)
    time_spent = Column(Integer, nullable=True)  # milliseconds on page
    event_type = Column(String(50), nullable=False)  # pageview, search, add_to_cart, etc.
    event_data = Column(Text, nullable=True)  # JSON data specific to the event
    country = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True) 
    date_added = Column(DateTime, nullable=False, default=datetime.utcnow)


class SearchQuery(Base):
    """Store search queries performed by users"""
    __tablename__ = "api_search_query"

    search_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(40), nullable=False)
    customer_id = Column(Integer, nullable=True, index=True)
    keyword = Column(String(255), nullable=False)
    category_id = Column(Integer, nullable=True)
    filter_data = Column(Text, nullable=True)  # JSON with filter params
    results_count = Column(Integer, nullable=True)
    date_added = Column(DateTime, nullable=False, default=datetime.utcnow)


class ProductView(Base):
    """Track product views for recommendations"""
    __tablename__ = "api_product_view"

    view_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, nullable=False, index=True)
    session_id = Column(String(40), nullable=False)
    customer_id = Column(Integer, nullable=True, index=True)
    source = Column(String(50), nullable=True)  # search, category, related, homepage
    time_spent = Column(Integer, nullable=True)  # seconds viewing product
    date_added = Column(DateTime, nullable=False, default=datetime.utcnow)


class SessionTracking(Base):
    """Track user sessions"""
    __tablename__ = "api_session"

    session_id = Column(String(40), primary_key=True)
    customer_id = Column(Integer, nullable=True, index=True)
    user_type = Column(String(20), nullable=False, default="guest")  # guest, customer, admin
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(Text, nullable=True)
    first_visit = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_activity = Column(DateTime, nullable=False, default=datetime.utcnow)
    visit_count = Column(Integer, nullable=False, default=1)
    country = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    device_type = Column(String(20), nullable=True)  # desktop, mobile, tablet
    browser = Column(String(50), nullable=True)
    os = Column(String(50), nullable=True)
    utm_source = Column(String(100), nullable=True)
    utm_medium = Column(String(100), nullable=True)
    utm_campaign = Column(String(100), nullable=True)
    referring_site = Column(String(255), nullable=True)