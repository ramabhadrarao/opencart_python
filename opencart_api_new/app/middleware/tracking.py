from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
import time
import uuid
from datetime import datetime
from app.database import SessionLocal
from app.models.online_user import OnlineUser

class TrackingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Generate a unique session ID if not present
        session_id = request.cookies.get("session_id")
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Process the request
        response = await call_next(request)
        
        # Record the user activity in the database
        url_path = request.url.path
        if not url_path.startswith(("/static/", "/api-docs", "/openapi.json")):
            try:
                db = SessionLocal()
                
                # Get client IP
                client_ip = request.client.host
                
                # Try to find existing session
                online_user = db.query(OnlineUser).filter(OnlineUser.ip == client_ip).first()
                
                if online_user:
                    # Update existing session
                    online_user.url = str(request.url)
                    online_user.referer = request.headers.get("referer", "")
                    online_user.date_added = datetime.now()
                else:
                    # Create new session record
                    new_user = OnlineUser(
                        ip=client_ip,
                        customer_id=0,  # Default to 0 for guests
                        url=str(request.url),
                        referer=request.headers.get("referer", ""),
                        date_added=datetime.now()
                    )
                    db.add(new_user)
                
                db.commit()
            except Exception as e:
                print(f"Error tracking user activity: {e}")
            finally:
                db.close()
        
        # Set session ID cookie if not present
        if "session_id" not in request.cookies:
            response.set_cookie(key="session_id", value=session_id, httponly=True)
        
        return response