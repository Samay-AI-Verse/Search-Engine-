import httpx
import json
import logging
from typing import List, Dict, Any, Optional
from .config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GroqAI:
    def __init__(self):
        self.api_key = Config.GROQ_API_KEY
        self.base_url = "https://api.groq.com/openai/v1"
        self.model = "llama-3.3-70b-versatile"
        
    async def generate_short_summary(self, query: str, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate SHORT AI summary like Gemini"""
        if not self.api_key:
            return {
                "error": "Groq API key not configured",
                "summary": "Add GROQ_API_KEY to .env file for AI summaries"
            }
        
        if not results:
            return {
                "summary": f"Search results for '{query}' are not available. Try searching on Google."
            }
        
        try:
            # Prepare context - keep it simple
            context_text = ""
            for i, result in enumerate(results[:3], 1):
                title = result.get('title', '')
                snippet = result.get('snippet', '')[:150]
                context_text += f"{i}. {title}: {snippet}\n"
            
            # Simple prompt for short summary
            prompt = f"""Question: {query}

Search Results:
{context_text}

Give a VERY SHORT answer (2-3 sentences) to the question based on the search results above.
Keep it brief and informative like Google's AI overview.

Answer:"""

            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.5,
                        "max_tokens": 150,
                        "top_p": 0.9
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    summary = data["choices"][0]["message"]["content"].strip()
                    return {
                        "summary": summary,
                        "model": self.model
                    }
                else:
                    logger.error(f"Groq API error: {response.status_code} - {response.text}")
                    return {"summary": f"Unable to generate AI summary for '{query}'"}
                    
        except Exception as e:
            logger.error(f"Groq error: {e}")
            return {"summary": f"Error generating AI summary for '{query}'"}