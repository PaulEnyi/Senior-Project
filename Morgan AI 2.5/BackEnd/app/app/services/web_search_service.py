"""
Web Search Service for Morgan State University CS Department
Provides fallback web search when knowledge base doesn't have the answer
"""

import logging
import httpx
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
import asyncio
from datetime import datetime
import re
import time
import os
import json
from functools import lru_cache
try:
    import redis
except ImportError:
    redis = None

logger = logging.getLogger(__name__)

class WebSearchService:
    """Service to search Morgan State CS department website for information"""
    
    def __init__(self):
        self.morgan_cs_urls = [
            # Computer Science Department - Primary
            "https://www.morgan.edu/scmns/computerscience",
            "https://www.morgan.edu/computer-science/degrees-and-programs",
            "https://www.morgan.edu/computer-science/faculty",
            "https://www.morgan.edu/computer-science/courses",
            "https://www.morgan.edu/computer-science/research",
            "https://www.morgan.edu/computer-science/student-resources",
            # School of CMNS
            "https://www.morgan.edu/school-of-computer-mathematical-and-natural-sciences",
            "https://www.morgan.edu/scmns/departments",
            # Academic Resources & Catalogs - PRIORITIZED FOR COURSE LOOKUPS
            "https://catalog.morgan.edu/",
            "https://catalog.morgan.edu/content.php?catoid=26&navoid=1880",  # CS Course listings
            "https://catalog.morgan.edu/preview_program.php?catoid=26&poid=5968&returnto=1880",  # BS Computer Science
            "https://catalog.morgan.edu/preview_program.php?catoid=26&poid=5969&returnto=1880",  # MS Computer Science  
            "https://catalog.morgan.edu/preview_program.php?catoid=26&poid=5970&returnto=1880",  # PhD Computer Science
            "https://www.morgan.edu/catalogs",
            "https://www.morgan.edu/academics",
            "https://www.morgan.edu/student-services-and-administration/office-of-the-registrar",
            # Admissions & Student Services
            "https://www.morgan.edu/admissions",
            "https://www.morgan.edu/student-affairs",
            "https://www.morgan.edu/financial-aid",
            # Career Services
            "https://www.morgan.edu/career-development-center",
            # Student Organizations
            "https://www.morgan.edu/student-life",
            # General University
            "https://www.morgan.edu"
        ]
        self.timeout = 30.0  # Increased timeout for deeper searches
        self.max_content_length = 100000  # Increased for more comprehensive content
        
        # HTTP headers to mimic a real browser and avoid being blocked
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Connection limits to avoid overwhelming the server
        self.max_concurrent_requests = 5  # Limit concurrent requests
        # Cache configuration (prefer Redis if available)
        self.cache_ttl_seconds = 6 * 3600  # 6 hours
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        self.redis_client = None
        if redis:
            try:
                self.redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)
                self.redis_client.ping()
                logger.info("[WEB SEARCH] Redis cache enabled")
            except Exception as e:
                logger.warning(f"[WEB SEARCH] Redis unavailable, falling back to memory cache: {e}")
        
    async def search_morgan_website(
        self, 
        query: str, 
        max_results: int = 5
    ) -> Dict[str, Any]:
        """
        Search Morgan State CS website for relevant information
        
        Args:
            query: User's search query
            max_results: Maximum number of results to return
            
        Returns:
            Dictionary containing search results and sources
        """
        try:
            logger.info(f"Searching Morgan State website for: {query}")
            
            # Extract key terms from query
            search_terms = self._extract_search_terms(query)
            
            # Search multiple pages in parallel
            search_tasks = [
                self._fetch_and_search_page(url, search_terms) 
                for url in self.morgan_cs_urls
            ]
            
            results = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            # Filter and rank results
            valid_results = []
            for result in results:
                if isinstance(result, dict) and result.get("content"):
                    valid_results.append(result)
            
            # Sort by relevance score
            valid_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
            
            # Take top results
            top_results = valid_results[:max_results]
            
            if not top_results:
                return {
                    "success": False,
                    "message": "No relevant information found on Morgan State website",
                    "query": query,
                    "sources": []
                }
            
            # Combine content from top results
            combined_content = self._combine_results(top_results, query)
            
            return {
                "success": True,
                "content": combined_content,
                "sources": [
                    {
                        "url": r["url"],
                        "title": r["title"],
                        "relevance_score": r["relevance_score"]
                    }
                    for r in top_results
                ],
                "query": query,
                "search_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error searching Morgan website: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "sources": []
            }
    
    async def _fetch_and_search_page(
        self, 
        url: str, 
        search_terms: List[str]
    ) -> Dict[str, Any]:
        """Fetch a page and search for relevant content"""
        try:
            cached = self._get_cached_page(url)
            if cached:
                logger.debug(f"[WEB SEARCH] Cache hit for {url}")
                html_text = cached.get("html", "")
            else:
                # Create client with proper headers and limits
                limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
                async with httpx.AsyncClient(
                    timeout=self.timeout,
                    headers=self.headers,
                    limits=limits,
                    follow_redirects=True,
                    verify=True  # Verify SSL certificates
                ) as client:
                    logger.debug(f"[WEB SEARCH] Fetching {url}...")
                    response = await client.get(url)
                    # Check response status
                    if response.status_code != 200:
                        logger.warning(f"[WEB SEARCH] {url} returned status {response.status_code}")
                        return {"url": url, "error": f"HTTP {response.status_code}", "relevance_score": 0}
                    html_text = response.text
                self._set_cached_page(url, html_text)

            # Parse HTML
            soup = BeautifulSoup(html_text, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            # Get text content
            text = soup.get_text(separator=' ', strip=True)
            # Limit content length
            if len(text) > self.max_content_length:
                text = text[:self.max_content_length]
            # Calculate relevance score
            relevance_score = self._calculate_relevance(text, search_terms)
            # Extract relevant sections
            relevant_content = self._extract_relevant_sections(soup, search_terms, text)
            # Specialized parsing for catalog program pages to produce structured JSON
            structured_data = None
            if "catalog.morgan.edu" in url or "preview_program.php" in url:
                try:
                    structured_data = self._parse_catalog_page(text)
                    if structured_data and any(g in " ".join(search_terms).lower() for g in ["master","graduate","phd","doctor","advanced"]):
                        structured_data = self._filter_undergraduate(structured_data)
                    if structured_data:
                        logger.info(f"[WEB SEARCH] Parsed structured catalog data for {url} (programs: {len(structured_data.get('programs', []))})")
                except Exception as parse_err:
                    logger.warning(f"[WEB SEARCH] Catalog parse failed for {url}: {parse_err}")
            # Get page title
            title = soup.title.string if soup.title else url
            logger.debug(f"[WEB SEARCH] Successfully fetched {url} - relevance: {relevance_score}")
            return {
                "url": url,
                "title": title,
                "content": relevant_content,
                "full_text": text,
                "relevance_score": relevance_score,
                "fetched_at": datetime.utcnow().isoformat(),
                "structured": structured_data
            }
        except httpx.TimeoutException:
            logger.warning(f"[WEB SEARCH] Timeout fetching {url}")
            return {"url": url, "error": "timeout", "relevance_score": 0}
        except httpx.ConnectError as e:
            logger.warning(f"[WEB SEARCH] Connection error for {url}: {str(e)}")
            return {"url": url, "error": "connection_error", "relevance_score": 0}
        except Exception as e:
            logger.error(f"[WEB SEARCH] Error fetching {url}: {str(e)}")
            return {"url": url, "error": str(e), "relevance_score": 0}

    def _get_cached_page(self, url: str) -> Optional[Dict[str, Any]]:
        now = time.time()
        # Redis path
        if self.redis_client:
            try:
                cached_html = self.redis_client.get(f"webcache:html:{url}")
                ts = self.redis_client.get(f"webcache:ts:{url}")
                if cached_html and ts and now - float(ts) < self.cache_ttl_seconds:
                    return {"html": cached_html}
            except Exception:
                pass
        # Memory cache
        entry = self._memory_cache.get(url)
        if entry and now - entry.get("ts", 0) < self.cache_ttl_seconds:
            return entry
        return None

    def _set_cached_page(self, url: str, html: str):
        now = time.time()
        self._memory_cache[url] = {"html": html, "ts": now}
        if self.redis_client:
            try:
                pipe = self.redis_client.pipeline()
                pipe.set(f"webcache:html:{url}", html, ex=self.cache_ttl_seconds)
                pipe.set(f"webcache:ts:{url}", str(now), ex=self.cache_ttl_seconds)
                pipe.execute()
            except Exception:
                pass

    def _parse_catalog_page(self, text: str) -> Dict[str, Any]:
        """Parse Morgan catalog program page into structured JSON."""
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        programs = []
        current_prog = None
        credit_patterns = [
            re.compile(r"^(General Education.*?)(\d+) credits", re.IGNORECASE),
            re.compile(r"^(Supporting Courses.*?)(\d+) credits", re.IGNORECASE),
            re.compile(r"^(Required Courses.*?)(\d+) credits", re.IGNORECASE),
            re.compile(r"^(Total.*?)(\d+)"),
        ]
        course_pattern = re.compile(r"^(?P<code>[A-Z]{2,4}\s?\d{3}[A-Z]?)\s*[\-–]\s*(?P<title>.+?)(?P<credits>\d+)credits", re.IGNORECASE)
        for line in lines:
            if line.lower().startswith("program:"):
                if current_prog:
                    programs.append(current_prog)
                current_prog = {"title": line.split("Program:",1)[1].strip(), "credits": {}, "courses": []}
            else:
                # Credits sections
                for cp in credit_patterns:
                    m = cp.search(line)
                    if m and current_prog:
                        key = m.group(1).strip()
                        val = int(m.group(2))
                        current_prog["credits"][key] = val
                # Course lines
                m2 = course_pattern.search(line)
                if m2 and current_prog:
                    current_prog["courses"].append({
                        "code": m2.group("code"),
                        "title": m2.group("title").rstrip(),
                        "credits": int(m2.group("credits"))
                    })
        if current_prog:
            programs.append(current_prog)
        return {"programs": programs}

    def _filter_undergraduate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        filtered = {"programs": []}
        for prog in data.get("programs", []):
            title_low = prog.get("title","" ).lower()
            if any(k in title_low for k in ["b.s", "bachelor", "undergraduate"]):
                continue
            filtered["programs"].append(prog)
        # If all filtered out, return original to avoid empty context
        return filtered if filtered["programs"] else data
    
    def _extract_search_terms(self, query: str) -> List[str]:
        """Extract important search terms from query"""
        # Remove common words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'should', 'could', 'may', 'might', 'must', 'can', 'what', 'when',
            'where', 'who', 'how', 'why', 'which', 'this', 'that', 'these', 'those',
            'i', 'me', 'my', 'you', 'your'
        }
        
        # Tokenize and filter
        words = re.findall(r'\b\w+\b', query.lower())
        search_terms = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Add important CS-related terms if in query
        important_terms = [
            'computer science', 'cs', 'scmns', 'morgan', 'department',
            'course', 'program', 'degree', 'faculty', 'staff', 'advisor',
            'registration', 'enrollment', 'prerequisite', 'major', 'minor',
            'internship', 'career', 'tutoring', 'organization', 'club'
        ]
        
        for term in important_terms:
            if term in query.lower():
                search_terms.append(term)
        
        return list(set(search_terms))  # Remove duplicates
    
    def _calculate_relevance(self, text: str, search_terms: List[str]) -> float:
        """Calculate relevance score based on term frequency"""
        text_lower = text.lower()
        score = 0.0
        
        for term in search_terms:
            # Count occurrences
            count = text_lower.count(term.lower())
            # Weight by term importance (longer terms = more important)
            weight = len(term) / 5.0
            score += count * weight
        
        # Normalize by text length
        if len(text) > 0:
            score = score / (len(text) / 1000.0)
        
        return round(score, 2)
    
    def _extract_relevant_sections(
        self, 
        soup: BeautifulSoup, 
        search_terms: List[str],
        full_text: str
    ) -> str:
        """Extract the most relevant sections from the page"""
        relevant_sections = []
        
        # Find paragraphs containing search terms
        paragraphs = soup.find_all(['p', 'div', 'section', 'article'])
        
        for para in paragraphs:
            text = para.get_text(strip=True)
            if not text or len(text) < 50:
                continue
            
            # Check if paragraph contains search terms
            text_lower = text.lower()
            term_count = sum(1 for term in search_terms if term.lower() in text_lower)
            
            if term_count > 0:
                relevant_sections.append({
                    'text': text,
                    'score': term_count
                })
        
        # Sort by relevance and take top sections
        relevant_sections.sort(key=lambda x: x['score'], reverse=True)
        top_sections = relevant_sections[:5]
        
        # Combine sections
        if top_sections:
            return '\n\n'.join([s['text'] for s in top_sections])
        
        # Fallback to first 2000 chars of full text
        return full_text[:2000] if full_text else ""
    
    def _combine_results(self, results: List[Dict], query: str) -> str:
        """Combine multiple search results into coherent content"""
        combined = f"Information from Morgan State University Computer Science Department:\n\n"
        
        for i, result in enumerate(results, 1):
            content = result.get("content", "")
            if content:
                combined += f"Source {i} ({result.get('url', 'Unknown')}):\n"
                combined += content
                combined += "\n\n" + "-" * 80 + "\n\n"
        
        return combined
    
    async def search_specific_topic(
        self, 
        topic: str, 
        subtopics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Search for specific topic with optional subtopics
        
        Args:
            topic: Main topic (e.g., "faculty", "courses", "admissions")
            subtopics: Optional list of subtopics to focus on
            
        Returns:
            Structured search results
        """
        # Map topics to specific URLs
        topic_urls = {
            "faculty": [
                "https://www.morgan.edu/scmns/computerscience",
                "https://www.morgan.edu/computer-science/faculty"
            ],
            "courses": [
                "https://www.morgan.edu/computer-science/degrees-and-programs",
                "https://www.morgan.edu/catalogs"
            ],
            "admissions": [
                "https://www.morgan.edu/admissions",
                "https://www.morgan.edu/computer-science/degrees-and-programs"
            ],
            "programs": [
                "https://www.morgan.edu/computer-science/degrees-and-programs"
            ],
            "contact": [
                "https://www.morgan.edu/scmns/computerscience"
            ]
        }
        
        urls = topic_urls.get(topic.lower(), self.morgan_cs_urls)
        
        # Build search query
        query = topic
        if subtopics:
            query += " " + " ".join(subtopics)
        
        search_terms = self._extract_search_terms(query)
        
        # Search specific URLs
        search_tasks = [
            self._fetch_and_search_page(url, search_terms) 
            for url in urls
        ]
        
        results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        # Process results
        valid_results = [r for r in results if isinstance(r, dict) and r.get("content")]
        
        if not valid_results:
            return {
                "success": False,
                "topic": topic,
                "message": f"No information found for topic: {topic}"
            }
        
        # Sort by relevance
        valid_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        return {
            "success": True,
            "topic": topic,
            "content": self._combine_results(valid_results[:3], query),
            "sources": [
                {"url": r["url"], "title": r["title"]}
                for r in valid_results[:3]
            ]
        }
    
    async def verify_information(self, statement: str) -> Dict[str, Any]:
        """
        Verify if a statement is accurate according to Morgan State website
        
        Args:
            statement: Statement to verify
            
        Returns:
            Verification result with supporting evidence
        """
        search_result = await self.search_morgan_website(statement)
        
        if not search_result.get("success"):
            return {
                "verified": False,
                "confidence": 0.0,
                "message": "Could not verify - no information found",
                "statement": statement
            }
        
        # Simple verification based on content similarity
        content = search_result.get("content", "")
        statement_lower = statement.lower()
        
        # Check if key terms from statement appear in content
        statement_terms = self._extract_search_terms(statement)
        matches = sum(1 for term in statement_terms if term.lower() in content.lower())
        confidence = min(matches / len(statement_terms) if statement_terms else 0, 1.0)
        
        return {
            "verified": confidence > 0.5,
            "confidence": round(confidence, 2),
            "supporting_content": content[:500],
            "sources": search_result.get("sources", []),
            "statement": statement
        }
    
    async def deep_search_morgan(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Perform a comprehensive deep search across Morgan State University official websites
        Prioritizes Computer Science department and related academic resources
        
        Args:
            query: User's search query
            max_results: Maximum number of results to return
            
        Returns:
            Comprehensive search results from official Morgan sources
        """
        try:
            logger.info(f"[DEEP SEARCH] Starting deep search for: {query}")
            
            # Extract search terms
            search_terms = self._extract_search_terms(query)
            logger.info(f"[DEEP SEARCH] Search terms: {search_terms}")
            
            # Search Morgan URLs with controlled concurrency to avoid overwhelming the server
            logger.info(f"[DEEP SEARCH] Searching {len(self.morgan_cs_urls)} Morgan State pages...")
            
            # Process URLs in batches to avoid rate limiting
            results = []
            batch_size = self.max_concurrent_requests
            
            for i in range(0, len(self.morgan_cs_urls), batch_size):
                batch_urls = self.morgan_cs_urls[i:i+batch_size]
                logger.debug(f"[DEEP SEARCH] Processing batch {i//batch_size + 1}: {len(batch_urls)} URLs")
                
                # Add small delay between batches to be respectful to the server
                if i > 0:
                    await asyncio.sleep(0.5)
                
                batch_tasks = [
                    self._fetch_and_search_page(url, search_terms) 
                    for url in batch_urls
                ]
                
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                results.extend(batch_results)
            
            # Filter and process results
            valid_results = []
            error_count = 0
            
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"[DEEP SEARCH] Exception during search: {str(result)}")
                    error_count += 1
                    continue
                    
                if isinstance(result, dict):
                    if result.get("error"):
                        error_count += 1
                        logger.debug(f"[DEEP SEARCH] Error from {result.get('url')}: {result.get('error')}")
                        continue
                        
                    if result.get("content"):
                        # Only include results with meaningful relevance
                        if result.get("relevance_score", 0) > 0.05:  # Lower threshold for better coverage
                            valid_results.append(result)
                            logger.info(f"[DEEP SEARCH] Found relevant content from {result.get('url')}: score={result.get('relevance_score')}")
            
            logger.info(f"[DEEP SEARCH] Summary: {len(valid_results)} relevant results, {error_count} errors out of {len(results)} total")
            
            if not valid_results:
                logger.warning(f"[DEEP SEARCH] No relevant results found for: {query}")
                return {
                    "success": False,
                    "message": f"No relevant information found on Morgan State official websites. Searched {len(self.morgan_cs_urls)} pages, {error_count} had connection errors.",
                    "query": query,
                    "sources": [],
                    "searched_urls": len(self.morgan_cs_urls),
                    "errors": error_count
                }
            
            # Sort by relevance score (highest first)
            valid_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
            
            # Take top results
            top_results = valid_results[:max_results]
            logger.info(f"[DEEP SEARCH] Using top {len(top_results)} results out of {len(valid_results)} valid results")
            
            # Combine content in a structured way
            combined_content = self._combine_deep_search_results(top_results, query)
            
            return {
                "success": True,
                "content": combined_content,
                "sources": [
                    {
                        "url": r["url"],
                        "title": r["title"],
                        "relevance_score": r["relevance_score"]
                    }
                    for r in top_results
                ],
                "query": query,
                "total_sources_checked": len(self.morgan_cs_urls),
                "relevant_sources_found": len(valid_results),
                "search_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"[DEEP SEARCH] Error during deep search: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "sources": []
            }
    
    def _combine_deep_search_results(self, results: List[Dict], query: str) -> str:
        """
        Combine deep search results with better structure and context
        
        Args:
            results: List of search result dictionaries
            query: Original query
            
        Returns:
            Formatted combined content
        """
        combined = f"=== COMPREHENSIVE SEARCH RESULTS FROM MORGAN STATE UNIVERSITY OFFICIAL WEBSITES ===\n\n"
        combined += f"Query: {query}\n"
        combined += f"Sources found: {len(results)}\n\n"
        
        for i, result in enumerate(results, 1):
            content = result.get("content", "")
            if content:
                url = result.get('url', 'Unknown')
                title = result.get('title', 'Unknown Page')
                score = result.get('relevance_score', 0)
                
                combined += f"[{i}] {title}\n"
                combined += f"URL: {url}\n"
                combined += f"Relevance Score: {score}\n"
                structured = result.get("structured")
                if structured and structured.get("programs"):
                    try:
                        combined += "Structured Programs JSON:\n"
                        combined += json.dumps(structured, indent=2) + "\n"
                    except Exception:
                        pass
                combined += f"\n{content}\n"
                combined += "\n" + "="*100 + "\n\n"
        
        combined += f"\nIMPORTANT: All information above is from official Morgan State University sources.\n"
        combined += f"Always cite the specific source URL when providing information to the user.\n"
        
        return combined
