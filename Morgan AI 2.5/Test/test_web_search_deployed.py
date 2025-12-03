import asyncio
import sys
sys.path.insert(0, 'BackEnd/app')

from app.services.web_search_service import WebSearchService

async def test_faculty_search():
    """Test faculty query with deployed code"""
    service = WebSearchService()
    
    # Test faculty query
    query = "Who are the faculty members in Computer Science?"
    print(f"\n🔍 Testing Query: {query}")
    print("=" * 60)
    
    results = await service.deep_search_morgan(query, search_terms=["faculty", "Computer Science"])
    
    print(f"\n✅ Results found: {len(results)}")
    for i, result in enumerate(results[:3], 1):
        print(f"\n{i}. {result.get('title', 'No title')}")
        print(f"   URL: {result.get('url')}")
        print(f"   Score: {result.get('relevance_score')}")
        content = result.get('content', '')[:200]
        print(f"   Content: {content}...")
        
        # Check if it's faculty-and-staff page
        if 'faculty-and-staff' in result.get('url', ''):
            print("   ✅ THIS IS THE FACULTY-AND-STAFF PAGE (CORRECT!)")
        elif 'academic-adviser' in result.get('url', ''):
            print("   ℹ️  This is academic-advisers (backup)")

if __name__ == "__main__":
    asyncio.run(test_faculty_search())
