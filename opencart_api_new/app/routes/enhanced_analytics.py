from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, distinct
from datetime import datetime, timedelta

from app.database import get_db
from app.models.analytics import UserActivity, SearchQuery, ProductView, SessionTracking
from app.models.enhanced_cart import EnhancedCart, CartHistory, AbandonedCart
from app.utils.auth import get_current_admin

router = APIRouter(
    prefix="/analytics/v2",
    tags=["enhanced-analytics"],
    responses={404: {"description": "No data found"}},
)

@router.get("/dashboard", response_model=Dict[str, Any])
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin),
    days: int = Query(7, ge=1, le=90)
):
    """
    Get comprehensive dashboard statistics (admin only)
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Get visitor stats
    total_sessions = db.query(func.count(distinct(SessionTracking.session_id))).filter(
        SessionTracking.first_visit >= cutoff_date
    ).scalar() or 0
    
    returning_sessions = db.query(func.count(distinct(SessionTracking.session_id))).filter(
        SessionTracking.first_visit < cutoff_date,
        SessionTracking.last_activity >= cutoff_date
    ).scalar() or 0
    
    unique_customers = db.query(func.count(distinct(SessionTracking.customer_id))).filter(
        SessionTracking.customer_id.isnot(None),
        SessionTracking.last_activity >= cutoff_date
    ).scalar() or 0
    
    # Get device stats
    device_stats = db.query(
        SessionTracking.device_type,
        func.count(distinct(SessionTracking.session_id)).label("count")
    ).filter(
        SessionTracking.last_activity >= cutoff_date
    ).group_by(SessionTracking.device_type).all()
    
    device_breakdown = {device: count for device, count in device_stats}
    
    # Get page view stats
    page_views = db.query(func.count(UserActivity.activity_id)).filter(
        UserActivity.date_added >= cutoff_date,
        UserActivity.event_type == "pageview"
    ).scalar() or 0
    
    product_views = db.query(func.count(UserActivity.activity_id)).filter(
        UserActivity.date_added >= cutoff_date,
        UserActivity.event_type == "product_view"
    ).scalar() or 0
    
    search_count = db.query(func.count(SearchQuery.search_id)).filter(
        SearchQuery.date_added >= cutoff_date
    ).scalar() or 0
    
    # Get cart stats
    cart_add_count = db.query(func.count(CartHistory.history_id)).filter(
        CartHistory.date_added >= cutoff_date,
        CartHistory.action == "add"
    ).scalar() or 0
    
    abandoned_carts = db.query(func.count(AbandonedCart.abandoned_id)).filter(
        AbandonedCart.abandoned_date >= cutoff_date,
        AbandonedCart.recovery_status == "pending"
    ).scalar() or 0
    
    # Get location stats
    location_stats = db.query(
        SessionTracking.country,
        func.count(distinct(SessionTracking.session_id)).label("count")
    ).filter(
        SessionTracking.last_activity >= cutoff_date,
        SessionTracking.country.isnot(None)
    ).group_by(SessionTracking.country).order_by(desc("count")).limit(5).all()
    
    location_breakdown = [{"country": country, "count": count} for country, count in location_stats]
    
    # Combine all stats
    return {
        "visitors": {
            "total_sessions": total_sessions,
            "returning_sessions": returning_sessions,
            "unique_customers": unique_customers,
            "device_breakdown": device_breakdown
        },
        "activity": {
            "page_views": page_views,
            "product_views": product_views,
            "searches": search_count,
            "cart_adds": cart_add_count,
            "abandoned_carts": abandoned_carts
        },
        "geo": {
            "top_countries": location_breakdown
        },
        "period_days": days
    }

@router.get("/visitors/online", response_model=Dict[str, Any])
def get_online_visitors(
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin),
    minutes: int = Query(15, ge=1, le=60)
):
    """
    Get visitors currently online (admin only)
    """
    cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
    
    # Get sessions with recent activity
    sessions = db.query(SessionTracking).filter(
        SessionTracking.last_activity >= cutoff_time
    ).all()
    
    # For each session, get the last activity
    result = []
    for session in sessions:
        last_activity = db.query(UserActivity).filter(
            UserActivity.session_id == session.session_id
        ).order_by(desc(UserActivity.date_added)).first()
        
        result.append({
            "session_id": session.session_id,
            "user_type": session.user_type,
            "customer_id": session.customer_id,
            "ip_address": session.ip_address,
            "device_type": session.device_type,
            "browser": session.browser,
            "location": f"{session.city or ''}, {session.region or ''}, {session.country or ''}",
            "last_activity_time": session.last_activity,
            "last_url": last_activity.url if last_activity else None,
            "last_page": last_activity.page_title if last_activity else None,
            "visit_count": session.visit_count
        })
    
    return {
        "online_visitors": result,
        "total": len(result),
        "time_window_minutes": minutes
    }

@router.get("/content/popular", response_model=Dict[str, Any])
def get_popular_content(
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin),
    days: int = Query(7, ge=1, le=90),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Get most popular content (admin only)
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Get popular pages
    popular_pages = db.query(
        UserActivity.url,
        UserActivity.page_title,
        func.count(UserActivity.activity_id).label("view_count")
    ).filter(
        UserActivity.date_added >= cutoff_date,
        UserActivity.event_type == "pageview"
    ).group_by(UserActivity.url, UserActivity.page_title).order_by(
        desc("view_count")
    ).limit(limit).all()
    
    # Get popular products
    popular_products = db.query(
        ProductView.product_id,
        func.count(ProductView.view_id).label("view_count")
    ).filter(
        ProductView.date_added >= cutoff_date
    ).group_by(ProductView.product_id).order_by(
        desc("view_count")
    ).limit(limit).all()
    
    # Get popular search terms
    popular_searches = db.query(
        SearchQuery.keyword,
        func.count(SearchQuery.search_id).label("search_count")
    ).filter(
        SearchQuery.date_added >= cutoff_date
    ).group_by(SearchQuery.keyword).order_by(
        desc("search_count")
    ).limit(limit).all()
    
    return {
        "popular_pages": [
            {
                "url": url,
                "title": title or url.split("/")[-1],
                "view_count": count
            } for url, title, count in popular_pages
        ],
        "popular_products": [
            {
                "product_id": product_id,
                "view_count": count
            } for product_id, count in popular_products
        ],
        "popular_searches": [
            {
                "keyword": keyword,
                "search_count": count
            } for keyword, count in popular_searches
        ],
        "period_days": days
    }

@router.get("/carts/abandoned", response_model=Dict[str, Any])
def get_abandoned_carts(
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin),
    days: int = Query(7, ge=1, le=90),
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
):
    """
    Get abandoned cart data (admin only)
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Build query
    query = db.query(AbandonedCart).filter(
        AbandonedCart.abandoned_date >= cutoff_date
    )
    
    if status:
        query = query.filter(AbandonedCart.recovery_status == status)
    
    # Count total for pagination
    total = query.count()
    
    # Apply pagination
    query = query.order_by(desc(AbandonedCart.abandoned_date)).offset((page - 1) * size).limit(size)
    
    # Get results
    carts = query.all()
    
    # Calculate statistics
    total_abandoned = db.query(func.count(AbandonedCart.abandoned_id)).filter(
        AbandonedCart.abandoned_date >= cutoff_date
    ).scalar() or 0
    
    total_recovered = db.query(func.count(AbandonedCart.abandoned_id)).filter(
        AbandonedCart.abandoned_date >= cutoff_date,
        AbandonedCart.recovery_status == "recovered"
    ).scalar() or 0
    
    recovery_rate = (total_recovered / total_abandoned * 100) if total_abandoned > 0 else 0
    
    # Format the response
    result_carts = []
    for cart in carts:
        # Parse cart contents
        contents = []
        if cart.cart_contents:
            try:
                contents = json.loads(cart.cart_contents)
            except:
                contents = []
        
        result_carts.append({
            "abandoned_id": cart.abandoned_id,
            "session_id": cart.session_id,
            "customer_id": cart.customer_id,
            "email": cart.email,
            "total_items": cart.total_items,
            "total_value": cart.total_value,
            "cart_contents": contents,
            "abandoned_date": cart.abandoned_date,
            "recovery_status": cart.recovery_status,
            "notification_count": cart.notification_count,
            "recovered_order_id": cart.recovered_order_id
        })
    
    return {
        "abandoned_carts": result_carts,
        "total": total,
        "page": page,
        "size": size,
        "pages": math.ceil(total / size) if total > 0 else 0,
        "stats": {
            "total_abandoned": total_abandoned,
            "total_recovered": total_recovered,
            "recovery_rate": f"{recovery_rate:.2f}%"
        },
        "period_days": days
    }

