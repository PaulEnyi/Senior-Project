#!/usr/bin/env python3
"""Direct test of web search faculty extraction"""

import sys
import asyncio
sys.path.insert(0, '/app')

from app.services.web_search_service import WebSearchService

async def test():
    web_search = WebSearchService()
    
    query = "Who are the faculty members in Computer Science?"
    print(f"Query: {query}\n")
    print("="*80)
    print("Deep Search Results:\n")
    
    results = await web_search.deep_search_morgan(query)
    
    print(f"Total results: {len(results)}")
    
    # Show first 3 results
    for i, result in enumerate(results[:3], 1):
        url = result.get('url', 'N/A')
        error = result.get('error')
        score = result.get('relevance_score', 0)
        text = result.get('text', '')
        
        print(f"\n[{i}] {url}")
        print(f"    Score: {score:.2f}")
        if error:
            print(f"    Error: {error}")
        else:
            # Show first 500 chars
            preview = text[:500].replace('\n', ' ')
            print(f"    Length: {len(text)} chars")
            print(f"    Preview: {preview}...")
            
            # Check for faculty keywords
            if "dr." in text.lower() or "professor" in text.lower():
                print(f"    ✓ Contains faculty information")

asyncio.run(test())
