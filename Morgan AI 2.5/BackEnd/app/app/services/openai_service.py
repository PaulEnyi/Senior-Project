import os
import json
import asyncio
import logging
import uuid
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import openai
from openai import AsyncOpenAI
import numpy as np
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.services.thread_manager import ThreadManager
from app.services.pinecone_service import PineconeService
from app.services.web_search_service import WebSearchService

logger = logging.getLogger(__name__)

class OpenAIService:
    """Service for handling OpenAI operations including Realtime API"""
    
    def __init__(self):
        """Initialize OpenAI service"""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.thread_manager = ThreadManager()
        self.pinecone_service = PineconeService()
        self.web_search_service = WebSearchService()
        
        # Model configurations
        self.chat_model = settings.OPENAI_MODEL
        self.embedding_model = settings.OPENAI_EMBEDDING_MODEL
        self.tts_model = settings.OPENAI_TTS_MODEL
        self.tts_voice = settings.OPENAI_TTS_VOICE
        self.stt_model = settings.OPENAI_STT_MODEL
        
        # Realtime API settings
        self.realtime_enabled = settings.OPENAI_REALTIME_ENABLED
        self._realtime_sessions: Dict[str, Dict[str, Any]] = {}
        
        # System prompt for Morgan AI
        self.system_prompt = self._get_system_prompt()
        
        logger.info("OpenAI service initialized with web search fallback")

    def _now_iso(self) -> str:
        """Precise UTC timestamp in ISO-8601 with milliseconds and 'Z'."""
        return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    
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
        7. Answer student-specific questions using their uploaded Degree Works transcript
        
        IMPORTANT SEARCH & RESPONSE GUIDELINES:
        - ALWAYS provide complete, helpful answers - never refuse to answer questions about Morgan State CS
        - When information is available from the knowledge base, use it as the primary source
        - When knowledge base information is insufficient or missing, web search results from Morgan State official websites (catalog.morgan.edu, www.morgan.edu/scmns/computerscience, etc.) will AUTOMATICALLY be retrieved
        - ALWAYS integrate web search results naturally into your response when provided
        - ALWAYS cite specific sources with URLs when using web search information (e.g., "According to the Morgan State CS Catalog (catalog.morgan.edu)..." or "Based on the department website (morgan.edu/scmns/computerscience)...")
        - For course inquiries (e.g., COSC 300, CSC 300): If not in knowledge base, web search will pull from Morgan State CS Catalog and Department pages
        - For program/admission questions: Automatically search Morgan State official sources for latest information
        - For any Morgan State CS information: Prioritize official Morgan State University sources over general information
        - If information isn't found in EITHER knowledge base OR web search, acknowledge the limitation and suggest contacting the CS Department directly
        - Be professional, supportive, and encouraging
        - Provide 100% accurate answers by utilizing ALL available context and sources
        - When multiple sources are provided, synthesize the information coherently
        
        DEGREE WORKS TRANSCRIPT ANALYSIS:
        - When a student's Degree Works data is provided in the "Student's Academic Record" section, use it to answer personalized questions
        - For questions like "Did I take COSC 111?" or "Have I completed Data Structures?", check the COMPLETED COURSES list in their Degree Works
        - For questions like "What courses am I taking now?", check the IN-PROGRESS COURSES list
        - For questions like "What do I still need to take?", check the REMAINING REQUIRED COURSES list
        - Always reference specific course codes, names, and grades from their transcript when answering
        - If asked about courses not in their transcript, clearly state "According to your Degree Works transcript, you have not taken [course name] yet"
        - Use their actual GPA, credits completed, and classification from their transcript
        - If no Degree Works data is available for a student, let them know they can upload their transcript for personalized academic guidance
        
        Remember: You represent Morgan State University's Computer Science Department and should always
        strive to give students the most accurate, comprehensive, and helpful information possible by using
        ALL available resources including knowledge base, web search results, internship data, and degree works information."""

    @property
    def realtime_available(self) -> bool:
        return self.realtime_enabled

    async def create_realtime_session(self, user_id: str) -> Dict[str, Any]:
        if not self.realtime_enabled:
            raise RuntimeError("Realtime not enabled")
        session_id = f"rt_{uuid.uuid4().hex}"
        ephemeral_key = f"epk_{uuid.uuid4().hex}"
        expires_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        data = {
            "session_id": session_id,
            "user_id": user_id,
            "ephemeral_key": ephemeral_key,
            "expires_at": expires_at,
            "created_at": time.time(),
            "websocket_url": f"/ws/voice/{session_id}"
        }
        self._realtime_sessions[session_id] = data
        return data

    async def close_realtime_session(self, session_id: str) -> None:
        self._realtime_sessions.pop(session_id, None)
    
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
                
                # Get Degree Works context if available
                if user_id:
                    try:
                        degree_works_context = await self._get_degree_works_context(user_id)
                        if degree_works_context:
                            logger.info(f"[MorganAI] Adding Degree Works context for user {user_id}")
                            messages.append({
                                "role": "system",
                                "content": f"Student's Academic Record:\n{degree_works_context}"
                            })
                    except Exception as dw_err:
                        logger.warning(f"[MorganAI] Could not retrieve Degree Works context: {dw_err}")
                
                # Get latest internship opportunities context
                try:
                    internship_context = await self._get_internship_context()
                    if internship_context:
                        logger.info(f"[MorganAI] Adding internship opportunities context")
                        messages.append({
                            "role": "system",
                            "content": f"Current Internship Opportunities:\n{internship_context}"
                        })
                except Exception as int_err:
                    logger.warning(f"[MorganAI] Could not retrieve internship context: {int_err}")
                
                # Add current message
                messages.append({"role": "user", "content": message})
                logger.info(f"[MorganAI] Messages for OpenAI: {messages}")
                # Enforce JSON-only response if user explicitly requests it
                lower_msg = message.lower()
                if any(kw in lower_msg for kw in ["only json","json only","return json","structured json"]):
                    messages.insert(0, {
                        "role": "system",
                        "content": (
                            "The user requested strictly raw JSON only. Respond with a single valid JSON object or array. "
                            "Do NOT include markdown fences, backticks, commentary, natural language, or prefixes. "
                            "If you cannot produce JSON, return an empty JSON object {}."
                        )
                    })
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
                        timestamp=datetime.now(timezone.utc),
                        user_id=user_id
                    )
                    assistant_msg = ChatMessage(
                        role="assistant",
                        content=ai_response,
                        timestamp=datetime.now(timezone.utc),
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
                    "timestamp": self._now_iso(),
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
        """Get relevant context from knowledge base using RAG, with web search fallback"""
        try:
            # First, try to get context from knowledge base
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
                    
                    # Threshold 0.65 ensures only highly relevant KB results, triggering web search when needed
                    if score and score > 0.65:  
                        context_parts.append(f"[Source: {source}]\n{text}")
                        logger.info(f"[MorganAI RAG] Added result {i+1} to context (score {score} > 0.65)")
                    else:
                        logger.info(f"[MorganAI RAG] Skipped result {i+1} (score {score} <= 0.65)")
            
            # If we have good knowledge base results, use them
            if context_parts:
                final_context = "\n\n".join(context_parts)
                logger.info(f"[MorganAI RAG] Final context length: {len(final_context)} chars, {len(context_parts)} sources")

                # Force deep search augmentation for program/admission related queries
                forced_keywords = {"admission","admissions","requirement","requirements","program","curriculum","degree","catalog","master","ph.d","phd","graduate"}
                q_lower = query.lower()
                if any(k in q_lower for k in forced_keywords):
                    try:
                        logger.info(f"[MorganAI RAG] Forcing deep search augmentation due to keyword match in query: {query}")
                        web_results = await self.web_search_service.deep_search_morgan(query, max_results=3)
                        if web_results.get("success") and web_results.get("content"):
                            deep_context = f"[DEEP SEARCH AUGMENTATION]\n{web_results['content']}"
                            final_context = final_context + "\n\n" + deep_context
                            logger.info(f"[MorganAI RAG] Deep search augmentation appended (length now {len(final_context)} chars)")
                        else:
                            logger.info("[MorganAI RAG] Deep search augmentation returned no content")
                    except Exception as aug_err:
                        logger.warning(f"[MorganAI RAG] Deep search augmentation failed: {aug_err}")

                return final_context
            
            # If no good knowledge base results, fall back to DEEP WEB SEARCH
            logger.info(f"[MorganAI RAG] No sufficient knowledge base results, attempting DEEP web search from Morgan State official sources...")
            web_results = await self.web_search_service.deep_search_morgan(query, max_results=5)
            
            if web_results.get("success") and web_results.get("content"):
                # If structured program JSON exists in sources, build concise summary
                structured_summary = ""
                try:
                    sources = web_results.get("sources", [])
                    # structured data was embedded directly in content per result, but we can still scan content length
                    # For brevity, extract first program credit summary JSON blocks
                    if "Structured Programs JSON:" in web_results['content']:
                        # Extract up to first JSON block
                        import re as _re
                        match = _re.search(r"Structured Programs JSON:\n(\{.*?\})", web_results['content'], _re.DOTALL)
                        if match:
                            structured_summary = f"\n[STRUCTURED PROGRAM DATA]\n{match.group(1)}\n"
                except Exception as _struct_err:
                    logger.debug(f"[MorganAI RAG] Unable to extract structured summary: {_struct_err}")
                web_context = f"[DEEP SEARCH - Morgan State University Official Websites]\n{structured_summary}\n{web_results['content']}"
                
                logger.info(f"[MorganAI RAG] Deep web search successful!")
                logger.info(f"  - Total sources checked: {web_results.get('total_sources_checked', 0)}")
                logger.info(f"  - Relevant sources found: {web_results.get('relevant_sources_found', 0)}")
                logger.info(f"  - Content length: {len(web_results['content'])} chars")
                
                return web_context
            else:
                logger.warning(f"[MorganAI RAG] Deep web search also returned no results")
                return ""
                
        except Exception as e:
            logger.error(f"Error getting RAG context: {e}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Even if there's an error, try deep web search as last resort
            try:
                logger.info(f"[MorganAI RAG] Error in RAG, attempting DEEP web search as last resort...")
                web_results = await self.web_search_service.deep_search_morgan(query, max_results=3)
                if web_results.get("success") and web_results.get("content"):
                    return f"[Deep Search Results from Morgan State Official Websites]\n\n{web_results['content']}"
            except Exception as web_error:
                logger.error(f"[MorganAI RAG] Deep web search fallback also failed: {web_error}")
            
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
        voice: Optional[str] = None,
        speed: Optional[float] = None,
        response_format: Optional[str] = None
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
            # Detect basic audio format (MP3 vs WAV) by header bytes
            # MP3 often starts with 'ID3' or 0xFF 0xFB / 0xFF 0xF3 / 0xFF 0xF2 frames
            # WAV starts with 'RIFF'
            header = audio_data[:4]
            if header.startswith(b'RIFF'):
                suffix = ".wav"
            elif header.startswith(b'ID3') or (len(audio_data) > 2 and audio_data[0] == 0xFF):
                suffix = ".mp3"
            else:
                # Fallback to wav; OpenAI Whisper generally auto-detects
                suffix = ".wav"

            import tempfile
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
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
                "timestamp": self._now_iso()
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
    
    async def _get_degree_works_context(self, user_id: str) -> Optional[str]:
        """
        Retrieve Degree Works context for a user from database
        
        Args:
            user_id: User ID to get Degree Works data for
            
        Returns:
            Formatted context string or None if no data available
        """
        try:
            # Import database operations
            from app.core.database import get_db
            from app.core.db_operations import get_latest_degree_works
            from app.services.degree_works_parser import DegreeWorksParser
            
            # Get database session
            async for db in get_db():
                # Get latest Degree Works file from database
                degree_works_file = await get_latest_degree_works(db, user_id)

                parsed_data = None
                if degree_works_file and degree_works_file.parsed_data:
                    parsed_data = degree_works_file.parsed_data
                else:
                    # Fallback: attempt hydration from file storage if DB empty
                    logger.info(f"[MorganAI] No Degree Works DB record for user {user_id}. Attempting file storage hydration.")
                    try:
                        from app.core.file_storage import FileStorageService
                        from app.models.database import DegreeWorksFile
                        fs = FileStorageService()
                        files = fs.get_user_degree_works_files(user_id)
                        if files:
                            latest = files[0]
                            fallback_parsed = latest.get('parsed_data')
                            if fallback_parsed and fallback_parsed.get('success'):
                                # Persist to DB for future fast access
                                academic_summary = fallback_parsed.get('academic_summary', {})
                                student_info = fallback_parsed.get('student_info', {})
                                db_record = DegreeWorksFile(
                                    user_id=user_id,
                                    filename=latest.get('file_name') or 'degree_works.pdf',
                                    file_path=latest.get('file_path'),
                                    file_size=latest.get('file_size'),
                                    parsed_data=fallback_parsed,
                                    student_name=student_info.get('name'),
                                    student_id=student_info.get('student_id'),
                                    major=student_info.get('major'),
                                    classification=academic_summary.get('classification'),
                                    gpa=str(academic_summary.get('gpa', '')),
                                    credits_earned=int(academic_summary.get('completed_credits', 0)),
                                    credits_needed=int(academic_summary.get('total_credits_required', 120)),
                                    is_processed=True,
                                    processed_at=datetime.utcnow()
                                )
                                db.add(db_record)
                                await db.commit()
                                await db.refresh(db_record)
                                logger.info(f"[MorganAI] Hydrated Degree Works DB record for user {user_id} from file storage (id={db_record.id}).")
                                parsed_data = fallback_parsed
                            else:
                                logger.info(f"[MorganAI] File storage found but missing valid parsed_data for user {user_id}.")
                        else:
                            logger.info(f"[MorganAI] No Degree Works files in file storage for user {user_id}.")
                    except Exception as hydration_err:
                        logger.warning(f"[MorganAI] Hydration attempt failed for user {user_id}: {hydration_err}")

                if not parsed_data:
                    logger.info(f"[MorganAI] Degree Works context unavailable after hydration attempts for user {user_id}")
                    return None

                # Format the parsed data for chatbot context
                parser = DegreeWorksParser()
                context = parser.format_for_chatbot(parsed_data)

                logger.info(f"[MorganAI] Retrieved Degree Works context for user {user_id}: {len(context)} chars (source={'db' if degree_works_file else 'hydrated'})")
                return context
            
            return None
        except Exception as e:
            logger.warning(f"Error retrieving Degree Works context from database: {e}")
            import traceback
            logger.warning(traceback.format_exc())
            return None
            
    async def stream_chat_response(
        self,
        message: str,
        context: Optional[str] = None,
        history: Optional[List[Dict[str, Any]]] = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        """Stream chat response chunks using OpenAI streaming API.

        Yields text chunks suitable for SSE. On completion, persists messages
        via ThreadManager, mirroring non-stream flow.
        """
        try:
            # Build messages array with system prompt and optional context/history
            messages: List[Dict[str, str]] = [{"role": "system", "content": self.system_prompt}]

            if history:
                for msg in history:
                    role = msg.get("role") if isinstance(msg, dict) else getattr(msg, "role", None)
                    content = msg.get("content") if isinstance(msg, dict) else getattr(msg, "content", None)
                    if role and content:
                        messages.append({"role": role, "content": content})

            if context:
                messages.append({
                    "role": "system",
                    "content": f"Context from knowledge base and search:\n{context}"
                })

            messages.append({"role": "user", "content": message})

            # Call OpenAI with streaming enabled
            aggregated_text: List[str] = []
            stream = await self.client.chat.completions.create(
                model=self.chat_model,
                messages=messages,
                max_tokens=min(settings.OPENAI_MAX_TOKENS, 1500),
                temperature=settings.OPENAI_TEMPERATURE,
                stream=True
            )

            async for event in stream:
                try:
                    delta = event.choices[0].delta.content if event and event.choices and event.choices[0].delta else None
                    if delta:
                        aggregated_text.append(delta)
                        # Yield raw text chunk for SSE
                        yield json.dumps({"type": "chunk", "content": delta})
                except Exception:
                    # Best-effort: skip malformed event
                    continue

            full_text = "".join(aggregated_text)

            # Persist to thread if session_id is provided
            if session_id and full_text:
                try:
                    from app.models.chat import ChatMessage
                    # Add user message
                    user_msg = ChatMessage(
                        role="user",
                        content=message,
                        timestamp=datetime.now(timezone.utc),
                        user_id=user_id
                    )
                    # Add assistant message
                    assistant_msg = ChatMessage(
                        role="assistant",
                        content=full_text,
                        timestamp=datetime.now(timezone.utc),
                        user_id=user_id
                    )
                    await self.thread_manager.add_message(session_id, user_msg)
                    await self.thread_manager.add_message(session_id, assistant_msg)
                except Exception as persist_err:
                    logger.warning(f"[MorganAI] Stream persist error: {persist_err}")

            # Signal completion
            yield json.dumps({
                "type": "complete",
                "content": full_text,
                "model": self.chat_model,
                "timestamp": self._now_iso()
            })

        except Exception as e:
            logger.error(f"[MorganAI] Error in stream_chat_response: {e}")
            yield json.dumps({"type": "error", "error": str(e)})
    
    async def _get_internship_context(self) -> Optional[str]:
        """
        Retrieve latest internship opportunities for chatbot context
        
        Returns:
            Formatted context string with current internships or None if no data
        """
        try:
            # Import here to avoid circular dependency
            from app.services.internship_update_service import internship_update_service
            
            # Get latest internships
            internships = internship_update_service.internships_cache
            
            if not internships:
                return None
            
            # Format top 10 most recent internships for context
            top_internships = internships[:10]
            
            context_lines = ["=== CURRENT INTERNSHIP OPPORTUNITIES FOR MORGAN CS MAJORS ===\n"]
            
            for idx, internship in enumerate(top_internships, 1):
                context_lines.append(f"{idx}. {internship.get('title', 'Unknown Position')}")
                context_lines.append(f"   Company: {internship.get('company', 'Unknown')}")
                context_lines.append(f"   Location: {internship.get('location', 'Not specified')}")
                context_lines.append(f"   Type: {internship.get('type', 'Internship')}")
                
                if internship.get('salary'):
                    context_lines.append(f"   Salary: {internship.get('salary')}")
                
                if internship.get('deadline'):
                    context_lines.append(f"   Deadline: {internship.get('deadline')}")
                
                if internship.get('description'):
                    # Truncate description to 100 chars
                    desc = internship.get('description', '')[:100]
                    context_lines.append(f"   Description: {desc}...")
                
                context_lines.append("")  # Empty line between internships
            
            context_lines.append(f"\nTotal available internships: {len(internships)}")
            context_lines.append(f"Last updated: {internship_update_service.last_update.isoformat() if internship_update_service.last_update else 'Unknown'}")
            context_lines.append("\nNOTE: When answering questions about internships, use this current data.")
            
            return "\n".join(context_lines)
            
        except Exception as e:
            logger.warning(f"Error retrieving internship context: {e}")
            return None