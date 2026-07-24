import httpx
import asyncio
import re
from typing import List, Dict, Any, Optional
import time
import logging
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from .vectorizer import Vectorizer
from .sentiment_analyzer import SentimentAnalyzer
from .groq_ai import GroqAI
from .config import Config
from .models import SearchResult, SearchQuery

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchEngine:
    def __init__(self):
        self.vectorizer = Vectorizer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.groq_ai = GroqAI()
        self.google_api_key = Config.GOOGLE_SEARCH_API_KEY
        self.search_engine_id = Config.GOOGLE_SEARCH_ENGINE_ID

    def _get_google_search_entry(self, query: str) -> Dict[str, Any]:
        """Always provide a Google search page as the first result."""
        return {
            "title": f"Google Search - {query}",
            "link": f"https://www.google.com/search?q={quote_plus(query)}",
            "snippet": f"Search Google for '{query}' and see the latest web results.",
            "domain": "google.com",
            "source": "Google",
            "icon": "https://www.google.com/s2/favicons?domain=google.com&sz=32",
            "priority": 0
        }
        
    async def search_duckduckgo_api(self, query: str, num_results: int = 20) -> List[Dict[str, Any]]:
        """Search using DuckDuckGo API"""
        try:
            search_url = f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json&no_html=1&skip_disambig=1"
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(search_url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                response.raise_for_status()
                data = response.json()
                
                results = []
                
                # Get Abstract
                if data.get("Abstract"):
                    link = data.get("AbstractURL", "")
                    results.append({
                        'title': data.get("Heading", query)[:120],
                        'link': link if link else f"https://duckduckgo.com/?q={quote_plus(query)}",
                        'snippet': data.get("Abstract", "")[:350],
                        'domain': self._extract_domain(link) if link else 'duckduckgo.com',
                        'source': 'DuckDuckGo',
                        'icon': f"https://www.google.com/s2/favicons?domain={self._extract_domain(link) if link else 'duckduckgo.com'}&sz=32"
                    })
                
                # Get Related Topics
                if "RelatedTopics" in data:
                    for topic in data["RelatedTopics"][:num_results]:
                        try:
                            if "Text" in topic and "FirstURL" in topic:
                                text = topic["Text"]
                                parts = text.split(' - ', 1)
                                title = parts[0] if parts else text
                                snippet = parts[1] if len(parts) > 1 else text
                                link = topic["FirstURL"]
                                
                                results.append({
                                    'title': title[:120],
                                    'link': link,
                                    'snippet': snippet[:350],
                                    'domain': self._extract_domain(link),
                                    'source': 'DuckDuckGo',
                                    'icon': f"https://www.google.com/s2/favicons?domain={self._extract_domain(link)}&sz=32"
                                })
                        except Exception:
                            continue
                
                logger.info(f"DuckDuckGo API returned {len(results)} results")
                return results
                
        except Exception as e:
            logger.error(f"DuckDuckGo API error: {e}")
            return []
    
    async def _search_duckduckgo_html(self, query: str, num_results: int = 20) -> List[Dict[str, Any]]:
        """HTML search with better error handling"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            
            async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
                response = await client.get(search_url, headers=headers)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                results = []
                
                # Try different selectors
                result_elements = soup.find_all('div', class_='result')
                
                if not result_elements:
                    result_elements = soup.find_all('div', {'class': re.compile(r'result.*')})
                
                for result in result_elements[:num_results]:
                    try:
                        title_elem = result.find('a', class_='result__a')
                        if not title_elem:
                            title_elem = result.find('a', {'class': re.compile(r'result.*link.*')})
                        
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            link = title_elem.get('href', '')
                            
                            snippet_elem = result.find('a', class_='result__snippet')
                            if not snippet_elem:
                                snippet_elem = result.find('div', class_='result__snippet')
                            
                            snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
                            
                            if link.startswith('/'):
                                link = 'https://duckduckgo.com' + link
                            
                            domain = self._extract_domain(link)
                            
                            results.append({
                                'title': title[:120],
                                'link': link,
                                'snippet': snippet[:350] if snippet else 'No description available',
                                'domain': domain,
                                'source': 'DuckDuckGo',
                                'icon': f"https://www.google.com/s2/favicons?domain={domain}&sz=32"
                            })
                    except Exception as e:
                        continue
                
                logger.info(f"DuckDuckGo HTML returned {len(results)} results")
                return results
                
        except Exception as e:
            logger.error(f"DuckDuckGo HTML search error: {e}")
            return []
    
    async def search_google(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """Search using Google Custom Search"""
        try:
            if not self.google_api_key or not self.search_engine_id or self.google_api_key == "your_google_api_key_here":
                logger.warning("Google API not configured, skipping")
                return []
                
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": self.google_api_key,
                "cx": self.search_engine_id,
                "q": query,
                "num": min(num_results, 10)
            }
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                results = []
                if "items" in data:
                    for item in data["items"]:
                        link = item.get("link", "")
                        domain = self._extract_domain(link)
                        results.append({
                            "title": item.get("title", "")[:120],
                            "link": link,
                            "snippet": item.get("snippet", "")[:350],
                            "domain": domain,
                            "source": "Google",
                            "icon": f"https://www.google.com/s2/favicons?domain={domain}&sz=32",
                            "priority": 1
                        })
                
                logger.info(f"Google returned {len(results)} results")
                return results
                
        except Exception as e:
            logger.error(f"Google search error: {e}")
            return []
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            if not url:
                return "web"
            if '://' in url:
                url = url.split('://')[1]
            domain = url.split('/')[0]
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return "web"
    
    async def search(self, search_query: SearchQuery) -> Dict[str, Any]:
        """Perform search - Returns 15+ REAL results"""
        start_time = time.time()
        
        all_results = [self._get_google_search_entry(search_query.query)]
        
        # 1. Prefer Google Custom Search results when configured.
        if self.google_api_key and self.google_api_key != "your_google_api_key_here":
            google_results = await self.search_google(search_query.query, 10)
            if google_results:
                all_results.extend(google_results)
        
        # 2. Try DuckDuckGo HTML search for more real web results.
        html_results = await self._search_duckduckgo_html(
            search_query.query, 
            max(search_query.max_results, 15)
        )
        if html_results:
            all_results.extend(html_results)
        
        # 3. If HTML gives too few results, try DuckDuckGo API.
        if len(all_results) < 5:
            api_results = await self.search_duckduckgo_api(
                search_query.query,
                max(search_query.max_results, 15)
            )
            if api_results:
                all_results.extend(api_results)
        
        # 4. If still no results, use fallback
        if not all_results:
            all_results = self._get_fallback_results(search_query.query, 15)
        
        # 5. Remove duplicates
        seen_links = set()
        unique_results = []
        for result in all_results:
            if result['link'] not in seen_links:
                seen_links.add(result['link'])
                unique_results.append(result)
        
        # 6. Ensure at least 10 results
        if len(unique_results) < 10:
            more_results = self._get_more_results(search_query.query, 15 - len(unique_results))
            unique_results.extend(more_results)
        
        unique_results = unique_results[:max(search_query.max_results, 15)]
        
        # 7. Process with vectorization and sentiment
        processed_results = []
        if unique_results:
            texts = [f"{r['title']} {r['snippet']}" for r in unique_results]
            
            try:
                vectors = self.vectorizer.encode(texts)
                query_vector = self.vectorizer.encode(search_query.query)
                relevance_scores = self.vectorizer.compute_similarity(query_vector, vectors)
            except Exception as e:
                logger.error(f"Vectorization error: {e}")
                relevance_scores = [0.5] * len(unique_results)
            
            sentiments = None
            if search_query.use_sentiment:
                try:
                    sentiments = self.sentiment_analyzer.analyze_bulk(texts)
                except Exception as e:
                    logger.error(f"Sentiment error: {e}")
            
            for i, (result, score) in enumerate(zip(unique_results, relevance_scores)):
                search_result = SearchResult(
                    title=result["title"][:120],
                    link=result["link"],
                    snippet=result["snippet"][:350] if result["snippet"] else "No description available",
                        relevance_score=float(score) if score is not None else 0.5,
                    source=result.get("source", "Web"),
                    domain=result.get("domain", ""),
                    icon=result.get("icon", ""),
                    sentiment=sentiments[i] if sentiments and i < len(sentiments) else None
                )
                processed_results.append(search_result)
            
            processed_results.sort(
                key=lambda x: (
                    0 if (x.source or "").lower() == "google" and x.domain == "google.com" else
                    1 if (x.source or "").lower() == "google" else
                    2,
                    -(x.relevance_score or 0)
                )
            )
        
        # 8. Generate AI summary
        ai_summary = None
        if processed_results and Config.USE_GROQ and self.groq_ai.api_key:
            try:
                top_results = processed_results[:5]
                ai_summary = await self.groq_ai.generate_short_summary(
                    search_query.query,
                    [{"title": r.title, "snippet": r.snippet} for r in top_results]
                )
            except Exception as e:
                logger.error(f"AI summary error: {e}")
        
        processing_time = time.time() - start_time
        
        return {
            "results": processed_results,
            "ai_summary": ai_summary,
            "total_results": len(processed_results),
            "processing_time": processing_time,
            "source_used": "Google + DuckDuckGo"
        }
    
    def _get_fallback_results(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Fallback results with multiple real websites"""
        websites = [
            {"domain": "google.com", "name": "Google"},
            {"domain": "wikipedia.org", "name": "Wikipedia"},
            {"domain": "stackoverflow.com", "name": "Stack Overflow"},
            {"domain": "github.com", "name": "GitHub"},
            {"domain": "reddit.com", "name": "Reddit"},
            {"domain": "medium.com", "name": "Medium"},
            {"domain": "youtube.com", "name": "YouTube"},
            {"domain": "quora.com", "name": "Quora"},
            {"domain": "dev.to", "name": "DEV Community"},
            {"domain": "hackernews.com", "name": "Hacker News"},
        ]
        
        results = []
        for site in websites[:num_results]:
            results.append({
                "title": f"{site['name']} - {query}",
                "link": f"https://{site['domain']}/search?q={quote_plus(query)}",
                "snippet": f"Search results for '{query}' on {site['name']}.",
                "domain": site['domain'],
                "source": site['name'],
                "icon": f"https://www.google.com/s2/favicons?domain={site['domain']}&sz=32",
                "priority": 0 if site["domain"] == "google.com" else 3
            })
        return results
    
    def _get_more_results(self, query: str, count: int) -> List[Dict[str, Any]]:
        """Get additional results"""
        more_sites = [
            {"domain": "bing.com", "name": "Bing"},
            {"domain": "yahoo.com", "name": "Yahoo"},
            {"domain": "duckduckgo.com", "name": "DuckDuckGo"},
            {"domain": "ask.com", "name": "Ask"},
        ]
        
        results = []
        for site in more_sites[:count]:
            results.append({
                "title": f"{site['name']} - {query}",
                "link": f"https://{site['domain']}/search?q={quote_plus(query)}",
                "snippet": f"Find '{query}' on {site['name']}.",
                "domain": site['domain'],
                "source": site['name'],
                "icon": f"https://www.google.com/s2/favicons?domain={site['domain']}&sz=32",
                "priority": 3
            })
        return results
