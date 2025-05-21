from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.address import Address
from app.schemas.address import Address as AddressSchema, AddressCreate, AddressUpdate
from app.utils.auth import get_current_customer, get_current_admin

router = APIRouter(
    prefix="/addresses",
    tags=["addresses"],
    responses={404: {"description": "Address not found"}},
)

@router.get("/my-addresses", response_model=List[AddressSchema])
def get_my_addresses(
    db: Session = Depends(get_db),
    current_customer = Depends(get_current_customer)
):
    """
    Get all addresses for the current customer
    """
    addresses = db.query(Address).filter(Address.customer_id == current_customer.customer_id).all()
    return addresses

@router.get("/{address_id}", response_model=AddressSchema)
def get_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_customer = Depends(get_current_customer)
):
    """
    Get a specific address for the current customer
    """
    address = db.query(Address).filter(
        Address.address_id == address_id,
        Address.customer_id == current_customer.customer_id
    ).first()
    
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    
    return address

@router.post("/", response_model=AddressSchema)
def create_address(
    address_data: AddressCreate,
    db: Session = Depends(get_db),
    current_customer = Depends(get_current_customer)
):
    """
    Create a new address for the current customer
    """
    db_address = Address(
        customer_id=current_customer.customer_id,
        firstname=address_data.firstname,
        lastname=address_data.lastname,
        company=address_data.company,
        address_1=address_data.address_1,
        address_2=address_data.address_2,
        city=address_data.city,
        postcode=address_data.postcode,
        country_id=address_data.country_id,
        zone_id=address_data.zone_id,
        custom_field=address_data.custom_field
    )
    
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    
    return db_address

@router.put("/{address_id}", response_model=AddressSchema)
def update_address(
    address_id: int,
    address_data: AddressUpdate,
    db: Session = Depends(get_db),
    current_customer = Depends(get_current_customer)
):
    """
    Update an address for the current customer
    """
    address = db.query(Address).filter(
        Address.address_id == address_id,
        Address.customer_id == current_customer.customer_id
    ).first()
    
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    
    # Update fields if provided
    if address_data.firstname:
        address.firstname = address_data.firstname
    if address_data.lastname:
        address.lastname = address_data.lastname
    if address_data.company is not None:
        address.company = address_data.company
    if address_data.address_1:
        address.address_1 = address_data.address_1
    if address_data.address_2 is not None:
        address.address_2 = address_data.address_2
    if address_data.city:
        address.city = address_data.city
    if address_data.postcode:
        address.postcode = address_data.postcode
    if address_data.country_id:
        address.country_id = address_data.country_id
    if address_data.zone_id:
        address.zone_id = address_data.zone_id
    if address_data.custom_field is not None:
        address.custom_field = address_data.custom_field
    
    db.commit()
    db.refresh(address)
    
    return address

@router.delete("/{address_id}", status_code=204)
def delete_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_customer = Depends(get_current_customer)
):
    """
    Delete an address for the current customer
    """
    address = db.query(Address).filter(
        Address.address_id == address_id,
        Address.customer_id == current_customer.customer_id
    ).first()
    
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    
    db.delete(address)
    db.commit()
    
    return None

# Admin routes for addresses
@router.get("/admin/customer/{customer_id}", response_model=List[AddressSchema])
def get_customer_addresses(
    customer_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    Get all addresses for a specific customer (admin only)
    """
    addresses = db.query(Address).filter(Address.customer_id == customer_id).all()
    return addresses

@router.put("/admin/{address_id}", response_model=AddressSchema)
def admin_update_address(
    address_id: int,
    address_data: AddressUpdate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    Update any address (admin only)
    """
    address = db.query(Address).filter(Address.address_id == address_id).first()
    
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    
    # Update fields if provided
    if address_data.firstname:
        address.firstname = address_data.firstname
    if address_data.lastname:
        address.lastname = address_data.lastname
    if address_data.company is not None:
        address.company = address_data.company
    if address_data.address_1:
        address.address_1 = address_data.address_1
    if address_data.address_2 is not None:
        address.address_2 = address_data.address_2
    if address_data.city:
        address.city = address_data.city
    if address_data.postcode:
        address.postcode = address_data.postcode
    if address_data.country_id:
        address.country_id = address_data.country_id
    if address_data.zone_id:
        address.zone_id = address_data.zone_id
    if address_data.custom_field is not None:
        address.custom_field = address_data.custom_field
    
    db.commit()
    db.refresh(address)
    
    return address

@router.delete("/admin/{address_id}", status_code=204)
def admin_delete_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    Delete any address (admin only)
    """
    address = db.query(Address).filter(Address.address_id == address_id).first()
    
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    
    db.delete(address)
    db.commit()
    
    return None