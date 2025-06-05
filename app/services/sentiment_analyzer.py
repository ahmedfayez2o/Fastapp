from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import Dict, List, Tuple
import numpy as np

class SentimentAnalyzer:
    def __init__(self):
        self.model_name = "cardiffnlp/twitter-roberta-base-sentiment"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
    
    def analyze_sentiment(self, text: str) -> float:
        """
        Analyze the sentiment of a text and return a score between -1 and 1.
        -1 indicates very negative sentiment, 1 indicates very positive sentiment.
        """
        if not text:
            return 0.0
        
        # Tokenize and prepare input
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Get model prediction
        with torch.no_grad():
            outputs = self.model(**inputs)
            scores = torch.softmax(outputs.logits, dim=1)
        
        # Convert to sentiment score (-1 to 1)
        # The model outputs 3 classes: negative (0), neutral (1), positive (2)
        sentiment_score = scores[0][2].item() - scores[0][0].item()
        return sentiment_score
    
    def get_sentiment_interpretation(self, score: float) -> str:
        """
        Convert a sentiment score to a human-readable interpretation.
        """
        if score >= 0.5:
            return "Very Positive"
        elif score >= 0.1:
            return "Positive"
        elif score >= -0.1:
            return "Neutral"
        elif score >= -0.5:
            return "Negative"
        else:
            return "Very Negative"
    
    def analyze_reviews(self, reviews: List[Tuple[int, str, str]]) -> List[Dict]:
        """
        Analyze a list of reviews and return sentiment analysis results.
        Each review should be a tuple of (review_id, book_title, review_text).
        """
        results = []
        for review_id, book_title, text in reviews:
            if not text:
                continue
            
            sentiment = self.analyze_sentiment(text)
            interpretation = self.get_sentiment_interpretation(sentiment)
            
            results.append({
                "review_id": review_id,
                "book_title": book_title,
                "sentiment": sentiment,
                "interpretation": interpretation
            })
        
        return results
    
    def get_sentiment_stats(self, reviews: List[Dict]) -> Dict:
        """
        Calculate sentiment statistics from a list of review analysis results.
        """
        if not reviews:
            return {
                "total_reviews": 0,
                "reviews_with_comments": 0,
                "average_sentiment": 0,
                "sentiment_stats": {
                    "Very Positive": 0,
                    "Positive": 0,
                    "Neutral": 0,
                    "Negative": 0,
                    "Very Negative": 0
                },
                "interpretation": "No reviews available"
            }
        
        sentiments = [r["sentiment"] for r in reviews]
        interpretations = [r["interpretation"] for r in reviews]
        
        # Calculate statistics
        avg_sentiment = np.mean(sentiments)
        sentiment_stats = {
            "Very Positive": interpretations.count("Very Positive"),
            "Positive": interpretations.count("Positive"),
            "Neutral": interpretations.count("Neutral"),
            "Negative": interpretations.count("Negative"),
            "Very Negative": interpretations.count("Very Negative")
        }
        
        # Generate interpretation
        if avg_sentiment >= 0.5:
            interpretation = "Overall very positive sentiment"
        elif avg_sentiment >= 0.1:
            interpretation = "Overall positive sentiment"
        elif avg_sentiment >= -0.1:
            interpretation = "Overall neutral sentiment"
        elif avg_sentiment >= -0.5:
            interpretation = "Overall negative sentiment"
        else:
            interpretation = "Overall very negative sentiment"
        
        return {
            "total_reviews": len(reviews),
            "reviews_with_comments": len([r for r in reviews if r["sentiment"] != 0]),
            "average_sentiment": float(avg_sentiment),
            "sentiment_stats": sentiment_stats,
            "interpretation": interpretation
        } 