import openai
from typing import List, Dict, Any, Optional
import logging
from ..core.config import settings
from ..core.exceptions import OpenAIServiceException

logger = logging.getLogger(__name__)

class OpenAIService:
    """Service for handling OpenAI API interactions"""
    
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.embedding_model = settings.OPENAI_EMBEDDING_MODEL
        self.temperature = settings.CHAT_TEMPERATURE
        self.max_tokens = settings.MAX_RESPONSE_TOKENS
    
    async def test_connection(self) -> bool:
        """Test OpenAI API connection"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            logger.info("OpenAI API connection successful")
            return True
        except Exception as e:
            logger.error(f"OpenAI API connection failed: {str(e)}")
            raise OpenAIServiceException(f"Failed to connect to OpenAI API: {str(e)}")
    
    async def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = None,
        context: str = None
    ) -> str:
        """Generate AI response for chat conversation"""
        try:
            # Build conversation messages
            conversation_messages = []
            
            # Add system prompt
            if system_prompt:
                conversation_messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            else:
                # Default Morgan AI system prompt
                default_prompt = self._get_default_system_prompt()
                conversation_messages.append({
                    "role": "system", 
                    "content": default_prompt
                })
            
            # Add context if provided
            if context:
                conversation_messages.append({
                    "role": "system",
                    "content": f"Relevant information from Morgan State CS Department knowledge base:\n{context}"
                })
            
            # Add conversation history
            conversation_messages.extend(messages)
            
            # Generate response
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=conversation_messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Failed to generate chat response: {str(e)}")
            raise OpenAIServiceException(f"Failed to generate response: {str(e)}")
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for text chunks"""
        try:
            response = await self.client.embeddings.create(
                model=self.embedding_model,
                input=texts
            )
            
            embeddings = [embedding.embedding for embedding in response.data]
            logger.info(f"Generated embeddings for {len(texts)} texts")
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {str(e)}")
            raise OpenAIServiceException(f"Failed to generate embeddings: {str(e)}")
    
    async def generate_single_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        embeddings = await self.generate_embeddings([text])
        return embeddings[0]
    
    async def text_to_speech(self, text: str, voice: str = None) -> bytes:
        """Convert text to speech using OpenAI TTS"""
        try:
            voice = voice or settings.TTS_VOICE
            
            response = await self.client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text[:4000]  # Limit text length for TTS
            )
            
            audio_content = b""
            async for chunk in response.iter_bytes():
                audio_content += chunk
                
            logger.info(f"Generated TTS audio for text length: {len(text)}")
            return audio_content
            
        except Exception as e:
            logger.error(f"Failed to generate TTS: {str(e)}")
            raise OpenAIServiceException(f"Failed to generate speech: {str(e)}")
    
    async def speech_to_text(self, audio_data: bytes, format: str = "mp3") -> str:
        """Convert speech to text using OpenAI Whisper"""
        try:
            # Create a temporary file-like object
            from io import BytesIO
            audio_file = BytesIO(audio_data)
            audio_file.name = f"audio.{format}"
            
            response = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            
            logger.info(f"Transcribed audio to text: {len(response.text)} characters")
            return response.text
            
        except Exception as e:
            logger.error(f"Failed to transcribe audio: {str(e)}")
            raise OpenAIServiceException(f"Failed to transcribe audio: {str(e)}")
    
    def _get_default_system_prompt(self) -> str:
        """Get the default system prompt for Morgan AI"""
        return """You are Morgan AI, a helpful and knowledgeable assistant specifically designed to support Computer Science students at Morgan State University. Your primary role is to provide accurate, helpful information about the Computer Science department.

Key responsibilities:
1. Department Information: Provide details about faculty, staff, office locations, contact information, and office hours.

2. Academic Support: Guide students to tutoring services, programming help, course recommendations, prerequisites, and degree requirements.

3. Atudent Organizations: Share information about WiCS (Women in Computer Science), GDSC (Google Developer Student Clubs), SACS (Student Association for Computing Systems), and how to join them.

4. Career Resources: Recommend internship programs (Google STEP, Microsoft Explore), interview preparation resources (NeetCode, LeetCode, ColorStack, CodePath), and career development opportunities.

5. Advising & Registration: Help with enrollment processes, PIN requests, course planning, override requests, academic forms, and important deadlines.

Communication Style:
- Be friendly, professional, and encouraging
- Use clear, concise language appropriate for college students
- Provide specific, actionable information when possible
- If you don't have specific information, guide students to appropriate resources or contacts
- Use Morgan State University branding colors (orange #FF9100 and navy blue #001b3a) in your tone - be warm and trustworthy

Always prioritize student success and well-being in your responses."""

    def _truncate_context(self, context: str, max_length: int = 2000) -> str:
        """Truncate context to fit within token limits"""
        if len(context) <= max_length:
            return context
        
        # Try to truncate at sentence boundaries
        sentences = context.split('.')
        truncated = ""
        
        for sentence in sentences:
            if len(truncated + sentence + ".") <= max_length:
                truncated += sentence + "."
            else:
                break
        
        return truncated if truncated else context[:max_length] + "..."