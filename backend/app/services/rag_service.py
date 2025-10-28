from typing import List, Dict, Any
import structlog
import openai
from qdrant_client.http import models

from app.core.config import settings
from app.core.qdrant import get_qdrant
from app.schemas.chat import RAGContext

logger = structlog.get_logger()

class RAGService:
    def __init__(self, db, redis):
        self.db = db
        self.redis = redis
        self.qdrant = get_qdrant()

    async def retrieve_context(self, query: str, language: str = "en") -> RAGContext:
        """Retrieve relevant context using hybrid search"""
        try:
            # Generate embedding for query
            embedding = await self._generate_embedding(query)
            
            # Semantic search in Qdrant
            semantic_results = self._semantic_search(embedding, language)
            
            # Lexical search in PostgreSQL (if available)
            lexical_results = await self._lexical_search(query, language)
            
            # Combine and rank results
            combined_results = self._combine_results(semantic_results, lexical_results)
            
            # Build context text
            context_text = self._build_context_text(combined_results)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence(combined_results)
            
            return RAGContext(
                query=query,
                retrieved_docs=combined_results,
                context_text=context_text,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            logger.error("RAG retrieval failed", error=str(e), query=query)
            return RAGContext(
                query=query,
                retrieved_docs=[],
                context_text="",
                confidence_score=0.0
            )

    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI API"""
        try:
            if not settings.openai_api_key:
                # Fallback to simple text processing
                return self._simple_embedding(text)
            
            client = openai.OpenAI(api_key=settings.openai_api_key)
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
            
        except Exception as e:
            logger.error("Embedding generation failed", error=str(e))
            return self._simple_embedding(text)

    def _simple_embedding(self, text: str) -> List[float]:
        """Simple fallback embedding (not recommended for production)"""
        # This is a placeholder - in production, use a proper embedding model
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        return [float(b) / 255.0 for b in hash_bytes[:16]] + [0.0] * 368  # Pad to 384 dimensions

    def _semantic_search(self, embedding: List[float], language: str) -> List[Dict[str, Any]]:
        """Perform semantic search in Qdrant"""
        try:
            search_result = self.qdrant.search(
                collection_name=settings.qdrant_collection,
                query_vector=embedding,
                limit=settings.max_retrieved_docs,
                query_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="language",
                            match=models.MatchValue(value=language)
                        ),
                        models.FieldCondition(
                            key="status",
                            match=models.MatchValue(value="active")
                        )
                    ]
                )
            )
            
            results = []
            for hit in search_result:
                results.append({
                    "id": hit.payload.get("id"),
                    "content": hit.payload.get("canonical_answer", ""),
                    "category": hit.payload.get("category", ""),
                    "score": hit.score,
                    "follow_up_suggestions": hit.payload.get("follow_up_suggestions", "")
                })
            
            return results
            
        except Exception as e:
            logger.error("Semantic search failed", error=str(e))
            return []

    async def _lexical_search(self, query: str, language: str) -> List[Dict[str, Any]]:
        """Perform lexical search in PostgreSQL"""
        try:
            if not self.db:
                return []
            
            from sqlalchemy import text
            
            # Simple keyword search
            search_query = text("""
                SELECT id, canonical_answer, category, follow_up_suggestions
                FROM kb_entries 
                WHERE language = :language 
                AND status = 'active'
                AND (
                    canonical_answer ILIKE :query
                    OR category ILIKE :query
                )
                ORDER BY 
                    CASE 
                        WHEN canonical_answer ILIKE :exact_query THEN 1
                        WHEN canonical_answer ILIKE :partial_query THEN 2
                        ELSE 3
                    END
                LIMIT :limit
            """)
            
            result = await self.db.execute(search_query, {
                "language": language,
                "query": f"%{query}%",
                "exact_query": f"%{query}%",
                "partial_query": f"%{query}%",
                "limit": settings.max_retrieved_docs
            })
            
            results = []
            for row in result:
                results.append({
                    "id": row.id,
                    "content": row.canonical_answer,
                    "category": row.category,
                    "score": 0.8,  # Fixed score for lexical results
                    "follow_up_suggestions": row.follow_up_suggestions or ""
                })
            
            return results
            
        except Exception as e:
            logger.error("Lexical search failed", error=str(e))
            return []

    def _combine_results(self, semantic_results: List[Dict], lexical_results: List[Dict]) -> List[Dict]:
        """Combine and deduplicate search results"""
        # Create a map to avoid duplicates
        results_map = {}
        
        # Add semantic results (higher weight)
        for result in semantic_results:
            doc_id = result["id"]
            if doc_id not in results_map or result["score"] > results_map[doc_id]["score"]:
                results_map[doc_id] = result
        
        # Add lexical results
        for result in lexical_results:
            doc_id = result["id"]
            if doc_id not in results_map:
                results_map[doc_id] = result
        
        # Sort by score and return top results
        combined = list(results_map.values())
        combined.sort(key=lambda x: x["score"], reverse=True)
        
        return combined[:settings.max_retrieved_docs]

    def _build_context_text(self, results: List[Dict]) -> str:
        """Build context text from retrieved documents"""
        if not results:
            return ""
        
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"Context {i} ({result['category']}): {result['content']}")
        
        return "\n\n".join(context_parts)

    def _calculate_confidence(self, results: List[Dict]) -> float:
        """Calculate confidence score based on retrieved results"""
        if not results:
            return 0.0
        
        # Average score of top results
        scores = [result["score"] for result in results]
        avg_score = sum(scores) / len(scores)
        
        # Apply threshold
        if avg_score < settings.similarity_threshold:
            return avg_score * 0.5  # Reduce confidence for low scores
        
        return min(avg_score, 1.0)
