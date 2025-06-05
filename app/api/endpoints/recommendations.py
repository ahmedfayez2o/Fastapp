from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.auth import get_current_user
from app.crud import recommendations as crud_recommendations
from app.schemas.recommendations import (
    UserActivity,
    UserActivityCreate,
    UserActivityUpdate,
    Recommendation,
    RecommendationCreate,
    RecommendationUpdate,
    RecommendationResponse,
    TrendingBook,
    RecommendationRequest
)
from app.services.recommender import HybridRecommender
from app.crud import books as crud_books

router = APIRouter()

@router.post("/activities/", response_model=UserActivity)
def create_user_activity(
    *,
    db: Session = Depends(get_db),
    activity: UserActivityCreate,
    current_user = Depends(get_current_user)
) -> UserActivity:
    """Create a new user activity record."""
    return crud_recommendations.create_user_activity(
        db=db,
        user_id=current_user.id,
        activity=activity
    )

@router.put("/activities/{book_id}", response_model=UserActivity)
def update_user_activity(
    *,
    db: Session = Depends(get_db),
    book_id: int,
    activity: UserActivityUpdate,
    current_user = Depends(get_current_user)
) -> UserActivity:
    """Update a user's activity for a book."""
    db_activity = crud_recommendations.update_user_activity(
        db=db,
        user_id=current_user.id,
        book_id=book_id,
        activity=activity
    )
    if not db_activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return db_activity

@router.post("/activities/{book_id}/view", response_model=UserActivity)
def record_book_view(
    *,
    db: Session = Depends(get_db),
    book_id: int,
    current_user = Depends(get_current_user)
) -> UserActivity:
    """Record a book view for the current user."""
    # Verify book exists
    if not crud_books.get_book(db, book_id=book_id):
        raise HTTPException(status_code=404, detail="Book not found")
    
    return crud_recommendations.record_book_view(
        db=db,
        user_id=current_user.id,
        book_id=book_id
    )

@router.post("/activities/{book_id}/favorite", response_model=UserActivity)
def toggle_favorite(
    *,
    db: Session = Depends(get_db),
    book_id: int,
    current_user = Depends(get_current_user)
) -> UserActivity:
    """Toggle favorite status for a book."""
    # Verify book exists
    if not crud_books.get_book(db, book_id=book_id):
        raise HTTPException(status_code=404, detail="Book not found")
    
    return crud_recommendations.toggle_favorite(
        db=db,
        user_id=current_user.id,
        book_id=book_id
    )

@router.get("/activities/", response_model=List[UserActivity])
def get_user_activities(
    *,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    favorite_only: bool = False
) -> List[UserActivity]:
    """Get user's activity history."""
    return crud_recommendations.get_user_activities(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        favorite_only=favorite_only
    )

@router.post("/recommendations/", response_model=RecommendationResponse)
def create_recommendation(
    *,
    db: Session = Depends(get_db),
    recommendation: RecommendationCreate,
    current_user = Depends(get_current_user)
) -> RecommendationResponse:
    """Create a new recommendation set."""
    db_recommendation = crud_recommendations.create_recommendation(
        db=db,
        user_id=current_user.id,
        recommendation=recommendation
    )
    
    # Get book details for each recommendation item
    books = []
    for item in db_recommendation.items:
        book = crud_books.get_book(db, book_id=item.book_id)
        if book:
            books.append({
                **book.__dict__,
                "relevance_score": item.relevance_score,
                "reason": item.reason
            })
    
    return RecommendationResponse(
        recommendation=db_recommendation,
        books=books
    )

@router.get("/recommendations/", response_model=List[RecommendationResponse])
def get_user_recommendations(
    *,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    skip: int = 0,
    limit: int = 10,
    active_only: bool = True
) -> List[RecommendationResponse]:
    """Get user's recommendation history."""
    recommendations = crud_recommendations.get_user_recommendations(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        active_only=active_only
    )
    
    response = []
    for rec in recommendations:
        books = []
        for item in rec.items:
            book = crud_books.get_book(db, book_id=item.book_id)
            if book:
                books.append({
                    **book.__dict__,
                    "relevance_score": item.relevance_score,
                    "reason": item.reason
                })
        response.append(RecommendationResponse(
            recommendation=rec,
            books=books
        ))
    
    return response

