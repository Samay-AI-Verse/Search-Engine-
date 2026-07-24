import numpy as np
from typing import List, Union
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Vectorizer:
    def __init__(self):
        self.vectorizer = None
        self._initialize_vectorizer()
    
    def _initialize_vectorizer(self):
        """Initialize TF-IDF vectorizer"""
        try:
            self.vectorizer = TfidfVectorizer(
                max_features=Config.VECTOR_DIMENSION,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1
            )
            logger.info("Initialized TF-IDF vectorizer")
        except Exception as e:
            logger.error(f"Error initializing vectorizer: {e}")
            self.vectorizer = None
    
    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Convert text to vector embeddings using TF-IDF"""
        if isinstance(texts, str):
            texts = [texts]
        
        # Filter out empty texts
        texts = [t for t in texts if t and t.strip()]
        
        if not texts:
            logger.warning("No valid texts to encode")
            return np.zeros((0, Config.VECTOR_DIMENSION))
        
        if not self.vectorizer:
            logger.warning("Vectorizer not initialized, using random embeddings")
            return np.random.randn(len(texts), Config.VECTOR_DIMENSION)
        
        try:
            if not hasattr(self.vectorizer, 'vocabulary_') or len(self.vectorizer.vocabulary_) == 0:
                embeddings = self.vectorizer.fit_transform(texts)
            else:
                embeddings = self.vectorizer.transform(texts)
            
            return embeddings.toarray()
            
        except Exception as e:
            logger.error(f"Error encoding texts: {e}")
            return np.random.randn(len(texts), Config.VECTOR_DIMENSION)
    
    def compute_similarity(self, query_vector: np.ndarray, document_vectors: np.ndarray) -> np.ndarray:
        """Compute cosine similarity between query and documents"""
        try:
            if len(document_vectors) == 0:
                return np.array([])
            
            if len(document_vectors.shape) == 1:
                document_vectors = document_vectors.reshape(1, -1)
            
            if len(query_vector.shape) == 1:
                query_vector = query_vector.reshape(1, -1)
            
            similarities = cosine_similarity(query_vector, document_vectors).flatten()
            return similarities
            
        except Exception as e:
            logger.error(f"Similarity computation error: {e}")
            return np.ones(len(document_vectors)) * 0.5