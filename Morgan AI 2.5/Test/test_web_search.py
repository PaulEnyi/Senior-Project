"""Test web search functionality"""
import asyncio
import sys
sys.path.insert(0, 'app')
from app.services.web_search_service import WebSearchService

async def test_web_search():
    print("=== TESTING WEB SEARCH FALLBACK ===\n")
    
    ws = WebSearchService()
    
    # Test query that should trigger web search
    query = "What are the admission requirements for Master of Science in Computer Science?"
    print(f"Query: {query}\n")
    
    result = await ws.deep_search_morgan(query, max_results=3)
    
    print(f"Success: {result.get('success')}")
    print(f"Total sources checked: {result.get('total_sources_checked', 0)}")
    print(f"Relevant sources found: {result.get('relevant_sources_found', 0)}")
    
    if result.get('sources'):
        print(f"\nTop {len(result['sources'])} sources:")
        for i, source in enumerate(result['sources'], 1):
            print(f"  {i}. {source.get('title')}")
            print(f"     URL: {source.get('url')}")
            print(f"     Relevance: {source.get('relevance_score', 0):.3f}")
        
        content_len = len(result.get('content', ''))
        print(f"\nTotal content length: {content_len} characters")
        
        if content_len > 0:
            print("\nFirst 800 characters of content:")
            print("-" * 80)
            print(result.get('content', '')[:800])
            print("-" * 80)
    else:
        print(f"\nNo sources found")
        if result.get('error'):
            print(f"Error: {result['error']}")

if __name__ == "__main__":
    asyncio.run(test_web_search())
