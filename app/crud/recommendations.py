from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from fastapi import HTTPException

from app.models.recommendations import UserActivity, Recommendation, RecommendationItem, ModelData
from app.models.books import Book
from app.models.users import User
from app.schemas.recommendations import (
    UserActivityCreate,
    UserActivityUpdate,
    RecommendationCreate,
    RecommendationUpdate,
    ModelDataCreate
)

def get_user_activity(db: Session, user_id: int, book_id: int) -> Optional[UserActivity]:
    return db.query(UserActivity).filter(
        UserActivity.user_id == user_id,
        UserActivity.book_id == book_id
    ).first()

def create_user_activity(
    db: Session,
    user_id: int,
    activity: UserActivityCreate
) -> UserActivity:
    db_activity = UserActivity(
        user_id=user_id,
        book_id=activity.book_id,
        view_count=activity.view_count,
        is_favorite=activity.is_favorite,
        interaction_score=activity.interaction_score,
        last_viewed=datetime.utcnow()
    )
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity

def update_user_activity(
    db: Session,
    user_id: int,
    book_id: int,
    activity: UserActivityUpdate
) -> Optional[UserActivity]:
    db_activity = get_user_activity(db, user_id, book_id)
    if not db_activity:
        return None

    update_data = activity.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_activity, field, value)
    
    db_activity.last_viewed = datetime.utcnow()
    db.commit()
    db.refresh(db_activity)
    return db_activity

def record_book_view(db: Session, user_id: int, book_id: int) -> UserActivity:
    db_activity = get_user_activity(db, user_id, book_id)
    if db_activity:
        db_activity.view_count += 1
        db_activity.last_viewed = datetime.utcnow()
        db_activity.interaction_score = calculate_interaction_score(db_activity)
        db.commit()
        db.refresh(db_activity)
        return db_activity
    
    return create_user_activity(
        db,
        user_id,
        UserActivityCreate(
            book_id=book_id,
            view_count=1,
            interaction_score=0.1  # Initial score for a view
        )
    )

def toggle_favorite(db: Session, user_id: int, book_id: int) -> UserActivity:
    db_activity = get_user_activity(db, user_id, book_id)
    if not db_activity:
        db_activity = create_user_activity(
            db,
            user_id,
            UserActivityCreate(book_id=book_id, is_favorite=True)
        )
    else:
        db_activity.is_favorite = not db_activity.is_favorite
        db_activity.interaction_score = calculate_interaction_score(db_activity)
        db.commit()
        db.refresh(db_activity)
    return db_activity

def calculate_interaction_score(activity: UserActivity) -> float:
    base_score = 0.0
    if activity.is_favorite:
        base_score += 0.5
    base_score += min(activity.view_count * 0.1, 0.4)  # Up to 0.4 for views
    return min(base_score, 1.0)

def get_user_activities(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    favorite_only: bool = False
) -> List[UserActivity]:
    query = db.query(UserActivity).filter(UserActivity.user_id == user_id)
    if favorite_only:
        query = query.filter(UserActivity.is_favorite == True)
    return query.order_by(desc(UserActivity.last_viewed)).offset(skip).limit(limit).all()

def get_recommendation(
    db: Session,
    recommendation_id: int
) -> Optional[Recommendation]:
    return db.query(Recommendation).filter(
        Recommendation.recommendation_id == recommendation_id
    ).first()

def create_recommendation(
    db: Session,
    user_id: int,
    recommendation: RecommendationCreate
) -> Recommendation:
    db_recommendation = Recommendation(
        user_id=user_id,
        recommendation_type=recommendation.recommendation_type,
        source_book_id=recommendation.source_book_id,
        date_generated=datetime.utcnow(),
        is_active=True
    )
    db.add(db_recommendation)
    db.flush()  # Flush to get the recommendation_id

    # Create recommendation items
    for item in recommendation.items:
        db_item = RecommendationItem(
            recommendation_id=db_recommendation.recommendation_id,
            book_id=item.book_id,
            relevance_score=item.relevance_score,
            position=item.position,
            reason=item.reason
        )
        db.add(db_item)

    db.commit()
    db.refresh(db_recommendation)
    return db_recommendation

def update_recommendation(
    db: Session,
    recommendation_id: int,
    recommendation: RecommendationUpdate
) -> Optional[Recommendation]:
    db_recommendation = get_recommendation(db, recommendation_id)
    if not db_recommendation:
        return None

    update_data = recommendation.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_recommendation, field, value)

    db.commit()
    db.refresh(db_recommendation)
    return db_recommendation

def get_user_recommendations(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 10,
    active_only: bool = True
) -> List[Recommendation]:
    query = db.query(Recommendation).filter(Recommendation.user_id == user_id)
    if active_only:
        query = query.filter(Recommendation.is_active == True)
    return query.order_by(desc(Recommendation.date_generated)).offset(skip).limit(limit).all()

def get_model_data(db: Session, name: str) -> Optional[ModelData]:
    return db.query(ModelData).filter(ModelData.name == name).first()

def save_model_data(
    db: Session,
    model_data: ModelDataCreate
) -> ModelData:
    existing = get_model_data(db, model_data.name)
    if existing:
        existing.version += 1
        existing.data = model_data.data
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing

    db_model_data = ModelData(
        name=model_data.name,
        version=model_data.version,
        data=model_data.data,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(db_model_data)
    db.commit()
    db.refresh(db_model_data)
    return db_model_data

def get_trending_books(
    db: Session,
    limit: int = 10,
    days: int = 7
) -> List[Dict[str, Any]]:
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Get recent views and ratings
    trending_query = db.query(
        Book.book_id,
        Book.title,
        Book.author,
        func.count(UserActivity.id).label('recent_views'),
        func.avg(Book.rating).label('average_rating'),
        func.count(Book.reviews).label('recent_ratings')
    ).join(
        UserActivity,
        Book.book_id == UserActivity.book_id
    ).filter(
        UserActivity.last_viewed >= cutoff_date
    ).group_by(
        Book.book_id
    ).order_by(
        desc('recent_views'),
        desc('average_rating')
    ).limit(limit)

    results = []
    for row in trending_query:
        trending_score = calculate_trending_score(
            row.recent_views,
            row.recent_ratings,
            row.average_rating
        )
        results.append({
            "book_id": row.book_id,
            "title": row.title,
            "author": row.author,
            "trending_score": trending_score,
            "recent_views": row.recent_views,
            "recent_ratings": row.recent_ratings,
            "average_rating": float(row.average_rating) if row.average_rating else 0.0
        })
    
    return results

def calculate_trending_score(views: int, ratings: int, avg_rating: float) -> float:
    view_weight = 0.4
    rating_weight = 0.6
    
    normalized_views = min(views / 100, 1.0)  # Cap at 100 views
    normalized_ratings = min(ratings / 50, 1.0)  # Cap at 50 ratings
    normalized_rating = (avg_rating - 1) / 4  # Convert 1-5 scale to 0-1
    
    return (
        view_weight * normalized_views +
        rating_weight * (0.7 * normalized_ratings + 0.3 * normalized_rating)
    ) 