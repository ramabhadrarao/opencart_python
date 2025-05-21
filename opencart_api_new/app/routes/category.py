from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from datetime import datetime

from app.database import get_db
from app.models.category import Category, CategoryDescription
from app.schemas.category import CategoryInList, CategoryDetail, CategoryCreate, CategoryUpdate
from app.utils.auth import get_current_admin  # Add this import

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
    responses={404: {"description": "Category not found"}},
)

@router.get("/", response_model=List[CategoryInList])
def get_categories(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """
    Get list of categories
    """
    categories = db.query(Category).options(
        joinedload(Category.descriptions)
    ).offset(skip).limit(limit).all()
    
    result = []
    for category in categories:
        if category.descriptions:
            description = category.descriptions[0]  # Get first description (usually default language)
            result.append({
                "category_id": category.category_id,
                "name": description.name,
                "parent_id": category.parent_id,
                "sort_order": category.sort_order,
                "status": category.status,
            })
    
    return result

@router.get("/{category_id}", response_model=CategoryDetail)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific category
    """
    category = db.query(Category).options(
        joinedload(Category.descriptions)
    ).filter(Category.category_id == category_id).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return category

@router.post("/", response_model=CategoryDetail, status_code=201)
def create_category(
    category_data: CategoryCreate, 
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)  # Add admin authentication
):
    """
    Create a new category
    """
    new_category = Category(
        parent_id=category_data.parent_id,
        top=category_data.top,
        column=category_data.column,
        sort_order=category_data.sort_order,
        status=category_data.status,
        image=category_data.image,
        date_added=datetime.now(),
        date_modified=datetime.now()
    )
    
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    
    # Add descriptions
    for desc in category_data.descriptions:
        db.add(CategoryDescription(
            category_id=new_category.category_id,
            language_id=desc.language_id,
            name=desc.name,
            description=desc.description,
            meta_title=desc.meta_title,
            meta_description=desc.meta_description,
            meta_keyword=desc.meta_keyword
        ))
    
    db.commit()
    db.refresh(new_category)
    
    return new_category

@router.put("/{category_id}", response_model=CategoryDetail)
def update_category(
    category_id: int, 
    category_data: CategoryUpdate, 
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)  # Add admin authentication
):
    """
    Update a category
    """
    category = db.query(Category).filter(Category.category_id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Update category fields if provided
    if category_data.parent_id is not None:
        category.parent_id = category_data.parent_id
    if category_data.status is not None:
        category.status = category_data.status
    if category_data.sort_order is not None:
        category.sort_order = category_data.sort_order
    if category_data.image is not None:
        category.image = category_data.image
    
    category.date_modified = datetime.now()
    
    # Update descriptions if provided
    if category_data.descriptions:
        # Delete existing descriptions
        db.query(CategoryDescription).filter(
            CategoryDescription.category_id == category_id
        ).delete()
        
        # Add new descriptions
        for desc in category_data.descriptions:
            db.add(CategoryDescription(
                category_id=category_id,
                language_id=desc.language_id,
                name=desc.name,
                description=desc.description,
                meta_title=desc.meta_title,
                meta_description=desc.meta_description,
                meta_keyword=desc.meta_keyword
            ))
    
    db.commit()
    db.refresh(category)
    
    return category

@router.delete("/{category_id}", status_code=204)
def delete_category(
    category_id: int, 
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)  # Add admin authentication
):
    """
    Delete a category
    """
    category = db.query(Category).filter(Category.category_id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Delete related records
    db.query(CategoryDescription).filter(CategoryDescription.category_id == category_id).delete()
    
    # Delete the category itself
    db.delete(category)
    db.commit()
    
    return None