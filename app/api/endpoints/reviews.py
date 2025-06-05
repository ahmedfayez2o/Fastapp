from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from app.core.deps import get_db
from app.core.auth import get_current_user, get_current_active_user
from app.models.users import User
from app.models.reviews import Review, BookReview
from app.schemas.reviews import (
    Review as ReviewSchema,
    ReviewCreate,
    ReviewUpdate,
    BookReview as BookReviewSchema,
    BookReviewCreate,
    BookReviewUpdate,
    ReviewHelpfulVoteCreate,
    ReviewHelpfulVote as ReviewHelpfulVoteSchema,
    SentimentAnalysis,
    BookSentimentStats,
    ReviewStats
)
from app.crud import reviews as crud_reviews
from app.services.sentiment_analyzer import SentimentAnalyzer

router = APIRouter()
sentiment_analyzer = SentimentAnalyzer()

# Review endpoints
@router.post("/", response_model=ReviewSchema)
def create_review(
    review: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new review.
    """
    try:
        return crud_reviews.create_review(db, review, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[ReviewSchema])
def get_reviews(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    book_id: Optional[int] = None,
    user_id: Optional[int] = None,
    rating: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    verified_only: bool = False,
    has_comment: bool = False,
    current_user: User = Depends(get_current_user)
):
    """
    Get a list of reviews with optional filtering.
    """
    return crud_reviews.get_reviews(
        db,
        skip=skip,
        limit=limit,
        book_id=book_id,
        user_id=user_id,
        rating=rating,
        start_date=start_date,
        end_date=end_date,
        verified_only=verified_only,
        has_comment=has_comment
    )

@router.get("/{review_id}", response_model=ReviewSchema)
def get_review(
    review_id: int = Path(..., title="The ID of the review to get"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific review by ID.
    """
    review = crud_reviews.get_review(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review

@router.put("/{review_id}", response_model=ReviewSchema)
def update_review(
    review_id: int = Path(..., title="The ID of the review to update"),
    review: ReviewUpdate = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a review.
    """
    updated_review = crud_reviews.update_review(db, review_id, review, current_user.id)
    if not updated_review:
        raise HTTPException(status_code=404, detail="Review not found or unauthorized")
    return updated_review

@router.delete("/{review_id}")
def delete_review(
    review_id: int = Path(..., title="The ID of the review to delete"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a review.
    """
    if not crud_reviews.delete_review(db, review_id, current_user.id):
        raise HTTPException(status_code=404, detail="Review not found or unauthorized")
    return {"message": "Review deleted successfully"}

# Book review endpoints
@router.post("/books/", response_model=BookReviewSchema)
def create_book_review(
    review: BookReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new book review.
    """
    try:
        return crud_reviews.create_book_review(db, review, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/books/", response_model=List[BookReviewSchema])
def get_book_reviews(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    book_id: Optional[int] = None,
    user_id: Optional[int] = None,
    min_rating: Optional[Decimal] = None,
    max_rating: Optional[Decimal] = None,
    verified_only: bool = False,
    source: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    sort_by: str = Query("date", regex="^(date|rating|helpful)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    current_user: User = Depends(get_current_user)
):
    """
    Get a list of book reviews with optional filtering and sorting.
    """
    return crud_reviews.get_book_reviews(
        db,
        skip=skip,
        limit=limit,
        book_id=book_id,
        user_id=user_id,
        min_rating=min_rating,
        max_rating=max_rating,
        verified_only=verified_only,
        source=source,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        sort_order=sort_order
    )

@router.get("/books/{review_id}", response_model=BookReviewSchema)
def get_book_review(
    review_id: int = Path(..., title="The ID of the book review to get"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific book review by ID.
    """
    review = crud_reviews.get_book_review(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Book review not found")
    return review

@router.put("/books/{review_id}", response_model=BookReviewSchema)
def update_book_review(
    review_id: int = Path(..., title="The ID of the book review to update"),
    review: BookReviewUpdate = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a book review.
    """
    updated_review = crud_reviews.update_book_review(db, review_id, review, current_user.id)
    if not updated_review:
        raise HTTPException(status_code=404, detail="Book review not found or unauthorized")
    return updated_review

@router.delete("/books/{review_id}")
def delete_book_review(
    review_id: int = Path(..., title="The ID of the book review to delete"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a book review.
    """
    if not crud_reviews.delete_book_review(db, review_id, current_user.id):
        raise HTTPException(status_code=404, detail="Book review not found or unauthorized")
    return {"message": "Book review deleted successfully"}

# Review helpful votes
@router.post("/books/{review_id}/vote", response_model=ReviewHelpfulVoteSchema)
def vote_review(
    review_id: int = Path(..., title="The ID of the book review to vote on"),
    vote: ReviewHelpfulVoteCreate = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Vote on whether a review is helpful.
    """
    if vote.review_id != review_id:
        raise HTTPException(status_code=400, detail="Review ID mismatch")
    
    db_vote = crud_reviews.vote_review(db, vote, current_user.id)
    if not db_vote:
        raise HTTPException(status_code=404, detail="Book review not found")
    return db_vote

# Review statistics
@router.get("/stats", response_model=ReviewStats)
def get_review_stats(
    book_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get review statistics, optionally filtered by book.
    """
    return crud_reviews.get_review_stats(db, book_id)

@router.get("/books/{book_id}/stats", response_model=BookSentimentStats)
def get_book_review_stats(
    book_id: int = Path(..., title="The ID of the book to get review stats for"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed review statistics for a specific book.
    """
    try:
        return crud_reviews.get_book_review_stats(db, book_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Sentiment analysis
@router.get("/books/{review_id}/sentiment", response_model=SentimentAnalysis)
def analyze_review_sentiment(
    review_id: int = Path(..., title="The ID of the book review to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze the sentiment of a specific review.
    """
    review = crud_reviews.get_book_review(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Book review not found")
    
    sentiment = sentiment_analyzer.analyze_sentiment(review.review_text or "")
    interpretation = sentiment_analyzer.get_sentiment_interpretation(sentiment)
    
    return {
        "review_id": review_id,
        "book_title": review.book.title,
        "sentiment": sentiment,
        "interpretation": interpretation
    }

@router.get("/books/{book_id}/sentiment/stats", response_model=BookSentimentStats)
def analyze_book_reviews_sentiment(
    book_id: int = Path(..., title="The ID of the book to analyze reviews for"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze the sentiment of all reviews for a specific book.
    """
    reviews = crud_reviews.get_book_reviews(db, book_id=book_id)
    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews found for this book")
    
    # Prepare reviews for analysis
    review_data = [(r.review_id, r.book.title, r.review_text or "") for r in reviews]
    analysis_results = sentiment_analyzer.analyze_reviews(review_data)
    stats = sentiment_analyzer.get_sentiment_stats(analysis_results)
    
    return {
        "book_id": book_id,
        "book_title": reviews[0].book.title,
        **stats
    }

# Special review lists
@router.get("/recent", response_model=List[BookReviewSchema])
def get_recent_reviews(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the most recent reviews.
    """
    return crud_reviews.get_recent_reviews(db, limit)

@router.get("/top-rated", response_model=List[BookReviewSchema])
def get_top_rated_reviews(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the highest rated reviews.
    """
    return crud_reviews.get_top_rated_reviews(db, limit)

@router.get("/helpful", response_model=List[BookReviewSchema])
def get_helpful_reviews(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the most helpful reviews.
    """
    return crud_reviews.get_helpful_reviews(db, limit)

@router.get("/me", response_model=List[BookReviewSchema])
def get_my_reviews(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the current user's reviews.
    """
    return crud_reviews.get_user_reviews(db, current_user.id, skip, limit) 