from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

# Association table for recommendations and books
recommendation_books = Table(
    'recommendation_books',
    Base.metadata,
    Column('recommendation_id', Integer, ForeignKey('recommendations.recommendation_id', ondelete='CASCADE')),
    Column('book_id', Integer, ForeignKey('books.book_id', ondelete='CASCADE'))
)

class UserActivity(Base):
    """
    Tracks user interactions with books including views and favorites.
    """
    __tablename__ = "user_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    book_id = Column(Integer, ForeignKey("books.book_id", ondelete="CASCADE"))
    view_count = Column(Integer, default=0)
    last_viewed = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_favorite = Column(Boolean, default=False)
    interaction_score = Column(Float, default=0)  # Calculated based on user interactions

    # Relationships
    user = relationship("User", back_populates="activities")
    book = relationship("Book", back_populates="user_activities")

    __table_args__ = (
        # Ensure a user can only have one activity record per book
        {'sqlite_autoincrement': True},
    )

class Recommendation(Base):
    """
    Stores book recommendations for users.
    """
    __tablename__ = "recommendations"

    recommendation_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    date_generated = Column(DateTime(timezone=True), server_default=func.now())
    recommendation_type = Column(String(20))  # PERSONALIZED, TRENDING, SIMILAR, GENRE
    is_active = Column(Boolean, default=True)
    source_book_id = Column(Integer, ForeignKey("books.book_id", ondelete="SET NULL"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="recommendations")
    source_book = relationship("Book", foreign_keys=[source_book_id], back_populates="source_recommendations")
    items = relationship("RecommendationItem", back_populates="recommendation", cascade="all, delete-orphan")

    __table_args__ = (
        # Ensure a user can only have one active recommendation of each type
        {'sqlite_autoincrement': True},
    )

class RecommendationItem(Base):
    """
    Represents a single book in a recommendation set.
    """
    __tablename__ = "recommendation_items"

    item_id = Column(Integer, primary_key=True, index=True)
    recommendation_id = Column(Integer, ForeignKey("recommendations.recommendation_id", ondelete="CASCADE"))
    book_id = Column(Integer, ForeignKey("books.book_id", ondelete="CASCADE"))
    relevance_score = Column(Float)  # How relevant this recommendation is (0-1)
    position = Column(Integer)  # Position in the recommendation list
    reason = Column(Text, nullable=True)  # Why this book was recommended

    # Relationships
    recommendation = relationship("Recommendation", back_populates="items")
    book = relationship("Book", back_populates="recommendation_items")

    __table_args__ = (
        # Ensure a book can only appear once in a recommendation set
        {'sqlite_autoincrement': True},
    )

class ModelData(Base):
    """
    Stores ML model data in the database.
    """
    __tablename__ = "model_data"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True)
    version = Column(Integer, default=1)
    data = Column(JSON)  # Store model data as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        # Ensure model names are unique
        {'sqlite_autoincrement': True},
    ) 