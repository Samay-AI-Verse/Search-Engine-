import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Groq API (Required for AI features)
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    
    # Google API (Optional - skip if you don't have)
    GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY", "")
    GOOGLE_SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID", "")
    
    # Model settings
    MODEL_NAME = "tfidf"
    VECTOR_DIMENSION = 100
    
    # Search settings
    DEFAULT_MAX_RESULTS = 15
    SEARCH_TIMEOUT = 20
    
    # Enable/Disable search sources
    USE_DUCKDUCKGO = True
    USE_GOOGLE = bool(GOOGLE_SEARCH_API_KEY and GOOGLE_SEARCH_API_KEY != "your_google_api_key_here")
    USE_WIKIPEDIA = True
    USE_GROQ = bool(GROQ_API_KEY)