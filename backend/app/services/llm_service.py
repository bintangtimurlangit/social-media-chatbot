from typing import List, Dict, Any
import openai
import structlog

from app.core.config import settings
from app.schemas.chat import ChatMessage, RAGContext

logger = structlog.get_logger()

class LLMService:
    def __init__(self):
        self.client = None
        if settings.openai_api_key:
            self.client = openai.OpenAI(api_key=settings.openai_api_key)

    async def generate_response(
        self, 
        user_message: str, 
        conversation_context: List[ChatMessage],
        rag_context: RAGContext,
        language: str = "en"
    ) -> str:
        """Generate response using LLM"""
        try:
            # Build system prompt
            system_prompt = self._build_system_prompt(language)
            
            # Build conversation messages
            messages = self._build_messages(
                system_prompt, 
                conversation_context, 
                user_message, 
                rag_context
            )
            
            # Generate response
            if self.client:
                response = await self._generate_with_openai(messages)
            else:
                response = await self._generate_fallback(user_message, rag_context)
            
            return response
            
        except Exception as e:
            logger.error("LLM generation failed", error=str(e))
            return self._generate_error_response(language)

    def _build_system_prompt(self, language: str) -> str:
        """Build system prompt based on language and context"""
        base_prompt = """You are a helpful customer service assistant for a social media business. 
        You should be friendly, professional, and helpful. Always answer based on the provided context.
        If you don't know something, politely say so and offer to help in other ways.
        Keep responses concise but informative."""
        
        if language == "id":
            return """Anda adalah asisten layanan pelanggan yang membantu untuk bisnis media sosial.
            Anda harus ramah, profesional, dan membantu. Selalu jawab berdasarkan konteks yang diberikan.
            Jika Anda tidak tahu sesuatu, katakan dengan sopan dan tawarkan bantuan lainnya.
            Buat respons yang ringkas tetapi informatif."""
        
        return base_prompt

    def _build_messages(
        self, 
        system_prompt: str, 
        conversation_context: List[ChatMessage],
        user_message: str,
        rag_context: RAGContext
    ) -> List[Dict[str, str]]:
        """Build messages for LLM API"""
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add context if available
        if rag_context.context_text:
            context_message = f"Relevant information:\n{rag_context.context_text}\n\nUser question: {user_message}"
        else:
            context_message = user_message
        
        # Add conversation history
        for msg in conversation_context[-5:]:  # Last 5 messages
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": context_message
        })
        
        return messages

    async def _generate_with_openai(self, messages: List[Dict[str, str]]) -> str:
        """Generate response using OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error("OpenAI API call failed", error=str(e))
            raise

    async def _generate_fallback(self, user_message: str, rag_context: RAGContext) -> str:
        """Fallback response generation when LLM is not available"""
        if rag_context.retrieved_docs:
            # Use the best matching document
            best_doc = rag_context.retrieved_docs[0]
            return f"Based on our knowledge base: {best_doc['content']}"
        else:
            return "I'm sorry, I don't have enough information to answer your question. Please contact our support team for assistance."

    def _generate_error_response(self, language: str) -> str:
        """Generate error response when LLM fails"""
        if language == "id":
            return "Maaf, terjadi kesalahan dalam memproses permintaan Anda. Silakan coba lagi nanti atau hubungi tim support kami."
        else:
            return "Sorry, there was an error processing your request. Please try again later or contact our support team."
