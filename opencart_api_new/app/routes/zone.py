from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.zone import Zone
from app.schemas.zone import Zone as ZoneSchema, ZoneCreate, ZoneUpdate
from app.utils.auth import get_current_admin

router = APIRouter(
    prefix="/zones",
    tags=["zones"],
    responses={404: {"description": "Zone not found"}},
)

@router.get("/", response_model=List[ZoneSchema])
def get_zones(
    db: Session = Depends(get_db),
    country_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    status: Optional[bool] = True
):
    """
    Get list of zones with optional country and status filters
    """
    query = db.query(Zone)
    
    if country_id:
        query = query.filter(Zone.country_id == country_id)
    
    if status is not None:
        query = query.filter(Zone.status == status)
    
    zones = query.offset(skip).limit(limit).all()
    return zones

@router.get("/{zone_id}", response_model=ZoneSchema)
def get_zone(zone_id: int, db: Session = Depends(get_db)):
    """
    Get a specific zone by ID
    """
    zone = db.query(Zone).filter(Zone.zone_id == zone_id).first()
    
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    
    return zone

@router.post("/", response_model=ZoneSchema)
def create_zone(
    zone_data: ZoneCreate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    Create a new zone (admin only)
    """
    db_zone = Zone(
        country_id=zone_data.country_id,
        name=zone_data.name,
        code=zone_data.code,
        status=zone_data.status
    )
    
    db.add(db_zone)
    db.commit()
    db.refresh(db_zone)
    
    return db_zone

@router.put("/{zone_id}", response_model=ZoneSchema)
def update_zone(
    zone_id: int,
    zone_data: ZoneUpdate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    Update a zone (admin only)
    """
    zone = db.query(Zone).filter(Zone.zone_id == zone_id).first()
    
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    
    # Update fields if provided
    if zone_data.country_id:
        zone.country_id = zone_data.country_id
    if zone_data.name:
        zone.name = zone_data.name
    if zone_data.code:
        zone.code = zone_data.code
    if zone_data.status is not None:
        zone.status = zone_data.status
    
    db.commit()
    db.refresh(zone)
    
    return zone

@router.delete("/{zone_id}", status_code=204)
def delete_zone(
    zone_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    Delete a zone (admin only)
    """
    zone = db.query(Zone).filter(Zone.zone_id == zone_id).first()
    
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    
    db.delete(zone)
    db.commit()
    
    return None