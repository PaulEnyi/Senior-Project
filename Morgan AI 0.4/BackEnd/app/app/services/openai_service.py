import os
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import openai
from openai import AsyncOpenAI
import numpy as np
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.services.thread_manager import ThreadManager
from app.services.pinecone_service import PineconeService

logger = logging.getLogger(__name__)

class OpenAIService:
    """Service for handling OpenAI operations including Realtime API"""
    
    def __init__(self):
        """Initialize OpenAI service"""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.thread_manager = ThreadManager()
        self.pinecone_service = PineconeService()
        
        # Model configurations
        self.chat_model = settings.OPENAI_MODEL
        self.embedding_model = settings.OPENAI_EMBEDDING_MODEL
        self.tts_model = settings.OPENAI_TTS_MODEL
        self.tts_voice = settings.OPENAI_TTS_VOICE
        self.stt_model = settings.OPENAI_STT_MODEL
        
        # Realtime API settings
        self.realtime_enabled = settings.OPENAI_REALTIME_ENABLED
        
        # System prompt for Morgan AI
        self.system_prompt = self._get_system_prompt()
        
        logger.info("OpenAI service initialized")
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the Morgan AI assistant"""
        return """You are the Morgan AI Assistant, a helpful and knowledgeable AI assistant for the 
        Computer Science Department at Morgan State University. Your role is to:
        
        1. Provide accurate information about CS courses, prerequisites, and degree requirements
        2. Help students with registration, academic planning, and advising
        3. Share information about faculty, office hours, and contact details
        4. Inform about internships, career opportunities, and professional development
        5. Guide students to appropriate resources and support services
        6. Provide information about department events, deadlines, and important dates
        
        Always be professional, supportive, and encouraging. If you're unsure about specific 
        Morgan State policies or information, suggest contacting the department directly.
        
        Remember: You represent Morgan State University's Computer Science Department."""
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_chat_response(
        self,
        message: str,
        session_id: str,
        user_id: Optional[str] = None,
        use_rag: bool = True
    ) -> Dict[str, Any]:
        """Generate a chat response using GPT-4"""
        import traceback
        try:
                logger.info(f"[MorganAI] Starting chat response for session_id={session_id}, user_id={user_id}")
                # Get conversation history
                history = await self.thread_manager.get_messages(session_id, limit=10)
                logger.info(f"[MorganAI] History type: {type(history)}, value: {history}")
                # Build messages array
                messages = [{"role": "system", "content": self.system_prompt}]
                if history:
                    for msg in history:
                        logger.info(f"[MorganAI] Processing history msg type: {type(msg)}, value: {msg}")
                        if hasattr(msg, 'role') and hasattr(msg, 'content'):
                            messages.append({
                                "role": msg.role,
                                "content": msg.content
                            })
                        else:
                            logger.warning(f"[MorganAI] History message missing attributes: {msg}")
                # If RAG is enabled, get context from knowledge base
                context = ""
                if use_rag:
                    try:
                        context = await self._get_rag_context(message)
                        logger.info(f"[MorganAI] RAG context: {context}")
                        if context:
                            messages.append({
                                "role": "system",
                                "content": f"Context from knowledge base:\n{context}"
                            })
                    except Exception as rag_err:
                        logger.error(f"[MorganAI] Error getting RAG context: {rag_err}\n{traceback.format_exc()}")
                # Add current message
                messages.append({"role": "user", "content": message})
                logger.info(f"[MorganAI] Messages for OpenAI: {messages}")
                # Generate response
                try:
                    response = await self.client.chat.completions.create(
                        model=self.chat_model,
                        messages=messages,
                        max_tokens=settings.OPENAI_MAX_TOKENS,
                        temperature=settings.OPENAI_TEMPERATURE,
                        stream=False
                    )
                    logger.info(f"[MorganAI] OpenAI response: {response}")
                    ai_response = response.choices[0].message.content
                except Exception as openai_err:
                    logger.error(f"[MorganAI] Error in OpenAI API call: {openai_err}\n{traceback.format_exc()}")
                    raise
                # Store in thread
                try:
                    from app.models.chat import ChatMessage
                    user_msg = ChatMessage(
                        role="user",
                        content=message,
                        timestamp=datetime.utcnow(),
                        user_id=user_id
                    )
                    assistant_msg = ChatMessage(
                        role="assistant",
                        content=ai_response,
                        timestamp=datetime.utcnow(),
                        user_id=user_id
                    )
                    await self.thread_manager.add_message(session_id, user_msg)
                    await self.thread_manager.add_message(session_id, assistant_msg)
                except Exception as thread_err:
                    logger.error(f"[MorganAI] Error storing messages in thread: {thread_err}\n{traceback.format_exc()}")
                    raise
                logger.info(f"[MorganAI] Chat response completed successfully.")
                return {
                    "success": True,
                    "response": ai_response,
                    "session_id": session_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "context_used": bool(context),
                    "model": self.chat_model
                }
        except Exception as e:
            logger.error(f"[MorganAI] Error generating chat response: {e}\n{traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "response": "I apologize, but I encountered an error. Please try again."
            }
    
    async def _get_rag_context(self, query: str, top_k: int = 5) -> str:
        """Get relevant context from knowledge base using RAG"""
        try:
            # Generate embedding for query
            embedding = await self.generate_embedding(query)
            logger.info(f"[MorganAI RAG] Generated embedding of length {len(embedding)} for query: {query[:50]}...")
            
            # Query Pinecone for similar documents (synchronous call)
            results = self.pinecone_service.query_vectors(
                query_embedding=embedding,
                top_k=top_k
            )
            logger.info(f"[MorganAI RAG] Query returned {len(results)} results")
            
            # Format context
            context_parts = []
            for i, match in enumerate(results):
                metadata = match.get("metadata") if isinstance(match, dict) else None
                score = match.get("score", 0)
                logger.info(f"[MorganAI RAG] Result {i+1}: score={score}, has_metadata={metadata is not None}")
                
                if metadata:
                    text = metadata.get("text", "")
                    source = metadata.get("source", "Unknown")
                    logger.info(f"[MorganAI RAG] Result {i+1}: source={source}, text_len={len(text)}")
                    
                    # Lower threshold to 0.5 to see more results
                    if score and score > 0.5:  
                        context_parts.append(f"[Source: {source}]\n{text}")
                        logger.info(f"[MorganAI RAG] Added result {i+1} to context (score {score} > 0.5)")
                    else:
                        logger.info(f"[MorganAI RAG] Skipped result {i+1} (score {score} <= 0.5)")
            
            final_context = "\n\n".join(context_parts)
            logger.info(f"[MorganAI RAG] Final context length: {len(final_context)} chars, {len(context_parts)} sources")
            return final_context
        except Exception as e:
            logger.error(f"Error getting RAG context: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return ""
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI"""
        try:
            response = await self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    async def create_embedding(self, text: str) -> List[float]:
        """Alias for generate_embedding - creates an embedding for the given text
        
        This is an alias method to maintain compatibility with different naming conventions
        """
        return await self.generate_embedding(text)
    
    async def text_to_speech(
        self,
        text: str,
        voice: Optional[str] = None
    ) -> bytes:
        """Convert text to speech using OpenAI TTS"""
        try:
            voice = voice or self.tts_voice
            
            response = await self.client.audio.speech.create(
                model=self.tts_model,
                voice=voice,
                input=text
            )
            
            return response.content
            
        except Exception as e:
            logger.error(f"Error in text-to-speech: {e}")
            raise
    
    async def speech_to_text(
        self,
        audio_data: bytes,
        language: str = "en"
    ) -> str:
        """Convert speech to text using OpenAI Whisper"""
        try:
            # Create a temporary file for audio
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_file.write(audio_data)
                tmp_file_path = tmp_file.name
            
            # Transcribe audio
            with open(tmp_file_path, "rb") as audio_file:
                response = await self.client.audio.transcriptions.create(
                    model=self.stt_model,
                    file=audio_file,
                    language=language
                )
            
            # Clean up temporary file
            os.remove(tmp_file_path)
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error in speech-to-text: {e}")
            raise
    
    async def process_realtime_message(
        self,
        message: str,
        session_id: str,
        voice_enabled: bool = False
    ) -> Dict[str, Any]:
        """Process a realtime message with optional voice response"""
        try:
            # Generate text response
            response_data = await self.generate_chat_response(
                message=message,
                session_id=session_id,
                use_rag=True
            )
            
            if not response_data["success"]:
                return response_data
            
            # If voice is enabled, generate audio
            if voice_enabled and self.realtime_enabled:
                try:
                    audio_data = await self.text_to_speech(response_data["response"])
                    response_data["audio"] = audio_data
                    response_data["audio_format"] = "mp3"
                except Exception as e:
                    logger.error(f"Error generating voice response: {e}")
                    response_data["voice_error"] = str(e)
            
            return response_data
            
        except Exception as e:
            logger.error(f"Error processing realtime message: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "I encountered an error processing your message."
            }
    
    async def process_realtime_audio(
        self,
        audio_data: bytes,
        session_id: str
    ) -> Dict[str, Any]:
        """Process realtime audio input and generate audio response"""
        try:
            # Convert speech to text
            transcript = await self.speech_to_text(audio_data)
            
            if not transcript:
                return {
                    "success": False,
                    "error": "Could not transcribe audio"
                }
            
            # Generate response
            response_data = await self.generate_chat_response(
                message=transcript,
                session_id=session_id,
                use_rag=True
            )
            
            if not response_data["success"]:
                return response_data
            
            # Generate audio response
            audio_response = await self.text_to_speech(response_data["response"])
            
            return {
                "success": True,
                "transcript": transcript,
                "response": response_data["response"],
                "audio": audio_response,
                "audio_format": "mp3",
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing realtime audio: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_welcome_message(
        self,
        user_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a welcome message with optional voice"""
        try:
            # Create welcome text
            if user_name:
                welcome_text = f"Hello {user_name}, welcome back to the Morgan State University Computer Science Department assistant. How can I help you today?"
            else:
                welcome_text = "Hello, welcome to the Morgan State University Computer Science Department assistant. How can I help you today?"
            
            # Generate audio if enabled
            audio_data = None
            if self.realtime_enabled:
                try:
                    audio_data = await self.text_to_speech(welcome_text)
                except Exception as e:
                    logger.error(f"Error generating welcome audio: {e}")
            
            return {
                "success": True,
                "message": welcome_text,
                "audio": audio_data,
                "audio_format": "mp3" if audio_data else None
            }
            
        except Exception as e:
            logger.error(f"Error generating welcome message: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Welcome to Morgan AI Assistant!"
            }
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of user message"""
        try:
            response = await self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {
                        "role": "system",
                        "content": "Analyze the sentiment of the following text. Return a JSON with 'sentiment' (positive/negative/neutral) and 'score' (0-1)."
                    },
                    {"role": "user", "content": text}
                ],
                max_tokens=100,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {"sentiment": "neutral", "score": 0.5}
    
    async def summarize_conversation(
        self,
        session_id: str,
        max_length: int = 500
    ) -> str:
        """Generate a summary of the conversation"""
        try:
            # Get conversation history
            messages = await self.thread_manager.get_messages(session_id)
            
            if not messages:
                return "No conversation to summarize."
            
            # Format conversation
            conversation_text = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in messages
            ])
            
            # Generate summary
            response = await self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {
                        "role": "system",
                        "content": f"Summarize the following conversation in {max_length} characters or less."
                    },
                    {"role": "user", "content": conversation_text}
                ],
                max_tokens=200,
                temperature=0.5
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error summarizing conversation: {e}")
            return "Error generating summary."