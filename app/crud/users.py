from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from typing import List, Optional, Dict, Any
from app.models.users import User, Group, Permission
from app.schemas.users import UserCreate, UserUpdate, PasswordUpdate
from fastapi import HTTPException
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def get_users(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    is_verified: Optional[bool] = None
) -> List[User]:
    query = db.query(User)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if is_verified is not None:
        query = query.filter(User.is_verified == is_verified)
    return query.order_by(desc(User.created_at)).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate) -> User:
    # Check if user with email or username already exists
    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already taken")

    # Create new user
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        password_hash=pwd_context.hash(user.password),
        address=user.address,
        phone_number=user.phone_number,
        bio=user.bio,
        birth_date=user.birth_date,
        favorite_genres=user.favorite_genres,
        notification_preferences=user.notification_preferences.dict()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(
    db: Session,
    user_id: int,
    user: UserUpdate
) -> Optional[User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    # Check if new email or username is already taken
    update_data = user.model_dump(exclude_unset=True)
    if 'email' in update_data and update_data['email'] != db_user.email:
        if get_user_by_email(db, update_data['email']):
            raise HTTPException(status_code=400, detail="Email already registered")
    if 'username' in update_data and update_data['username'] != db_user.username:
        if get_user_by_username(db, update_data['username']):
            raise HTTPException(status_code=400, detail="Username already taken")

    # Update user
    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user

def update_password(
    db: Session,
    user_id: int,
    password_update: PasswordUpdate
) -> Optional[User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    # Verify current password
    if not pwd_context.verify(password_update.current_password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    # Update password
    db_user.password_hash = pwd_context.hash(password_update.new_password)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_notification_preferences(
    db: Session,
    user_id: int,
    preferences: Dict[str, bool]
) -> Optional[User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    db_user.notification_preferences = preferences
    db.commit()
    db.refresh(db_user)
    return db_user

def update_favorite_genres(
    db: Session,
    user_id: int,
    genres: List[str]
) -> Optional[User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    db_user.favorite_genres = genres
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_email(db: Session, email: str, token: str) -> Optional[User]:
    # This is a placeholder for email verification logic
    # In a real implementation, this would verify the token
    db_user = get_user_by_email(db, email)
    if not db_user:
        return None

    # Add your token verification logic here
    # For now, just mark the user as verified
    db_user.is_verified = True
    db.commit()
    db.refresh(db_user)
    return db_user

def deactivate_user(db: Session, user_id: int) -> Optional[User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    db_user.is_active = False
    db.commit()
    db.refresh(db_user)
    return db_user

def activate_user(db: Session, user_id: int) -> Optional[User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    db_user.is_active = True
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_groups(db: Session, user_id: int) -> List[Group]:
    db_user = get_user(db, user_id)
    if not db_user:
        return []
    return db_user.groups

def get_user_permissions(db: Session, user_id: int) -> List[Permission]:
    db_user = get_user(db, user_id)
    if not db_user:
        return []
    return db_user.permissions

def add_user_to_group(db: Session, user_id: int, group_id: int) -> Optional[User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    if group not in db_user.groups:
        db_user.groups.append(group)
        db.commit()
        db.refresh(db_user)
    return db_user

def remove_user_from_group(db: Session, user_id: int, group_id: int) -> Optional[User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    if group in db_user.groups:
        db_user.groups.remove(group)
        db.commit()
        db.refresh(db_user)
    return db_user

def add_user_permission(db: Session, user_id: int, permission_id: int) -> Optional[User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    if permission not in db_user.permissions:
        db_user.permissions.append(permission)
        db.commit()
        db.refresh(db_user)
    return db_user

def remove_user_permission(db: Session, user_id: int, permission_id: int) -> Optional[User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    if permission in db_user.permissions:
        db_user.permissions.remove(permission)
        db.commit()
        db.refresh(db_user)
    return db_user

def get_user_stats(db: Session, user_id: int) -> Dict[str, Any]:
    db_user = get_user(db, user_id)
    if not db_user:
        return {}

    # Get user's orders
    orders = db_user.orders
    total_orders = len(orders)
    active_borrows = len([o for o in orders if o.status == "BORROWED"])
    completed_purchases = len([o for o in orders if o.status == "PURCHASED"])

    # Get user's reviews
    reviews = db_user.reviews
    total_reviews = len(reviews)
    average_rating = sum(r.rating for r in reviews) / total_reviews if total_reviews > 0 else 0

    # Get user's transactions
    transactions = db_user.transactions
    total_transactions = len(transactions)
    total_spent = sum(t.total_amount for t in transactions if t.status == "DELIVERED")

    return {
        "total_orders": total_orders,
        "active_borrows": active_borrows,
        "completed_purchases": completed_purchases,
        "total_reviews": total_reviews,
        "average_rating": average_rating,
        "total_transactions": total_transactions,
        "total_spent": total_spent
    }

# Group operations
def get_group(db: Session, group_id: int) -> Optional[Group]:
    return db.query(Group).filter(Group.id == group_id).first()

def get_groups(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[Group]:
    return db.query(Group).offset(skip).limit(limit).all()

def create_group(db: Session, name: str, description: Optional[str] = None) -> Group:
    db_group = Group(name=name, description=description)
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

def delete_user(db: Session, user_id: int) -> bool:
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True

def verify_user_email(db: Session, user_id: int) -> Optional[User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    db_user.is_verified = True
    db.commit()
    db.refresh(db_user)
    return db_user 