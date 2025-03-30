import os
import re

from fastapi import APIRouter, HTTPException
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document

from models import QueryRequest, RAGResponse, DocumentResponse
from services.chroma_service import ChromaService
from services.ollama_service import OllamaService
from services.cache_service import CacheService
from utils.clean_wiki import process_documents
from utils.helpers import get_memory_usage, calculate_processing_time
from datetime import datetime
from langchain_community.embeddings import OllamaEmbeddings
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

chroma_service = ChromaService(
    embeddings=OllamaEmbeddings(
        model="nomic-embed-text",
        model_kwargs={"embedding_dimension": 768}
    )
)
ollama_service = OllamaService()
cache_service = CacheService()


@router.post("/rag", response_model=RAGResponse)
async def rag_endpoint(request: QueryRequest):
    docs = None
    start_time = datetime.now()
    initial_memory = get_memory_usage()
    cache_hit = False
    cache_key = None

    try:
        if request.url:
            source = request.url
            loader = WebBaseLoader(
                request.url,
                requests_kwargs={"headers": {"User-Agent": os.environ.get('USER_AGENT', 'MyRAGBot')}}
            )
            docs = loader.load()
            docs = await process_documents(docs)
            cache_key = cache_service.generate_cache_key(source)
        elif request.file_path and os.path.exists(request.file_path):
            source = request.file_path
            cache_key = cache_service.generate_cache_key(source)

        else:
            raise HTTPException(status_code=400, detail="Either URL or valid file_path required")

        if request.use_cache and cache_key:
            cached_data = await cache_service.load_vector_cache(cache_key)
            if cached_data:
                texts, metadatas = cached_data
                cache_hit = True
                docs = [Document(page_content=text, metadata=meta) for text, meta in zip(texts, metadatas)]

        vector_store = await chroma_service.create_vector_store(
            texts=[doc.page_content for doc in docs],
            metadatas=[doc.metadata for doc in docs]
        )

        if not cache_hit and cache_key:
            await cache_service.save_vector_cache(
                cache_key,
                [doc.page_content for doc in docs],
                [doc.metadata for doc in docs]
            )

        results = await vector_store.asimilarity_search_with_relevance_scores(
            request.query,
            k=request.top_k * 2
        )

        filtered_results = [r for r in results if r[1] > 0.7] or results[:request.top_k]

        context_chunks = []
        for doc, score in filtered_results[:request.top_k]:
            sentences = re.split(r'(?<=[.!?])\s+', doc.page_content)
            context_chunks.extend(sentences[:5])

        context = "\n".join([f"- {chunk}" for chunk in context_chunks])

        # Генерация ответа
        prompt = f"""Ты - ассистент с доступом к базе знаний. Ответь на вопрос, используя ТОЛЬКО предоставленный контекст.
Если информации нет в контексте, скажи "Не могу найти ответ в предоставленных источниках".

Контекст:
{context}

Вопрос: {request.query}

Сформулируй точный, развернутый ответ, цитируя конкретные факты из контекста. Ответ:"""

        answer = await ollama_service.generate_response(prompt)

        return RAGResponse(
            query=request.query,
            answer=answer,
            sources=[DocumentResponse(
                content=doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content,
                metadata=doc.metadata,
                score=score
            ) for doc, score in filtered_results],
            processing_time_ms=calculate_processing_time(start_time),
            memory_usage_mb=round(get_memory_usage() - initial_memory, 2),
            cache_hit=cache_hit,
            cache_key=cache_key
        )

    except Exception as e:
        logger.error(f"Error in RAG endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))