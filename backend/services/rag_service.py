"""
Serwis RAG (Retrieval-Augmented Generation) z pgvector
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import structlog
from datetime import datetime
import openai

from database.connection import get_database_session, get_raw_connection
from services.object_storage import ScalewayObjectStorage
from utils.config import get_settings

logger = structlog.get_logger(__name__)

class RAGService:
    """Serwis do Retrieval-Augmented Generation z pgvector"""
    
    def __init__(self):
        self.settings = get_settings()
        self.openai_client = openai.AsyncOpenAI(api_key=self.settings.OPENAI_API_KEY)
        self.object_storage = ScalewayObjectStorage()
        self.embedding_model = "text-embedding-ada-002"
        self.chunk_size = 1000
        self.chunk_overlap = 200
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generowanie embedingu dla tekstu przez OpenAI
        
        Args:
            text: Tekst do embedowania
            
        Returns:
            Lista floatów reprezentująca embedding
        """
        try:
            logger.info("Generowanie embedingu", text_length=len(text))
            
            response = await self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            
            embedding = response.data[0].embedding
            
            logger.info("Embedding wygenerowany pomyślnie", 
                       dimension=len(embedding),
                       model=self.embedding_model)
            
            return embedding
            
        except Exception as e:
            logger.error("Błąd generowania embedingu", error=str(e))
            raise
    
    def chunk_text(self, text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """
        Podział tekstu na chunki z overlappingiem
        
        Args:
            text: Tekst do podziału
            chunk_size: Rozmiar chunka (słowa)
            overlap: Nakładanie się chunków (słowa)
            
        Returns:
            Lista chunków tekstowych
        """
        chunk_size = chunk_size or self.chunk_size
        overlap = overlap or self.chunk_overlap
        
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            if chunk_text.strip():
                chunks.append(chunk_text.strip())
            
            # Sprawdź czy to ostatni chunk
            if i + chunk_size >= len(words):
                break
        
        logger.info("Tekst podzielony na chunki",
                   total_words=len(words),
                   chunk_count=len(chunks),
                   chunk_size=chunk_size,
                   overlap=overlap)
        
        return chunks
    
    async def add_document(
        self, 
        title: str, 
        content: str, 
        source_type: str = 'manual',
        source_reference: str = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Dodanie dokumentu do bazy wiedzy z automatycznym embeddingiem
        
        Args:
            title: Tytuł dokumentu
            content: Zawartość dokumentu
            source_type: Typ źródła ('manual', 'upload', 'url', 'api')
            source_reference: Referencja do źródła
            metadata: Dodatkowe metadane
            
        Returns:
            Dict z informacjami o dodanym dokumencie
        """
        try:
            async with get_database_session() as session:
                # 1. Dodaj dokument do tabeli documents
                insert_doc_query = """
                    INSERT INTO documents (title, content, source_type, source_reference, metadata)
                    VALUES ($1, $2, $3, $4, $5)
                    RETURNING id
                """
                
                conn = await get_raw_connection()
                
                document_id = await conn.fetchval(
                    insert_doc_query,
                    title,
                    content,
                    source_type,
                    source_reference,
                    metadata or {}
                )
                
                # 2. Podziel tekst na chunki
                chunks = self.chunk_text(content)
                
                # 3. Generuj embeddingi dla każdego chunka
                embeddings_data = []
                
                for i, chunk in enumerate(chunks):
                    try:
                        embedding = await self.generate_embedding(chunk)
                        embeddings_data.append((document_id, i, chunk, embedding))
                        
                        # Pauza między requestami żeby nie przekroczyć rate limitu
                        if i > 0 and i % 5 == 0:
                            await asyncio.sleep(1)
                            
                    except Exception as e:
                        logger.warning("Błąd generowania embedingu dla chunka",
                                     chunk_index=i,
                                     error=str(e))
                        continue
                
                # 4. Zapisz embeddingi do bazy
                if embeddings_data:
                    # Sprawdź czy pgvector jest dostępny
                    try:
                        insert_embedding_query = """
                            INSERT INTO document_embeddings (document_id, chunk_index, chunk_text, embedding, model_name)
                            VALUES ($1, $2, $3, $4, $5)
                        """
                        
                        for doc_id, chunk_idx, chunk_text, embedding in embeddings_data:
                            await conn.execute(
                                insert_embedding_query,
                                doc_id,
                                chunk_idx,
                                chunk_text,
                                embedding,  # pgvector automatycznie konwertuje listę
                                self.embedding_model
                            )
                            
                    except Exception as e:
                        # Fallback do tabeli bez pgvector
                        logger.warning("pgvector niedostępny, używam fallback tabeli", error=str(e))
                        
                        insert_fallback_query = """
                            INSERT INTO document_embeddings_fallback (document_id, chunk_index, chunk_text, embedding_json, model_name)
                            VALUES ($1, $2, $3, $4, $5)
                        """
                        
                        for doc_id, chunk_idx, chunk_text, embedding in embeddings_data:
                            await conn.execute(
                                insert_fallback_query,
                                doc_id,
                                chunk_idx,
                                chunk_text,
                                str(embedding),  # JSON jako string
                                self.embedding_model
                            )
                
                await conn.close()
                
                # 5. Opcjonalnie uploaduj do Object Storage
                if self.settings.ENVIRONMENT == 'production':
                    try:
                        storage_result = await self.object_storage.upload_document_for_rag(
                            document_content=content,
                            document_title=title,
                            source_reference=source_reference
                        )
                        logger.info("Dokument zapisany w Object Storage", 
                                   document_id=document_id,
                                   storage_success=storage_result['success'])
                    except Exception as e:
                        logger.warning("Błąd zapisu do Object Storage", error=str(e))
                
                logger.info("Dokument dodany do bazy wiedzy",
                           document_id=document_id,
                           title=title,
                           chunks_count=len(chunks),
                           embeddings_count=len(embeddings_data))
                
                return {
                    'success': True,
                    'document_id': document_id,
                    'title': title,
                    'chunks_processed': len(embeddings_data),
                    'total_chunks': len(chunks),
                    'embedding_model': self.embedding_model
                }
                
        except Exception as e:
            logger.error("Błąd dodawania dokumentu", error=str(e))
            return {
                'success': False,
                'error': str(e),
                'title': title
            }
    
    async def search_similar_documents(
        self, 
        query: str, 
        limit: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Wyszukiwanie podobnych dokumentów przez similarity search
        
        Args:
            query: Query do wyszukiwania
            limit: Maksymalna liczba wyników
            similarity_threshold: Próg podobieństwa (0-1)
            
        Returns:
            Lista podobnych chunków z metadanymi
        """
        try:
            # 1. Generuj embedding dla query
            query_embedding = await self.generate_embedding(query)
            
            # 2. Wyszukaj podobne dokumenty
            conn = await get_raw_connection()
            
            try:
                # Próbuj z pgvector
                search_query = """
                    SELECT 
                        de.chunk_text,
                        de.chunk_index,
                        d.id as document_id,
                        d.title,
                        d.source_type,
                        d.source_reference,
                        d.metadata,
                        (de.embedding <-> $1::vector) as distance,
                        1 - (de.embedding <-> $1::vector) as similarity
                    FROM document_embeddings de
                    JOIN documents d ON de.document_id = d.id
                    WHERE d.is_active = true
                    AND (de.embedding <-> $1::vector) < $2
                    ORDER BY de.embedding <-> $1::vector
                    LIMIT $3
                """
                
                results = await conn.fetch(
                    search_query,
                    query_embedding,
                    1 - similarity_threshold,  # Konwersja similarity na distance
                    limit
                )
                
            except Exception as e:
                # Fallback bez pgvector - mniej efektywny
                logger.warning("pgvector niedostępny, używam fallback wyszukiwania", error=str(e))
                
                fallback_query = """
                    SELECT 
                        def.chunk_text,
                        def.chunk_index,
                        d.id as document_id,
                        d.title,
                        d.source_type,
                        d.source_reference,
                        d.metadata,
                        def.embedding_json
                    FROM document_embeddings_fallback def
                    JOIN documents d ON def.document_id = d.id
                    WHERE d.is_active = true
                    ORDER BY def.id
                """
                
                all_results = await conn.fetch(fallback_query)
                
                # Oblicz similarity manualnie
                results = []
                for row in all_results:
                    try:
                        doc_embedding = eval(row['embedding_json'])  # Unsafe ale to fallback
                        similarity = self._cosine_similarity(query_embedding, doc_embedding)
                        
                        if similarity >= similarity_threshold:
                            result = dict(row)
                            result['similarity'] = similarity
                            result['distance'] = 1 - similarity
                            results.append(result)
                            
                    except Exception:
                        continue
                
                # Sortuj i ogranicz
                results = sorted(results, key=lambda x: x['similarity'], reverse=True)[:limit]
            
            await conn.close()
            
            # 3. Formatuj wyniki
            formatted_results = []
            for row in results:
                formatted_results.append({
                    'chunk_text': row['chunk_text'],
                    'chunk_index': row['chunk_index'],
                    'document_id': row['document_id'],
                    'document_title': row['title'],
                    'source_type': row['source_type'],
                    'source_reference': row['source_reference'],
                    'similarity': float(row['similarity']),
                    'metadata': row.get('metadata', {})
                })
            
            logger.info("Wyszukiwanie dokumentów zakończone",
                       query_length=len(query),
                       results_count=len(formatted_results),
                       similarity_threshold=similarity_threshold)
            
            return formatted_results
            
        except Exception as e:
            logger.error("Błąd wyszukiwania dokumentów", error=str(e))
            return []
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Obliczenie cosine similarity między dwoma wektorami"""
        try:
            a = np.array(vec1)
            b = np.array(vec2)
            
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            similarity = dot_product / (norm_a * norm_b)
            return float(similarity)
            
        except Exception:
            return 0.0
    
    async def get_context_for_query(
        self, 
        query: str, 
        max_chunks: int = 3,
        similarity_threshold: float = 0.7
    ) -> str:
        """
        Pobieranie kontekstu dla zapytania - główna funkcja RAG
        
        Args:
            query: Zapytanie użytkownika
            max_chunks: Maksymalna liczba chunków do zwrócenia
            similarity_threshold: Próg podobieństwa
            
        Returns:
            Skonkatenowany kontekst z dokumentów
        """
        try:
            similar_docs = await self.search_similar_documents(
                query=query,
                limit=max_chunks,
                similarity_threshold=similarity_threshold
            )
            
            if not similar_docs:
                return "Brak relevantnych dokumentów w bazie wiedzy."
            
            context_parts = []
            for i, doc in enumerate(similar_docs, 1):
                context_parts.append(f"""
Dokument {i}: {doc['document_title']}
Źródło: {doc['source_type']}
Podobieństwo: {doc['similarity']:.2f}

{doc['chunk_text']}
---
""")
            
            context = "\n".join(context_parts)
            
            logger.info("Kontekst RAG przygotowany",
                       query_length=len(query),
                       documents_used=len(similar_docs),
                       context_length=len(context))
            
            return context
            
        except Exception as e:
            logger.error("Błąd przygotowania kontekstu RAG", error=str(e))
            return "Błąd podczas pobierania kontekstu z bazy wiedzy."