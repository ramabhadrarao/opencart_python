from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
import time
import json
import uuid
from datetime import datetime
import re
from user_agents import parse
from urllib.parse import urlparse, parse_qs
import requests

from app.database import SessionLocal
from app.models.analytics import UserActivity, SessionTracking

# Device detection regex patterns
MOBILE_PATTERN = r"(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino"
TABLET_PATTERN = r"(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|pre)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino|android|ipad|playbook|silk"

# Cache for IP geolocation data to reduce API calls
GEOLOCATION_CACHE = {}

class EnhancedTrackingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Start timer for request
        start_time = time.time()
        
        # Get or generate session ID
        session_id = request.cookies.get("session_id")
        is_new_session = False
        if not session_id:
            session_id = str(uuid.uuid4())
            is_new_session = True
        
        # Process the request
        response = await call_next(request)
        
        # Skip tracking for static files and API docs
        url_path = request.url.path
        if url_path.startswith(("/static/", "/api-docs", "/openapi.json")):
            # Still set the session cookie if needed
            if is_new_session:
                response.set_cookie(key="session_id", value=session_id, httponly=True, max_age=2592000)  # 30 days
            return response
        
        # Calculate time spent
        time_spent = int((time.time() - start_time) * 1000)  # milliseconds
        
        # Get client IP
        client_ip = request.client.host
        
        # Get user agent
        user_agent_str = request.headers.get("user-agent", "")
        
        # Determine event type
        event_type = "pageview"
        if "search" in url_path.lower():
            event_type = "search"
        elif "product" in url_path.lower() and url_path.split("/")[-1].isdigit():
            event_type = "product_view"
        elif "cart" in url_path.lower():
            if request.method == "POST":
                event_type = "add_to_cart"
            elif request.method == "DELETE":
                event_type = "remove_from_cart"
            elif request.method == "PUT":
                event_type = "update_cart"
        
        # Extract query params
        query_params = {}
        if request.query_params:
            query_params = dict(request.query_params)
        
        # Determine user type and customer ID
        customer_id = None
        user_type = "guest"
        
        # Try to get auth info from request state (if auth middleware has processed it)
        if hasattr(request.state, "user") and request.state.user:
            user_type = request.state.user.get("type", "guest")
            user = request.state.user.get("user")
            if user:
                customer_id = getattr(user, "customer_id", None) or getattr(user, "user_id", None)
        
        # Extract UTM parameters
        utm_source = query_params.get("utm_source")
        utm_medium = query_params.get("utm_medium")
        utm_campaign = query_params.get("utm_campaign")
        
        # Get referring site
        referer = request.headers.get("referer", "")
        referring_site = ""
        if referer:
            try:
                parsed_referer = urlparse(referer)
                referring_site = parsed_referer.netloc
            except:
                pass
        
        # Detect device, browser, and OS
        device_type = "desktop"
        browser = "unknown"
        os = "unknown"
        
        # Simple device detection
        if re.search(MOBILE_PATTERN, user_agent_str, re.IGNORECASE):
            device_type = "mobile"
        elif re.search(TABLET_PATTERN, user_agent_str, re.IGNORECASE):
            device_type = "tablet"
        
        # Better detection using user-agents library
        try:
            user_agent = parse(user_agent_str)
            browser = f"{user_agent.browser.family} {user_agent.browser.version_string}"
            os = f"{user_agent.os.family} {user_agent.os.version_string}"
            
            if user_agent.is_mobile:
                device_type = "mobile"
            elif user_agent.is_tablet:
                device_type = "tablet"
            elif user_agent.is_pc:
                device_type = "desktop"
        except:
            # Fallback if parsing fails
            pass
        
        # Get geolocation data
        country = None
        region = None
        city = None
        
        # Check cache first to reduce API calls
        if client_ip in GEOLOCATION_CACHE:
            geo_data = GEOLOCATION_CACHE[client_ip]
            country = geo_data.get("country")
            region = geo_data.get("region") 
            city = geo_data.get("city")
        else:
            # Only call geolocation API for real IPs (not localhost)
            if client_ip not in ("127.0.0.1", "localhost", "::1"):
                try:
                    geo_response = requests.get(f"https://ipinfo.io/{client_ip}/json")
                    if geo_response.status_code == 200:
                        geo_data = geo_response.json()
                        country = geo_data.get("country")
                        region = geo_data.get("region")
                        city = geo_data.get("city")
                        
                        # Cache for future use
                        GEOLOCATION_CACHE[client_ip] = {
                            "country": country,
                            "region": region,
                            "city": city
                        }
                except:
                    # Geolocation lookup failed
                    pass
        
        # Record the activity in the database
        try:
            db = SessionLocal()
            
            # 1. First update or create the session
            session = db.query(SessionTracking).filter(SessionTracking.session_id == session_id).first()
            
            if session:
                # Update existing session
                session.last_activity = datetime.utcnow()
                session.visit_count += 1
                if customer_id and not session.customer_id:
                    session.customer_id = customer_id  # Associate session with customer if now logged in
                    session.user_type = user_type
            else:
                # Create new session
                session = SessionTracking(
                    session_id=session_id,
                    customer_id=customer_id,
                    user_type=user_type,
                    ip_address=client_ip,
                    user_agent=user_agent_str,
                    first_visit=datetime.utcnow(),
                    last_activity=datetime.utcnow(),
                    visit_count=1,
                    country=country,
                    region=region,
                    city=city,
                    device_type=device_type,
                    browser=browser,
                    os=os,
                    utm_source=utm_source,
                    utm_medium=utm_medium,
                    utm_campaign=utm_campaign,
                    referring_site=referring_site
                )
                db.add(session)
            
            # 2. Record this activity
            activity = UserActivity(
                session_id=session_id,
                customer_id=customer_id,
                user_type=user_type,
                ip_address=client_ip,
                user_agent=user_agent_str,
                url=str(request.url),
                referer=referer,
                page_title=url_path.split("/")[-1] or "Home",
                query_params=json.dumps(query_params) if query_params else None,
                time_spent=time_spent,
                event_type=event_type,
                event_data=None,  # Could be populated with request body data in more advanced implementations
                country=country,
                region=region,
                city=city,
                date_added=datetime.utcnow()
            )
            db.add(activity)
            
            db.commit()
        except Exception as e:
            print(f"Error tracking user activity: {e}")
        finally:
            db.close()
        
        # Set session ID cookie if new session
        if is_new_session:
            response.set_cookie(key="session_id", value=session_id, httponly=True, max_age=2592000)  # 30 days
        
        return response