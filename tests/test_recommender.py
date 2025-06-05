import pytest
from sqlalchemy.orm import Session
from app.services.recommender import HybridRecommender
from app.crud import books as crud_books
from app.crud import recommendations as crud_recommendations

# Sample test data
SAMPLE_BOOKS = [
    {
        "book_id": 1,
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "description": "A story of the fabulously wealthy Jay Gatsby",
        "genres": ["Fiction", "Classic"]
    },
    {
        "book_id": 2,
        "title": "1984",
        "author": "George Orwell",
        "description": "A dystopian social science fiction novel",
        "genres": ["Fiction", "Dystopian"]
    },
    {
        "book_id": 3,
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "description": "The story of racial injustice and the loss of innocence",
        "genres": ["Fiction", "Classic"]
    }
]

SAMPLE_ACTIVITIES = [
    {
        "user_id": 1,
        "book_id": 1,
        "interaction_score": 1.0
    },
    {
        "user_id": 1,
        "book_id": 2,
        "interaction_score": 0.8
    },
    {
        "user_id": 2,
        "book_id": 1,
        "interaction_score": 0.9
    },
    {
        "user_id": 2,
        "book_id": 3,
        "interaction_score": 0.7
    }
]

def test_recommender_initialization(db: Session):
    """Test recommender initialization"""
    recommender = HybridRecommender(db)
    assert recommender.content_model is None
    assert recommender.collaborative_model is None
    assert recommender.books_df is None
    assert recommender.user_item_matrix is None
    assert recommender.vectorizer is None

def test_recommender_training(db: Session):
    """Test recommender training"""
    recommender = HybridRecommender(db)
    recommender.train(SAMPLE_BOOKS, SAMPLE_ACTIVITIES)
    
    assert recommender.content_model is not None
    assert recommender.collaborative_model is not None
    assert recommender.books_df is not None
    assert recommender.user_item_matrix is not None
    assert recommender.vectorizer is not None

def test_content_recommendations(db: Session):
    """Test content-based recommendations"""
    recommender = HybridRecommender(db)
    recommender.train(SAMPLE_BOOKS, SAMPLE_ACTIVITIES)
    
    recommendations = recommender.get_content_recommendations(book_id=1, n_recommendations=2)
    assert len(recommendations) == 2
    assert all(isinstance(rec[0], int) for rec in recommendations)
    assert all(isinstance(rec[1], float) for rec in recommendations)

def test_collaborative_recommendations(db: Session):
    """Test collaborative filtering recommendations"""
    recommender = HybridRecommender(db)
    recommender.train(SAMPLE_BOOKS, SAMPLE_ACTIVITIES)
    
    recommendations = recommender.get_collaborative_recommendations(user_id=1, n_recommendations=2)
    assert len(recommendations) == 2
    assert all(isinstance(rec[0], int) for rec in recommendations)
    assert all(isinstance(rec[1], float) for rec in recommendations)

def test_hybrid_recommendations(db: Session):
    """Test hybrid recommendations"""
    recommender = HybridRecommender(db)
    recommender.train(SAMPLE_BOOKS, SAMPLE_ACTIVITIES)
    
    recommendations = recommender.get_hybrid_recommendations(
        user_id=1,
        n_recommendations=2,
        content_weight=0.3,
        collab_weight=0.7
    )
    assert len(recommendations) == 2
    assert all(isinstance(rec["book_id"], int) for rec in recommendations)
    assert all(isinstance(rec["score"], float) for rec in recommendations)
    assert all(isinstance(rec["reason"], str) for rec in recommendations)

def test_recommendation_reasons(db: Session):
    """Test recommendation reason generation"""
    recommender = HybridRecommender(db)
    recommender.train(SAMPLE_BOOKS, SAMPLE_ACTIVITIES)
    
    # Test user-based recommendation reason
    reason = recommender._get_recommendation_reason(book_id=1, user_id=1, source_book_id=None)
    assert isinstance(reason, str)
    assert "reading history" in reason.lower()
    
    # Test book-based recommendation reason
    reason = recommender._get_recommendation_reason(book_id=1, user_id=None, source_book_id=2)
    assert isinstance(reason, str)
    assert "similarity" in reason.lower() 