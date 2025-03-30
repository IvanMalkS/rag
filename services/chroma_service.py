import hashlib
import logging
from typing import Dict, List

from langchain_community.embeddings import OllamaEmbeddings
import chromadb
from langchain_community.vectorstores import Chroma
from config import CHROMA_SETTINGS, VECTOR_CACHE_DIR

logger = logging.getLogger(__name__)


class ChromaService:
    def __init__(self, embeddings: OllamaEmbeddings):
        db_path = str(VECTOR_CACHE_DIR / "chroma_db")

        self.embeddings = embeddings
        self.client = chromadb.PersistentClient(
            path=db_path,
            settings=chromadb.Settings(**CHROMA_SETTINGS)
        )

        # Verify embedding dimension
        test_embedding = self.embeddings.embed_query("test")
        self.embedding_dimension = len(test_embedding)

    async def create_vector_store(self, texts: List[str], metadatas: List[Dict]) -> Chroma:
        try:
            collection = self.client.get_or_create_collection(
                name="documents",
                metadata={
                    "hnsw:space": "cosine",
                    "dimension": self.embedding_dimension
                }
            )


            ids = [str(hashlib.md5((text + str(meta)).encode()).hexdigest())
                   for text, meta in zip(texts, metadatas)]

            return await Chroma.afrom_texts(
                texts=texts,
                embedding=self.embeddings,
                metadatas=metadatas,
                ids=ids,
                client=self.client,
                collection_name="documents"
            )
        except Exception as e:
            logger.error(f"Vector store creation failed: {str(e)}")
            raise