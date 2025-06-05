from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
from surprise import SVD
from surprise import Dataset, Reader
import pickle
import logging
from datetime import datetime

from app.models.recommendations import ModelData
from app.crud.recommendations import get_model_data, save_model_data
from app.schemas.recommendations import ModelDataCreate

logger = logging.getLogger(__name__)

class HybridRecommender:
    def __init__(self, db_session):
        self.db = db_session
        self.content_model = None
        self.collaborative_model = None
        self.books_df = None
        self.user_item_matrix = None
        self.vectorizer = None
        self.model_name = "hybrid_recommender"
        self.load_model()

    def load_model(self) -> None:
        """Load the recommendation model from the database."""
        try:
            model_data = get_model_data(self.db, self.model_name)
            if model_data:
                data = model_data.data
                self.vectorizer = pickle.loads(data['vectorizer'])
                self.content_model = pickle.loads(data['content_model'])
                self.collaborative_model = pickle.loads(data['collaborative_model'])
                self.books_df = pd.DataFrame(data['books_data'])
                self.user_item_matrix = csr_matrix(data['user_item_matrix'])
                logger.info(f"Loaded recommendation model version {model_data.version}")
            else:
                logger.info("No existing model found. Will train new model when needed.")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise

    def save_model(self) -> None:
        """Save the current model state to the database."""
        try:
            model_data = {
                'vectorizer': pickle.dumps(self.vectorizer),
                'content_model': pickle.dumps(self.content_model),
                'collaborative_model': pickle.dumps(self.collaborative_model),
                'books_data': self.books_df.to_dict(),
                'user_item_matrix': self.user_item_matrix.toarray()
            }
            
            save_model_data(
                self.db,
                ModelDataCreate(
                    name=self.model_name,
                    data=model_data
                )
            )
            logger.info("Successfully saved recommendation model")
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            raise

    def prepare_data(
        self,
        books: List[Dict[str, Any]],
        user_activities: List[Dict[str, Any]]
    ) -> Tuple[pd.DataFrame, csr_matrix]:
        """Prepare data for model training."""
        # Prepare books data
        books_df = pd.DataFrame(books)
        books_df['content'] = books_df.apply(
            lambda x: f"{x['title']} {x['author']} {x['description']} {' '.join(x['genres'])}",
            axis=1
        )

        # Create user-item interaction matrix
        user_ids = {activity['user_id']: idx for idx, activity in enumerate(set(a['user_id'] for a in user_activities))}
        book_ids = {book['book_id']: idx for idx, book in enumerate(books)}
        
        matrix_data = []
        for activity in user_activities:
            if activity['user_id'] in user_ids and activity['book_id'] in book_ids:
                matrix_data.append((
                    user_ids[activity['user_id']],
                    book_ids[activity['book_id']],
                    activity['interaction_score']
                ))
        
        user_item_matrix = csr_matrix(
            (np.array([d[2] for d in matrix_data]),
             (np.array([d[0] for d in matrix_data]),
              np.array([d[1] for d in matrix_data]))),
            shape=(len(user_ids), len(book_ids))
        )

        return books_df, user_item_matrix

    def train(
        self,
        books: List[Dict[str, Any]],
        user_activities: List[Dict[str, Any]]
    ) -> None:
        """Train both content-based and collaborative filtering models."""
        try:
            # Prepare data
            self.books_df, self.user_item_matrix = self.prepare_data(books, user_activities)

            # Train content-based model
            self.vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 2)
            )
            content_matrix = self.vectorizer.fit_transform(self.books_df['content'])
            self.content_model = cosine_similarity(content_matrix)

            # Train collaborative filtering model using scikit-surprise
            reader = Reader(rating_scale=(0, 1))
            data = Dataset.load_from_df(
                pd.DataFrame({
                    'user_id': [a['user_id'] for a in user_activities],
                    'book_id': [a['book_id'] for a in user_activities],
                    'rating': [a['interaction_score'] for a in user_activities]
                }),
                reader
            )
            trainset = data.build_full_trainset()
            self.collaborative_model = SVD(n_factors=64, n_epochs=15, lr_all=0.01, reg_all=0.01)
            self.collaborative_model.fit(trainset)

            # Save the trained model
            self.save_model()
            logger.info("Successfully trained and saved recommendation model")
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            raise

    def get_content_recommendations(
        self,
        book_id: int,
        n_recommendations: int = 10
    ) -> List[Tuple[int, float]]:
        """Get content-based recommendations for a book."""
        try:
            book_idx = self.books_df[self.books_df['book_id'] == book_id].index[0]
            book_similarities = self.content_model[book_idx]
            similar_indices = np.argsort(book_similarities)[::-1][1:n_recommendations + 1]
            
            return [
                (self.books_df.iloc[idx]['book_id'], float(book_similarities[idx]))
                for idx in similar_indices
            ]
        except Exception as e:
            logger.error(f"Error getting content recommendations: {str(e)}")
            return []

    def get_collaborative_recommendations(
        self,
        user_id: int,
        n_recommendations: int = 10
    ) -> List[Tuple[int, float]]:
        """Get collaborative filtering recommendations for a user."""
        try:
            predictions = []
            for book_id in self.books_df['book_id']:
                pred = self.collaborative_model.predict(user_id, book_id)
                predictions.append((book_id, pred.est))
            
            predictions.sort(key=lambda x: x[1], reverse=True)
            return predictions[:n_recommendations]
        except Exception as e:
            logger.error(f"Error getting collaborative recommendations: {str(e)}")
            return []

    def get_hybrid_recommendations(
        self,
        user_id: Optional[int] = None,
        book_id: Optional[int] = None,
        n_recommendations: int = 10,
        content_weight: float = 0.3,
        collab_weight: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Get hybrid recommendations combining content-based and collaborative filtering."""
        try:
            if not user_id and not book_id:
                raise ValueError("Either user_id or book_id must be provided")

            recommendations = {}
            
            # Get content-based recommendations if book_id is provided
            if book_id:
                content_recs = self.get_content_recommendations(book_id, n_recommendations)
                for book_id, score in content_recs:
                    recommendations[book_id] = content_weight * score

            # Get collaborative filtering recommendations if user_id is provided
            if user_id:
                collab_recs = self.get_collaborative_recommendations(user_id, n_recommendations)
                for book_id, score in collab_recs:
                    if book_id in recommendations:
                        recommendations[book_id] += collab_weight * score
                    else:
                        recommendations[book_id] = collab_weight * score

            # Sort recommendations by score
            sorted_recs = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
            return [
                {
                    'book_id': book_id,
                    'score': score,
                    'reason': self._get_recommendation_reason(book_id, user_id, book_id)
                }
                for book_id, score in sorted_recs[:n_recommendations]
            ]
        except Exception as e:
            logger.error(f"Error getting hybrid recommendations: {str(e)}")
            return []

    def _get_recommendation_reason(
        self,
        book_id: int,
        user_id: Optional[int],
        source_book_id: Optional[int]
    ) -> str:
        """Generate a reason for the recommendation."""
        if user_id and source_book_id:
            return f"Recommended based on your interest in similar books and your reading history."
        elif user_id:
            return f"Recommended based on your reading history and preferences."
        else:
            return f"Recommended based on similarity to books you've viewed." 