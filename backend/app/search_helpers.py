import httpx
import asyncio
from typing import List, Dict, Any
import logging
from urllib.parse import quote_plus
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchHelpers:
    @staticmethod
    async def fetch_page_content(url: str) -> str:
        """Fetch and extract text content from a webpage"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                return text[:5000]  # Limit text length
                
        except Exception as e:
            logger.error(f"Error fetching page: {e}")
            return ""
    
    @staticmethod
    async def search_news(query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Search news articles"""
        try:
            news_url = f"https://news.google.com/rss/search?q={quote_plus(query)}"
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(news_url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'xml')
                items = soup.find_all('item')[:num_results]
                
                results = []
                for item in items:
                    title = item.title.text if item.title else ""
                    link = item.link.text if item.link else ""
                    description = item.description.text if item.description else ""
                    
                    results.append({
                        'title': title,
                        'link': link,
                        'snippet': description
                    })
                
                return results
                
        except Exception as e:
            logger.error(f"News search error: {e}")
            return []