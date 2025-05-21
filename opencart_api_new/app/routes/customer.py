from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models.customer import Customer
from app.schemas.customer import CustomerInList, CustomerDetail, CustomerCreate, CustomerUpdate
from app.utils.auth import get_current_admin, get_current_customer  # Add this import

router = APIRouter(
    prefix="/customers",
    tags=["customers"],
    responses={404: {"description": "Customer not found"}},
)

@router.get("/", response_model=List[CustomerInList])
def get_customers(
    db: Session = Depends(get_db), 
    skip: int = 0, 
    limit: int = 100,
    current_admin = Depends(get_current_admin)  # Restrict customer list to admin only
):
    """
    Get list of customers (admin only)
    """
    customers = db.query(Customer).offset(skip).limit(limit).all()
    return customers

@router.get("/me", response_model=CustomerDetail)
def get_my_profile(
    db: Session = Depends(get_db),
    current_customer = Depends(get_current_customer)  # Get current authenticated customer
):
    """
    Get profile of the currently authenticated customer
    """
    return current_customer

@router.get("/{customer_id}", response_model=CustomerDetail)
def get_customer(
    customer_id: int, 
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)  # Restrict to admin only
):
    """
    Get detailed information about a specific customer (admin only)
    """
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return customer

@router.post("/", response_model=CustomerDetail, status_code=201)
def create_customer(customer_data: CustomerCreate, db: Session = Depends(get_db)):
    """
    Create a new customer (registration, available to public)
    """
    # Check if email already exists
    existing_customer = db.query(Customer).filter(Customer.email == customer_data.email).first()
    if existing_customer:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # In a real implementation, you'd hash the password here
    import hashlib
    import uuid
    
    salt = uuid.uuid4().hex[:9]
    password_hash = hashlib.sha1((customer_data.password + salt).encode()).hexdigest()
    
    new_customer = Customer(
        customer_group_id=customer_data.customer_group_id,
        store_id=customer_data.store_id,
        language_id=customer_data.language_id,
        firstname=customer_data.firstname,
        lastname=customer_data.lastname,
        email=customer_data.email,
        telephone=customer_data.telephone,
        fax=customer_data.fax,
        password=password_hash,
        salt=salt,
        newsletter=customer_data.newsletter,
        status=customer_data.status,
        custom_field="",
        ip="",
        safe=0,
        token="",
        code="",
        date_added=datetime.now(),
        verifymobile=0
    )
    
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    
    return new_customer

@router.put("/me", response_model=CustomerDetail)
def update_my_profile(
    customer_data: CustomerUpdate, 
    db: Session = Depends(get_db),
    current_customer = Depends(get_current_customer)  # Get current authenticated customer
):
    """
    Update the currently authenticated customer's profile
    """
    customer = current_customer
    
    # If email is provided and differs from current, check for duplicates
    if customer_data.email and customer_data.email != customer.email:
        existing_customer = db.query(Customer).filter(Customer.email == customer_data.email).first()
        if existing_customer:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # Update customer fields if provided
    if customer_data.firstname:
        customer.firstname = customer_data.firstname
    if customer_data.lastname:
        customer.lastname = customer_data.lastname
    if customer_data.email:
        customer.email = customer_data.email
    if customer_data.telephone:
        customer.telephone = customer_data.telephone
    
    # Handle password update
    if customer_data.password:
        import hashlib
        import uuid
        
        salt = uuid.uuid4().hex[:9]
        password_hash = hashlib.sha1((customer_data.password + salt).encode()).hexdigest()
        
        customer.password = password_hash
        customer.salt = salt
    
    db.commit()
    db.refresh(customer)
    
    return customer

@router.put("/{customer_id}", response_model=CustomerDetail)
def update_customer(
    customer_id: int, 
    customer_data: CustomerUpdate, 
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)  # Restrict to admin only
):
    """
    Update a customer (admin only)
    """
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # If email is provided and differs from current, check for duplicates
    if customer_data.email and customer_data.email != customer.email:
        existing_customer = db.query(Customer).filter(Customer.email == customer_data.email).first()
        if existing_customer:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # Update customer fields if provided
    if customer_data.firstname:
        customer.firstname = customer_data.firstname
    if customer_data.lastname:
        customer.lastname = customer_data.lastname
    if customer_data.email:
        customer.email = customer_data.email
    if customer_data.telephone:
        customer.telephone = customer_data.telephone
    if customer_data.status is not None:
        customer.status = customer_data.status
    
    # Handle password update
    if customer_data.password:
        import hashlib
        import uuid
        
        salt = uuid.uuid4().hex[:9]
        password_hash = hashlib.sha1((customer_data.password + salt).encode()).hexdigest()
        
        customer.password = password_hash
        customer.salt = salt
    
    db.commit()
    db.refresh(customer)
    
    return customer

@router.delete("/{customer_id}", status_code=204)
def delete_customer(
    customer_id: int, 
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)  # Restrict to admin only
):
    """
    Delete a customer (admin only)
    """
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    db.delete(customer)
    db.commit()
    
    return None