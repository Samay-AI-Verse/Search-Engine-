from textblob import TextBlob
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self):
        """Initialize sentiment analyzer using TextBlob"""
        logger.info("Initialized TextBlob sentiment analyzer")
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            if polarity > 0.1:
                sentiment = "positive"
            elif polarity < -0.1:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
            return {
                "sentiment": sentiment,
                "confidence": abs(polarity),
                "polarity": polarity,
                "subjectivity": subjectivity
            }
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return {
                "sentiment": "neutral",
                "confidence": 0.0,
                "polarity": 0.0,
                "subjectivity": 0.0
            }
    
    def analyze_bulk(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze sentiment for multiple texts"""
        return [self.analyze(text) for text in texts]