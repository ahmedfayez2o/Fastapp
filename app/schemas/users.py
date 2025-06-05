from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum

class NotificationChannel(str, Enum):
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"

class NotificationPreferences(BaseModel):
    email: bool = True
    push: bool = True
    sms: bool = False

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    address: Optional[str] = None
    phone_number: Optional[str] = None
    bio: Optional[str] = None
    birth_date: Optional[date] = None
    favorite_genres: List[str] = Field(default_factory=list)
    notification_preferences: NotificationPreferences = Field(default_factory=NotificationPreferences)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)

    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('passwords do not match')
        return v

    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v is not None:
            # Remove any non-digit characters
            digits = ''.join(filter(str.isdigit, v))
            if len(digits) < 10:
                raise ValueError('phone number must have at least 10 digits')
        return v

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    address: Optional[str] = None
    phone_number: Optional[str] = None
    bio: Optional[str] = None
    birth_date: Optional[date] = None
    favorite_genres: Optional[List[str]] = None
    notification_preferences: Optional[NotificationPreferences] = None

    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v is not None:
            digits = ''.join(filter(str.isdigit, v))
            if len(digits) < 10:
                raise ValueError('phone number must have at least 10 digits')
        return v

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)

    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('passwords do not match')
        return v

class User(UserBase):
    id: int
    is_admin: bool
    is_staff: bool
    is_superuser: bool
    is_active: bool
    is_verified: bool
    profile_picture: Optional[str] = None
    last_active: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserInDB(User):
    password_hash: str

class UserResponse(User):
    """Extended user response with additional data"""
    groups: List[Dict[str, Any]] = Field(default_factory=list)
    permissions: List[Dict[str, Any]] = Field(default_factory=list)

class GroupBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = None

class GroupCreate(GroupBase):
    pass

class GroupUpdate(GroupBase):
    pass

class Group(GroupBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PermissionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    codename: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None

class PermissionCreate(PermissionBase):
    pass

class PermissionUpdate(PermissionBase):
    pass

class Permission(PermissionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []

class EmailVerification(BaseModel):
    email: EmailStr
    token: str 