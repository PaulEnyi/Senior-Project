from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone as LangchainPinecone
from typing import List, Dict, Any, Optional, Tuple
import logging
import json
import os
from ..core.config import settings
from ..core.exceptions import KnowledgeBaseException
from .pinecone_service import PineconeService
from .openai_service import OpenAIService

logger = logging.getLogger(__name__)

class LangChainRAGService:
    """Service for handling RAG (Retrieval-Augmented Generation) operations using LangChain"""
    
    def __init__(self):
        self.openai_service = OpenAIService()
        self.pinecone_service = PineconeService()
        
        # Initialize LangChain components
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.CHAT_TEMPERATURE,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        self.embeddings = OpenAIEmbeddings(
            model=settings.OPENAI_EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Text splitter for processing documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Memory for conversation
        self.memory = ConversationBufferWindowMemory(
            k=5,  # Remember last 5 exchanges
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
    
    async def process_knowledge_base(self, knowledge_base_path: str = None) -> bool:
        """Process and ingest the knowledge base documents"""
        try:
            if not knowledge_base_path:
                knowledge_base_path = os.path.join(
                    settings.KNOWLEDGE_BASE_PATH, 
                    settings.TRAINING_DATA_FILE
                )
            
            logger.info(f"Processing knowledge base from: {knowledge_base_path}")
            
            # Load documents from various sources
            documents = []
            
            # Process main training data file
            if os.path.exists(knowledge_base_path):
                with open(knowledge_base_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    doc = Document(
                        page_content=content,
                        metadata={
                            'source': 'training_data.txt',
                            'category': 'general',
                            'title': 'Morgan State CS Training Data'
                        }
                    )
                    documents.append(doc)
            
            # Process JSON knowledge base files
            knowledge_dirs = [
                'department_info',
                'academics', 
                'student_resources',
                'administrative'
            ]
            
            for dir_name in knowledge_dirs:
                dir_path = os.path.join(settings.KNOWLEDGE_BASE_PATH, dir_name)
                if os.path.exists(dir_path):
                    documents.extend(await self._process_json_directory(dir_path, dir_name))
            
            logger.info(f"Loaded {len(documents)} documents")
            
            # Split documents into chunks
            split_documents = self.text_splitter.split_documents(documents)
            logger.info(f"Split into {len(split_documents)} chunks")
            
            # Convert to format for Pinecone
            doc_dicts = []
            for i, doc in enumerate(split_documents):
                doc_dict = {
                    'id': f"doc_{i}",
                    'content': doc.page_content,
                    'category': doc.metadata.get('category', 'general'),
                    'source': doc.metadata.get('source', 'unknown'),
                    'title': doc.metadata.get('title', ''),
                    'last_updated': doc.metadata.get('last_updated', '')
                }
                doc_dicts.append(doc_dict)
            
            # Generate embeddings
            texts = [doc['content'] for doc in doc_dicts]
            embeddings = await self.openai_service.generate_embeddings(texts)
            
            # Clear existing data and upsert new data
            await self.pinecone_service.clear_index()
            await self.pinecone_service.upsert_documents(doc_dicts, embeddings)
            
            logger.info("Knowledge base processing completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process knowledge base: {str(e)}")
            raise KnowledgeBaseException(f"Failed to process knowledge base: {str(e)}")
    
    async def _process_json_directory(self, directory_path: str, category: str) -> List[Document]:
        """Process JSON files in a directory"""
        documents = []
        
        try:
            for filename in os.listdir(directory_path):
                if filename.endswith('.json'):
                    file_path = os.path.join(directory_path, filename)
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Convert JSON data to text content
                    content = self._json_to_text(data, filename)
                    
                    doc = Document(
                        page_content=content,
                        metadata={
                            'source': filename,
                            'category': category,
                            'title': filename.replace('.json', '').replace('_', ' ').title()
                        }
                    )
                    documents.append(doc)
                    
        except Exception as e:
            logger.error(f"Error processing directory {directory_path}: {str(e)}")
        
        return documents
    
    def _json_to_text(self, data: Any, filename: str) -> str:
        """Convert JSON data to readable text"""
        if isinstance(data, dict):
            text_parts = [f"Information from {filename}:"]
            
            for key, value in data.items():
                if isinstance(value, (str, int, float)):
                    text_parts.append(f"{key.replace('_', ' ').title()}: {value}")
                elif isinstance(value, list):
                    text_parts.append(f"{key.replace('_', ' ').title()}:")
                    for item in value:
                        if isinstance(item, str):
                            text_parts.append(f"  • {item}")
                        elif isinstance(item, dict):
                            text_parts.append(f"  • {self._dict_to_text(item)}")
                elif isinstance(value, dict):
                    text_parts.append(f"{key.replace('_', ' ').title()}:")
                    text_parts.append(f"  {self._dict_to_text(value)}")
            
            return "\n".join(text_parts)
        
        elif isinstance(data, list):
            return f"Information from {filename}:\n" + "\n".join([
                f"• {item}" if isinstance(item, str) else f"• {self._dict_to_text(item)}"
                for item in data
            ])
        
        else:
            return str(data)
    
    def _dict_to_text(self, d: Dict) -> str:
        """Convert a dictionary to readable text"""
        parts = []
        for key, value in d.items():
            if isinstance(value, (str, int, float)):
                parts.append(f"{key.replace('_', ' ')}: {value}")
            elif isinstance(value, list):
                parts.append(f"{key.replace('_', ' ')}: {', '.join(map(str, value))}")
        return "; ".join(parts)
    
    async def get_relevant_context(
        self, 
        query: str, 
        max_results: int = 5,
        category_filter: str = None
    ) -> str:
        """Get relevant context for a query using vector search"""
        try:
            # Search for relevant documents
            results = await self.pinecone_service.search_by_text_query(
                query=query,
                openai_service=self.openai_service,
                top_k=max_results,
                category_filter=category_filter
            )
            
            if not results:
                return "No relevant information found in the knowledge base."
            
            # Combine results into context
            context_parts = []
            for result in results:
                context_parts.append(f"[Source: {result['source']}]")
                context_parts.append(result['content'])
                context_parts.append("")  # Empty line for separation
            
            context = "\n".join(context_parts)
            
            # Truncate if too long
            max_context_length = 3000  # Adjust based on token limits
            if len(context) > max_context_length:
                context = context[:max_context_length] + "\n...[Context truncated]"
            
            logger.info(f"Generated context of {len(context)} characters from {len(results)} sources")
            return context
            
        except Exception as e:
            logger.error(f"Failed to get relevant context: {str(e)}")
            return f"Error retrieving context: {str(e)}"
    
    async def generate_rag_response(
        self,
        query: str,
        conversation_history: List[Dict[str, str]] = None,
        category_filter: str = None
    ) -> Tuple[str, str]:
        """Generate response using RAG (Retrieval-Augmented Generation)"""
        try:
            # Get relevant context
            context = await self.get_relevant_context(
                query=query,
                category_filter=category_filter
            )
            
            # Build conversation messages
            messages = []
            
            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history[-6:])  # Last 6 messages
            
            # Add current query
            messages.append({"role": "user", "content": query})
            
            # Generate response with context
            response = await self.openai_service.generate_chat_response(
                messages=messages,
                context=context
            )
            
            return response, context
            
        except Exception as e:
            logger.error(f"Failed to generate RAG response: {str(e)}")
            raise KnowledgeBaseException(f"Failed to generate response: {str(e)}")
    
    async def suggest_related_questions(self, query: str) -> List[str]:
        """Suggest related questions based on the current query"""
        try:
            # Get relevant documents
            results = await self.pinecone_service.search_by_text_query(
                query=query,
                openai_service=self.openai_service,
                top_k=3
            )
            
            if not results:
                return []
            
            # Generate related questions using GPT
            context = "\n".join([result['content'] for result in results])
            
            prompt = f"""Based on the user's query: "{query}"
            And this relevant information about Morgan State University Computer Science:
            {context[:1000]}
            
            Suggest 3 related questions that a student might ask. Format as a simple list:
            1. Question 1
            2. Question 2
            3. Question 3"""
            
            response = await self.openai_service.generate_chat_response(
                messages=[{"role": "user", "content": prompt}],
                system_prompt="You are a helpful assistant that suggests related questions for students."
            )
            
            # Parse the response to extract questions
            questions = []
            lines = response.strip().split('\n')
            for line in lines:
                if line.strip() and any(line.startswith(str(i)) for i in range(1, 6)):
                    # Remove numbering and clean up
                    question = line.split('.', 1)[-1].strip()
                    if question:
                        questions.append(question)
            
            return questions[:3]  # Return max 3 questions
            
        except Exception as e:
            logger.error(f"Failed to suggest related questions: {str(e)}")
            return []