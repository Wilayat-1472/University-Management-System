from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate
from app.services.user_service import get_user, get_users, create_user, update_user
from app.middleware.rbac import RoleChecker
from app.models.user import User

router = APIRouter()

# Only admins can access these routes
admin_only = RoleChecker(["Admin"])

@router.get("/", response_model=List[UserSchema], dependencies=[Depends(admin_only)])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve users.
    """
    users = get_users(db, skip=skip, limit=limit)
    return users

@router.post("/", response_model=UserSchema, dependencies=[Depends(admin_only)])
def create_user_admin(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    Create new user.
    """
    user = create_user(db, user=user_in)
    return user

@router.put("/{user_id}", response_model=UserSchema, dependencies=[Depends(admin_only)])
def update_user_admin(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    user_in: UserUpdate,
) -> Any:
    """
    Update a user.
    """
    user = get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user = update_user(db, db_user=user, user_in=user_in)
    return user

@router.delete("/{user_id}", response_model=UserSchema, dependencies=[Depends(admin_only)])
def delete_user_admin(
    *,
    db: Session = Depends(get_db),
    user_id: int,
) -> Any:
    """
    Delete a user.
    """
    user = get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return user