@router.get("/recommendations/{recommendation_id}", response_model=RecommendationResponse)
def get_recommendation(
    *,
    db: Session = Depends(get_db),
    recommendation_id: int,
    current_user = Depends(get_current_user)
) -> RecommendationResponse:
    """Get a specific recommendation set."""
    recommendation = crud_recommendations.get_recommendation(
        db=db,
        recommendation_id=recommendation_id
    )
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    if recommendation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this recommendation")
    
    books = []
    for item in recommendation.items:
        book = crud_books.get_book(db, book_id=item.book_id)
        if book:
            books.append({
                **book.__dict__,
                "relevance_score": item.relevance_score,
                "reason": item.reason
            })
    
    return RecommendationResponse(
        recommendation=recommendation,
        books=books
    )

@router.put("/recommendations/{recommendation_id}", response_model=Recommendation)
def update_recommendation(
    *,
    db: Session = Depends(get_db),
    recommendation_id: int,
    recommendation: RecommendationUpdate,
    current_user = Depends(get_current_user)
) -> Recommendation:
    """Update a recommendation set."""
    db_recommendation = crud_recommendations.get_recommendation(
        db=db,
        recommendation_id=recommendation_id
    )
    if not db_recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    if db_recommendation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this recommendation")
    
    updated = crud_recommendations.update_recommendation(
        db=db,
        recommendation_id=recommendation_id,
        recommendation=recommendation
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return updated

@router.get("/trending/", response_model=List[TrendingBook])
def get_trending_books(
    *,
    db: Session = Depends(get_db),
    limit: int = 10,
    days: int = 7
) -> List[TrendingBook]:
    """Get trending books based on recent activity."""
    return crud_recommendations.get_trending_books(
        db=db,
        limit=limit,
        days=days
    )

@router.post("/generate/", response_model=RecommendationResponse)
def generate_recommendations(
    *,
    db: Session = Depends(get_db),
    request: RecommendationRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
) -> RecommendationResponse:
    """Generate new recommendations for the user."""
    recommender = HybridRecommender(db)
    
    # Get recommendations based on type
    if request.recommendation_type == "PERSONALIZED":
        recommendations = recommender.get_hybrid_recommendations(
            user_id=current_user.id,
            n_recommendations=request.limit
        )
    elif request.recommendation_type == "SIMILAR" and request.source_book_id:
        recommendations = recommender.get_hybrid_recommendations(
            book_id=request.source_book_id,
            n_recommendations=request.limit
        )
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid recommendation type or missing source book"
        )
    
    # Create recommendation record
    recommendation_items = [
        {
            "book_id": rec["book_id"],
            "relevance_score": rec["relevance_score"],
            "position": idx + 1,
            "reason": rec["reason"]
        }
        for idx, rec in enumerate(recommendations)
    ]
    
    db_recommendation = crud_recommendations.create_recommendation(
        db=db,
        user_id=current_user.id,
        recommendation=RecommendationCreate(
            recommendation_type=request.recommendation_type,
            source_book_id=request.source_book_id,
            items=recommendation_items
        )
    )
    
    # Get book details
    books = []
    for item in db_recommendation.items:
        book = crud_books.get_book(db, book_id=item.book_id)
        if book:
            books.append({
                **book.__dict__,
                "relevance_score": item.relevance_score,
                "reason": item.reason
            })
    
    # Schedule model retraining in background if needed
    background_tasks.add_task(
        recommender.train,
        books=[book.__dict__ for book in crud_books.get_books(db, limit=1000)],
        user_activities=[
            activity.__dict__
            for activity in crud_recommendations.get_user_activities(
                db=db,
                user_id=current_user.id,
                limit=1000
            )
        ]
    )
    
    return RecommendationResponse(
        recommendation=db_recommendation,
        books=books
    ) 