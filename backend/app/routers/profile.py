from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.profile import Profile as ProfileSchema, ProfileUpdate
from app.services.auth_service import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.get("/me", response_model=ProfileSchema)
def read_profile_me(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get current user profile.
    """
    return current_user.profile

@router.put("/me", response_model=ProfileSchema)
def update_profile_me(
    *,
    db: Session = Depends(get_db),
    profile_in: ProfileUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update current user profile.
    """
    profile = current_user.profile
    update_data = profile_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(profile, field, value)
        
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile
