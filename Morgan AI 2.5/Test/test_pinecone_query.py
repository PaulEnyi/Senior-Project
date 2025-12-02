"""Quick semantic query test to confirm Pinecone is used before web search.

Run locally:
  python .\Test\test_pinecone_query.py
"""
import asyncio
import sys
sys.path.insert(0, 'BackEnd/app')

from app.services.openai_service import OpenAIService

async def run():
    svc = OpenAIService()
    query = "What are the graduation requirements for the BS in Computer Science?"
    print(f"Query: {query}\n")
    # Call the RAG helper to observe KB vs web search behavior
    context = await svc._get_rag_context(query, top_k=5)
    source_hint = "KB context" if "[DEEP SEARCH" not in context and "[Deep Search" not in context else "Web search fallback"
    print(f"Source path: {source_hint}\n")
    print("=== Returned Context (first 800 chars) ===")
    print(context[:800])
    print("\n=== Done ===")

if __name__ == "__main__":
    asyncio.run(run())
    print("Source count:", len(r.get('sources', [])))
    if r.get('sources'):
        print("Top sources:")
        for i, src in enumerate(r['sources'][:3], 1):
            print(f"  {i}.", src.get('source') or src.get('url') or src)
    print("\nFirst 400 chars of response:\n", (r.get('response') or '')[:400])

if __name__ == '__main__':
    asyncio.run(run())
