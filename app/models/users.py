from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, Date, JSON, ARRAY, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from passlib.context import CryptContext
from typing import List

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Association tables for many-to-many relationships
user_groups = Table(
    'user_groups',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE')),
    Column('group_id', Integer, ForeignKey('groups.id', ondelete='CASCADE'))
)

user_permissions = Table(
    'user_permissions',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE')),
    Column('permission_id', Integer, ForeignKey('permissions.id', ondelete='CASCADE'))
)

class Group(Base):
    """Represents a user group."""
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    users = relationship("User", secondary=user_groups, back_populates="groups")

class Permission(Base):
    """Represents a user permission."""
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True)
    codename = Column(String(100), unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    users = relationship("User", secondary=user_permissions, back_populates="permissions")

class User(Base):
    """Custom user model that matches our database schema."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    full_name = Column(String(100))
    password_hash = Column(String(255))
    is_admin = Column(Boolean, default=False)
    is_staff = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    address = Column(Text, nullable=True)
    phone_number = Column(String(20), nullable=True)
    profile_picture = Column(String(255), nullable=True)  # Store file path
    bio = Column(Text, nullable=True)
    birth_date = Column(Date, nullable=True)
    favorite_genres = Column(JSON, default=list)
    notification_preferences = Column(JSON, default=dict)
    is_verified = Column(Boolean, default=False)
    last_active = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    groups = relationship("Group", secondary=user_groups, back_populates="users")
    permissions = relationship("Permission", secondary=user_permissions, back_populates="users")
    orders = relationship("Order", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    activities = relationship("UserActivity", back_populates="user")

    def __repr__(self):
        return f"<User {self.email}>"

    def verify_password(self, plain_password: str) -> bool:
        return pwd_context.verify(plain_password, self.password_hash)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password) 