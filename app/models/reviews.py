from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Numeric, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    book_id = Column(Integer, ForeignKey("books.book_id", ondelete="CASCADE"))
    rating = Column(Integer)  # 1-5
    comment = Column(Text, nullable=True)
    date_reviewed = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="reviews")
    book = relationship("Book", back_populates="reviews")

class BookReview(Base):
    __tablename__ = "book_reviews"

    review_id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.book_id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    rating = Column(Numeric(2, 1))  # 1.0-5.0
    review_text = Column(Text, nullable=True)
    review_date = Column(DateTime(timezone=True), server_default=func.now())
    helpful_votes = Column(Integer, default=0)
    verified_purchase = Column(Boolean, default=False)
    source = Column(String(50), default='amazon')
    external_review_id = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    book = relationship("Book", back_populates="book_reviews")
    user = relationship("User", back_populates="book_reviews")
    helpful_votes_rel = relationship("ReviewHelpfulVote", back_populates="review")

class ReviewHelpfulVote(Base):
    __tablename__ = "review_helpful_votes"

    vote_id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("book_reviews.review_id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    is_helpful = Column(Boolean)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    review = relationship("BookReview", back_populates="helpful_votes_rel")
    user = relationship("User", back_populates="helpful_votes")

    __table_args__ = (
        # Ensure a user can only vote once per review
        {'sqlite_autoincrement': True},
    ) 