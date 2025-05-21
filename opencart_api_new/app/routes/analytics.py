from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta

from app.database import get_db
from app.models.online_user import OnlineUser
from app.utils.auth import get_current_admin

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
    responses={404: {"description": "No data found"}},
)

# Define a simple schema for the response
class OnlineUserResponse:
    def __init__(self, ip, customer_id, url, referer, date_added):
        self.ip = ip
        self.customer_id = customer_id
        self.url = url
        self.referer = referer
        self.date_added = date_added

@router.get("/online-users")
def get_online_users(
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin),
    minutes: int = Query(15, ge=1),  # Users active in the last X minutes
    skip: int = 0,
    limit: int = 100
):
    """
    Get list of currently online users (admin only)
    """
    cutoff_time = datetime.now() - timedelta(minutes=minutes)
    
    online_users = db.query(OnlineUser).filter(
        OnlineUser.date_added >= cutoff_time
    ).order_by(desc(OnlineUser.date_added)).offset(skip).limit(limit).all()
    
    return [
        {
            "ip": user.ip,
            "customer_id": user.customer_id,
            "url": user.url,
            "referer": user.referer,
            "date_added": user.date_added
        } for user in online_users
    ]

@router.get("/stats/visitor-count")
def get_visitor_count(
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin),
    days: int = Query(7, ge=1)
):
    """
    Get visitor count statistics (admin only)
    """
    cutoff_date = datetime.now() - timedelta(days=days)
    
    total_visitors = db.query(func.count(OnlineUser.ip.distinct())).filter(
        OnlineUser.date_added >= cutoff_date
    ).scalar()
    
    unique_customers = db.query(func.count(OnlineUser.customer_id.distinct())).filter(
        OnlineUser.date_added >= cutoff_date,
        OnlineUser.customer_id > 0
    ).scalar()
    
    return {
        "total_visitors": total_visitors,
        "unique_customers": unique_customers,
        "period_days": days
    }

@router.get("/stats/popular-pages")
def get_popular_pages(
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin),
    days: int = Query(7, ge=1),
    limit: int = 10
):
    """
    Get most popular pages (admin only)
    """
    cutoff_date = datetime.now() - timedelta(days=days)
    
    popular_pages = db.query(
        OnlineUser.url,
        func.count(OnlineUser.ip).label("visit_count")
    ).filter(
        OnlineUser.date_added >= cutoff_date
    ).group_by(OnlineUser.url).order_by(
        desc("visit_count")
    ).limit(limit).all()
    
    return {
        "popular_pages": [
            {
                "url": url,
                "visit_count": count
            } for url, count in popular_pages
        ],
        "period_days": days
    }