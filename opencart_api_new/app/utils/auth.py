import hashlib
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.customer import Customer
from app.models.user import User
from app.config import settings

# Create OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

# JWT configuration
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

def verify_password_customer(plain_password: str, hashed_password: str, salt: str) -> bool:
    """Verify customer password using OpenCart's hashing method"""
    # OpenCart hash: sha1(salt . sha1(salt . sha1(password)))
    password_hash = hashlib.sha1((salt + hashlib.sha1((salt + hashlib.sha1(plain_password.encode()).hexdigest()).encode()).hexdigest()).encode()).hexdigest()
    return password_hash == hashed_password

def verify_password_admin(plain_password: str, hashed_password: str, salt: str) -> bool:
    """Verify admin user password using OpenCart's hashing method"""
    # OpenCart hash: sha1(salt . sha1(salt . sha1(password)))
    password_hash = hashlib.sha1((salt + hashlib.sha1((salt + hashlib.sha1(plain_password.encode()).hexdigest()).encode()).hexdigest()).encode()).hexdigest()
    return password_hash == hashed_password

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_customer(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current authenticated customer"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        customer_id: int = payload.get("sub")
        if customer_id is None or payload.get("type") != "customer":
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    # Get the customer from database
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if customer is None:
        raise credentials_exception
    
    return customer

def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current authenticated admin user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None or payload.get("type") != "admin":
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    # Get the admin user from database
    admin = db.query(User).filter(User.user_id == user_id).first()
    if admin is None:
        raise credentials_exception
    
    return admin

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current authenticated user (either customer or admin)"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        user_type: str = payload.get("type")
        if user_id is None or user_type not in ["customer", "admin"]:
            raise credentials_exception
        
        if user_type == "customer":
            user = db.query(Customer).filter(Customer.customer_id == user_id).first()
        else:  # admin
            user = db.query(User).filter(User.user_id == user_id).first()
            
        if user is None:
            raise credentials_exception
            
        return {"user": user, "type": user_type}
    except jwt.PyJWTError:
        raise credentials_exception