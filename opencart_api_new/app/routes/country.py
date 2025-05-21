from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.country import Country
from app.schemas.country import Country as CountrySchema, CountryCreate, CountryUpdate
from app.utils.auth import get_current_admin

router = APIRouter(
    prefix="/countries",
    tags=["countries"],
    responses={404: {"description": "Country not found"}},
)

@router.get("/", response_model=List[CountrySchema])
def get_countries(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[bool] = True
):
    """
    Get list of countries with optional status filter
    """
    query = db.query(Country)
    
    if status is not None:
        query = query.filter(Country.status == status)
    
    countries = query.offset(skip).limit(limit).all()
    return countries

@router.get("/{country_id}", response_model=CountrySchema)
def get_country(country_id: int, db: Session = Depends(get_db)):
    """
    Get a specific country by ID
    """
    country = db.query(Country).filter(Country.country_id == country_id).first()
    
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    
    return country

@router.post("/", response_model=CountrySchema)
def create_country(
    country_data: CountryCreate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    Create a new country (admin only)
    """
    db_country = Country(
        name=country_data.name,
        iso_code_2=country_data.iso_code_2,
        iso_code_3=country_data.iso_code_3,
        address_format=country_data.address_format,
        postcode_required=country_data.postcode_required,
        status=country_data.status
    )
    
    db.add(db_country)
    db.commit()
    db.refresh(db_country)
    
    return db_country

@router.put("/{country_id}", response_model=CountrySchema)
def update_country(
    country_id: int,
    country_data: CountryUpdate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    Update a country (admin only)
    """
    country = db.query(Country).filter(Country.country_id == country_id).first()
    
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    
    # Update fields if provided
    if country_data.name:
        country.name = country_data.name
    if country_data.iso_code_2:
        country.iso_code_2 = country_data.iso_code_2
    if country_data.iso_code_3:
        country.iso_code_3 = country_data.iso_code_3
    if country_data.address_format is not None:
        country.address_format = country_data.address_format
    if country_data.postcode_required is not None:
        country.postcode_required = country_data.postcode_required
    if country_data.status is not None:
        country.status = country_data.status
    
    db.commit()
    db.refresh(country)
    
    return country

@router.delete("/{country_id}", status_code=204)
def delete_country(
    country_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    Delete a country (admin only)
    """
    country = db.query(Country).filter(Country.country_id == country_id).first()
    
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    
    db.delete(country)
    db.commit()
    
    return None