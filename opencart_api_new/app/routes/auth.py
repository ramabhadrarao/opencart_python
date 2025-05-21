from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any

from app.database import get_db
from app.models.customer import Customer
from app.models.user import User
from app.schemas.auth import Token, CustomerLogin, AdminLogin
from app.utils.auth import (
    verify_password_customer, verify_password_admin,
    create_access_token, get_current_customer, get_current_admin
)

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)

@router.post("/customer/login", response_model=Token)
def login_customer(login_data: CustomerLogin, db: Session = Depends(get_db)) -> Any:
    """
    Customer login endpoint
    """
    customer = db.query(Customer).filter(Customer.email == login_data.email).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password using OpenCart's method
    if not verify_password_customer(login_data.password, customer.password, customer.salt):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(
        data={
            "sub": customer.customer_id,
            "type": "customer",
            "name": f"{customer.firstname} {customer.lastname}",
            "email": customer.email
        }
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/admin/login", response_model=Token)
def login_admin(login_data: AdminLogin, db: Session = Depends(get_db)) -> Any:
    """
    Admin login endpoint
    """
    admin = db.query(User).filter(User.username == login_data.username).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password using OpenCart's method
    if not verify_password_admin(login_data.password, admin.password, admin.salt):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(
        data={
            "sub": admin.user_id,
            "type": "admin",
            "isAdmin": True,
            "username": admin.username,
            "email": admin.email
        }
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/customer/me", response_model=dict)
def get_current_customer_info(current_customer: Customer = Depends(get_current_customer)) -> Any:
    """
    Get information about currently authenticated customer
    """
    return {
        "id": current_customer.customer_id,
        "firstname": current_customer.firstname,
        "lastname": current_customer.lastname,
        "email": current_customer.email,
        "telephone": current_customer.telephone,
        "status": current_customer.status
    }

@router.get("/admin/me", response_model=dict)
def get_current_admin_info(current_admin: User = Depends(get_current_admin)) -> Any:
    """
    Get information about currently authenticated admin
    """
    return {
        "id": current_admin.user_id,
        "username": current_admin.username,
        "firstname": current_admin.firstname,
        "lastname": current_admin.lastname,
        "email": current_admin.email,
        "status": current_admin.status
    }