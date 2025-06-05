from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
from datetime import datetime
from decimal import Decimal

class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    book_id: int

class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None

class Review(ReviewBase):
    id: int
    user_id: int
    book_id: int
    date_reviewed: datetime

    class Config:
        from_attributes = True

class BookReviewBase(BaseModel):
    rating: Decimal = Field(..., ge=1, le=5, decimal_places=1)
    review_text: Optional[str] = None
    verified_purchase: bool = False
    source: str = "amazon"
    external_review_id: Optional[str] = None

class BookReviewCreate(BookReviewBase):
    book_id: int

class BookReviewUpdate(BaseModel):
    rating: Optional[Decimal] = Field(None, ge=1, le=5, decimal_places=1)
    review_text: Optional[str] = None
    verified_purchase: Optional[bool] = None
    source: Optional[str] = None
    external_review_id: Optional[str] = None

class BookReview(BookReviewBase):
    review_id: int
    user_id: int
    book_id: int
    review_date: datetime
    helpful_votes: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ReviewHelpfulVoteBase(BaseModel):
    is_helpful: bool

class ReviewHelpfulVoteCreate(ReviewHelpfulVoteBase):
    review_id: int

class ReviewHelpfulVote(ReviewHelpfulVoteBase):
    vote_id: int
    review_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class SentimentAnalysis(BaseModel):
    sentiment: float
    interpretation: str
    review_id: int
    book_title: str

class BookSentimentStats(BaseModel):
    book_id: int
    total_reviews: int
    reviews_with_comments: int
    average_sentiment: float
    sentiment_stats: Dict[str, int]
    interpretation: str

class ReviewStats(BaseModel):
    total_reviews: int
    average_rating: float
    rating_distribution: Dict[str, int] 