from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.auth import (
    get_current_user,
    get_current_active_user,
    get_current_active_superuser,
    create_access_token,
)
from app.core.config import settings
from app.core.deps import get_db
from app.crud import users as crud
from app.schemas.users import (
    User,
    UserCreate,
    UserUpdate,
    UserResponse,
    PasswordUpdate,
    Token,
    EmailVerification,
    Group,
    GroupCreate,
    GroupUpdate,
    Permission,
    PermissionCreate,
    PermissionUpdate
)

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user."""
    return crud.create_user(db=db, user=user)

@router.post("/login", response_model=Token)
def login(
    email: str,
    password: str,
    db: Session = Depends(get_db)
):
    """Login user and return access token."""
    user = crud.get_user_by_email(db, email)
    if not user or not user.verify_password(password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def read_users_me(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user."""
    return current_user

@router.put("/me", response_model=UserResponse)
def update_user_me(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user."""
    return crud.update_user(db=db, user_id=current_user.id, user=user_in)

@router.put("/me/password", response_model=UserResponse)
def update_password_me(
    password_in: PasswordUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user's password."""
    return crud.update_password(
        db=db,
        user_id=current_user.id,
        password_update=password_in
    )

@router.post("/verify-email", response_model=UserResponse)
def verify_email(
    verification: EmailVerification,
    db: Session = Depends(get_db)
):
    """Verify user's email."""
    return crud.verify_email(
        db=db,
        email=verification.email,
        token=verification.token
    )

@router.get("/stats", response_model=dict)
def read_user_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's statistics."""
    return crud.get_user_stats(db=db, user_id=current_user.id)

# Admin endpoints
@router.get("/", response_model=List[UserResponse])
def read_users(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    is_verified: Optional[bool] = None,
    current_user: User = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
):
    """Get all users. Admin only."""
    return crud.get_users(
        db=db,
        skip=skip,
        limit=limit,
        is_active=is_active,
        is_verified=is_verified
    )

@router.get("/{user_id}", response_model=UserResponse)
def read_user(
    user_id: int,
    current_user: User = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
):
    """Get user by ID. Admin only."""
    user = crud.get_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
):
    """Update user. Admin only."""
    user = crud.get_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.update_user(db=db, user_id=user_id, user=user_in)

@router.delete("/{user_id}", response_model=bool)
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
):
    """Delete user. Admin only."""
    user = crud.get_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.delete_user(db=db, user_id=user_id)

@router.post("/{user_id}/activate", response_model=UserResponse)
def activate_user(
    user_id: int,
    current_user: User = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
):
    """Activate user. Admin only."""
    user = crud.get_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.activate_user(db=db, user_id=user_id)

@router.post("/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(
    user_id: int,
    current_user: User = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
):
    """Deactivate user. Admin only."""
    user = crud.get_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.deactivate_user(db=db, user_id=user_id)

# Group endpoints
@router.get("/groups/", response_model=List[Group])
def read_groups(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
):
    """Get all groups. Admin only."""
    return crud.get_groups(db=db, skip=skip, limit=limit)

@router.post("/groups/", response_model=Group)
def create_group(
    group_in: GroupCreate,
    current_user: User = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
):
    """Create new group. Admin only."""
    return crud.create_group(db=db, group=group_in)

@router.get("/groups/{group_id}", response_model=Group)
def read_group(
    group_id: int,
    current_user: User = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
):
    """Get group by ID. Admin only."""
    group = crud.get_group(db=db, group_id=group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group

@router.put("/groups/{group_id}", response_model=Group)
def update_group(
    group_id: int,
    group_in: GroupUpdate,
    current_user: User = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
):
    """Update group. Admin only."""
    group = crud.get_group(db=db, group_id=group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return crud.update_group(db=db, group_id=group_id, group=group_in)

@router.delete("/groups/{group_id}", response_model=bool)
def delete_group(
    group_id: int,
    current_user: User = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
):
    """Delete group. Admin only."""
    group = crud.get_group(db=db, group_id=group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return crud.delete_group(db=db, group_id=group_id)

@router.post("/{user_id}/groups/{group_id}", response_model=UserResponse)
def add_user_to_group(
    user_id: int,
    group_id: int,
    current_user: User = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
):
    """Add user to group. Admin only."""
    return crud.add_user_to_group(db=db, user_id=user_id, group_id=group_id)

@router.delete("/{user_id}/groups/{group_id}", response_model=UserResponse)
def remove_user_from_group(
    user_id: int,
    group_id: int,
    current_user: User = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
):
    """Remove user from group. Admin only."""
    return crud.remove_user_from_group(db=db, user_id=user_id, group_id=group_id)

# Permission endpoints
@router.get("/permissions/", response_model=List[Permission])
def read_permissions(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
):
    """Get all permissions. Admin only."""
    return crud.get_permissions(db=db, skip=skip, limit=limit)

@router.post("/permissions/", response_model=Permission)
def create_permission(
    permission_in: PermissionCreate,
    current_user: User = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
):
    """Create new permission. Admin only."""
    return crud.create_permission(db=db, permission=permission_in)

@router.get("/permissions/{permission_id}", response_model=Permission)
def read_permission(
    permission_id: int,
    current_user: User = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
):
    """Get permission by ID. Admin only."""
    permission = crud.get_permission(db=db, permission_id=permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return permission

@router.put("/permissions/{permission_id}", response_model=Permission)
def update_permission(
    permission_id: int,
    permission_in: PermissionUpdate,
    current_user: User = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
):
    """Update permission. Admin only."""
    permission = crud.get_permission(db=db, permission_id=permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return crud.update_permission(db=db, permission_id=permission_id, permission=permission_in)

@router.delete("/permissions/{permission_id}", response_model=bool)
def delete_permission(
    permission_id: int,
    current_user: User = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
):
    """Delete permission. Admin only."""
    permission = crud.get_permission(db=db, permission_id=permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return crud.delete_permission(db=db, permission_id=permission_id)

@router.post("/{user_id}/permissions/{permission_id}", response_model=UserResponse)
def add_user_permission(
    user_id: int,
    permission_id: int,
    current_user: User = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
):
    """Add permission to user. Admin only."""
    return crud.add_user_permission(db=db, user_id=user_id, permission_id=permission_id)

@router.delete("/{user_id}/permissions/{permission_id}", response_model=UserResponse)
def remove_user_permission(
    user_id: int,
    permission_id: int,
    current_user: User = Depends(get_current_active_superuser),
    db: Session = Depends(get_db)
):
    """Remove permission from user. Admin only."""
    return crud.remove_user_permission(db=db, user_id=user_id, permission_id=permission_id) 