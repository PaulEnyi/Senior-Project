"""
Script to ingest knowledge base data into Pinecone
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from pinecone import Pinecone
from openai import OpenAI
import json

# Load environment variables
load_dotenv()

def load_knowledge_base():
    """Load knowledge base from JSON file"""
    kb_path = Path(__file__).parent.parent / "data" / "knowledge_base.json"
    
    if not kb_path.exists():
        print(f"ERROR: Knowledge base file not found at {kb_path}")
        print("Creating sample knowledge base...")
        
        # Create data directory if it doesn't exist
        kb_path.parent.mkdir(exist_ok=True)
        
        # Create sample knowledge base
        sample_kb = {
            "department_info": [
                {
                    "title": "Computer Science Department Overview",
                    "content": "The Morgan State University Computer Science Department is located in the Science Center. We offer undergraduate and graduate programs in Computer Science.",
                    "category": "department_info"
                }
            ],
            "faculty": [
                {
                    "title": "Computer Science Faculty",
                    "content": "The CS department has experienced faculty members specializing in various areas of computer science including AI, cybersecurity, and software engineering.",
                    "category": "faculty"
                }
            ]
        }
        
        with open(kb_path, 'w') as f:
            json.dump(sample_kb, f, indent=2)
        
        print(f"Sample knowledge base created at {kb_path}")
        return sample_kb
    
    with open(kb_path, 'r') as f:
        return json.load(f)

def create_embeddings(texts, openai_client):
    """Create embeddings using OpenAI"""
    embeddings = []
    
    for text in texts:
        response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        embeddings.append(response.data[0].embedding)
    
    return embeddings

def ingest_data():
    """Ingest knowledge base data into Pinecone"""
    
    # Get configuration
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME", "morgan-ai-knowledge")
    
    if not pinecone_api_key:
        print("ERROR: PINECONE_API_KEY not found in .env file")
        sys.exit(1)
    
    if not openai_api_key:
        print("ERROR: OPENAI_API_KEY not found in .env file")
        sys.exit(1)
    
    print("Loading knowledge base...")
    kb_data = load_knowledge_base()
    
    # Initialize clients
    pc = Pinecone(api_key=pinecone_api_key)
    openai_client = OpenAI(api_key=openai_api_key)
    
    # Connect to index
    try:
        index = pc.Index(index_name)
    except Exception as e:
        print(f"ERROR: Could not connect to index '{index_name}'")
        print("Please run setup_pinecone.py first")
        sys.exit(1)
    
    print(f"Connected to index: {index_name}")
    
    # Prepare documents for ingestion
    documents = []
    for category, items in kb_data.items():
        for item in items:
            documents.append({
                "id": f"{category}_{len(documents)}",
                "text": f"{item['title']}\n\n{item['content']}",
                "metadata": {
                    "title": item['title'],
                    "category": item.get('category', category)
                }
            })
    
    print(f"Processing {len(documents)} documents...")
    
    # Create embeddings and upsert
    batch_size = 100
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        
        print(f"Processing batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")
        
        # Create embeddings
        texts = [doc["text"] for doc in batch]
        embeddings = create_embeddings(texts, openai_client)
        
        # Prepare vectors for upsert
        vectors = []
        for doc, embedding in zip(batch, embeddings):
            vectors.append({
                "id": doc["id"],
                "values": embedding,
                "metadata": {
                    "text": doc["text"],
                    **doc["metadata"]
                }
            })
        
        # Upsert to Pinecone
        index.upsert(vectors=vectors)
        print(f"Upserted {len(vectors)} vectors")
    
    # Get final stats
    stats = index.describe_index_stats()
    print(f"\nIngestion complete!")
    print(f"Total vectors in index: {stats.get('total_vector_count', 0)}")
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("Morgan AI - Knowledge Base Ingestion")
    print("=" * 60)
    
    try:
        success = ingest_data()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        sys.exit(1)