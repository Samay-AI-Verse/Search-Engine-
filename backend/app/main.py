from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .models import SearchQuery
from .search_engine import SearchEngine
from .groq_ai import GroqAI
import time
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Search Engine", version="3.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize search engine
search_engine = SearchEngine()
groq_ai = GroqAI()

# Serve static files
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def root():
    """Serve frontend"""
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "AI Search Engine API", "docs": "/docs"}

@app.post("/api/search")
async def search(query: SearchQuery):
    """Perform search with AI"""
    try:
        result = await search_engine.search(query)
        return result
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/suggestions")
async def get_suggestions(q: str = Query(..., min_length=1)):
    """Get search suggestions"""
    try:
        suggestions = [
            f"{q} tutorial",
            f"{q} documentation", 
            f"{q} examples",
            f"{q} guide",
            f"{q} basics",
            f"{q} advanced",
            f"{q} API",
            f"{q} reference"
        ]
        
        # Add specific suggestions based on query
        q_lower = q.lower()
        if "python" in q_lower:
            suggestions.extend(["python programming", "python for beginners", "python libraries", "python django", "python flask"])
        elif "html" in q_lower:
            suggestions.extend(["html css", "html tutorial", "html5", "html tags", "html forms"])
        elif "javascript" in q_lower:
            suggestions.extend(["javascript tutorial", "js frameworks", "react javascript", "node js", "javascript functions"])
        elif "w3" in q_lower:
            suggestions.extend(["w3schools python", "w3schools html", "w3schools css", "w3schools javascript", "w3schools sql"])
        elif "css" in q_lower:
            suggestions.extend(["css tutorial", "css flexbox", "css grid", "css animations", "css selectors"])
        elif "react" in q_lower:
            suggestions.extend(["react tutorial", "react hooks", "react components", "react js", "react redux"])
        elif "sql" in q_lower:
            suggestions.extend(["sql tutorial", "sql queries", "sql database", "mysql tutorial", "postgresql"])
        elif "java" in q_lower:
            suggestions.extend(["java tutorial", "java programming", "java oops", "java spring", "java collections"])
        elif "php" in q_lower:
            suggestions.extend(["php tutorial", "php mysql", "php framework", "laravel php", "php functions"])
        elif "machine" in q_lower or "ml" in q_lower:
            suggestions.extend(["machine learning tutorial", "ml algorithms", "deep learning", "neural networks", "tensorflow"])
        elif "ai" in q_lower or "artificial" in q_lower:
            suggestions.extend(["artificial intelligence tutorial", "ai basics", "chatgpt", "generative ai", "ai tools"])
        
        return {"suggestions": suggestions[:10]}
    except Exception as e:
        logger.error(f"Suggestions error: {e}")
        return {"suggestions": []}

@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "groq_configured": bool(groq_ai.api_key),
        "google_configured": bool(search_engine.google_api_key and search_engine.google_api_key != "your_google_api_key_here")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)