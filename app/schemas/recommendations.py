from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from decimal import Decimal

class UserActivityBase(BaseModel):
    book_id: int
    view_count: int = 0
    is_favorite: bool = False
    interaction_score: float = 0

class UserActivityCreate(UserActivityBase):
    pass

class UserActivityUpdate(BaseModel):
    view_count: Optional[int] = None
    is_favorite: Optional[bool] = None
    interaction_score: Optional[float] = None

class UserActivity(UserActivityBase):
    id: int
    user_id: int
    last_viewed: datetime

    class Config:
        from_attributes = True

class RecommendationItemBase(BaseModel):
    book_id: int
    relevance_score: float = Field(..., ge=0, le=1)
    position: int
    reason: Optional[str] = None

class RecommendationItemCreate(RecommendationItemBase):
    pass

class RecommendationItem(RecommendationItemBase):
    item_id: int
    recommendation_id: int

    class Config:
        from_attributes = True

class RecommendationBase(BaseModel):
    recommendation_type: str = Field(..., pattern="^(PERSONALIZED|TRENDING|SIMILAR|GENRE)$")
    source_book_id: Optional[int] = None

class RecommendationCreate(RecommendationBase):
    items: List[RecommendationItemCreate]

class RecommendationUpdate(BaseModel):
    is_active: Optional[bool] = None

class Recommendation(RecommendationBase):
    recommendation_id: int
    user_id: int
    date_generated: datetime
    is_active: bool
    items: List[RecommendationItem]

    class Config:
        from_attributes = True

class ModelDataBase(BaseModel):
    name: str
    version: int = 1
    data: Dict

class ModelDataCreate(ModelDataBase):
    pass

class ModelData(ModelDataBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RecommendationResponse(BaseModel):
    recommendation: Recommendation
    books: List[Dict]  # List of book details with recommendation metadata

class TrendingBook(BaseModel):
    book_id: int
    title: str
    author: str
    trending_score: float
    recent_views: int
    recent_ratings: int
    average_rating: float

class RecommendationRequest(BaseModel):
    recommendation_type: str = Field(..., pattern="^(PERSONALIZED|TRENDING|SIMILAR|GENRE)$")
    source_book_id: Optional[int] = None
    limit: int = Field(10, ge=1, le=50) 