@router.get("/search/analysis", response_model=Dict[str, Any])
def get_search_analysis(
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin),
    days: int = Query(7, ge=1, le=90)
):
    """
    Get search query analysis (admin only)
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Get search volume by day
    search_volume = db.query(
        func.date(SearchQuery.date_added).label("date"),
        func.count(SearchQuery.search_id).label("count")
    ).filter(
        SearchQuery.date_added >= cutoff_date
    ).group_by("date").order_by("date").all()
    
    # Get popular search terms
    popular_searches = db.query(
        SearchQuery.keyword,
        func.count(SearchQuery.search_id).label("count"),
        func.avg(SearchQuery.results_count).label("avg_results")
    ).filter(
        SearchQuery.date_added >= cutoff_date
    ).group_by(SearchQuery.keyword).order_by(
        desc("count")
    ).limit(20).all()
    
    # Get zero-result searches
    zero_result_searches = db.query(
        SearchQuery.keyword,
        func.count(SearchQuery.search_id).label("count")
    ).filter(
        SearchQuery.date_added >= cutoff_date,
        SearchQuery.results_count == 0
    ).group_by(SearchQuery.keyword).order_by(
        desc("count")
    ).limit(20).all()
    
    return {
        "search_volume": [
            {
                "date": date.strftime("%Y-%m-%d"),
                "count": count
            } for date, count in search_volume
        ],
        "popular_searches": [
            {
                "keyword": keyword,
                "count": count,
                "avg_results": float(avg_results) if avg_results is not None else None
            } for keyword, count, avg_results in popular_searches
        ],
        "zero_result_searches": [
            {
                "keyword": keyword,
                "count": count
            } for keyword, count in zero_result_searches
        ],
        "period_days": days
    }