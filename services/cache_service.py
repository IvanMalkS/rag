import json
import hashlib
import logging
from typing import List, Dict, Optional, Tuple

from langchain_community.vectorstores import Chroma

from config import VECTOR_CACHE_DIR

logger = logging.getLogger(__name__)


class CacheService:
    def __init__(self):
        self.document_cache: Dict[str, List[Dict]] = {}

    def generate_cache_key(self, source: str) -> str:
        return hashlib.md5(source.encode()).hexdigest()

    async def save_vector_cache(self, cache_key: str, texts: List[str], metadatas: List[dict]):
        try:
            cache_file = VECTOR_CACHE_DIR / f"{cache_key}.json"
            with open(cache_file, "w") as f:
                json.dump({"texts": texts, "metadatas": metadatas}, f)
            logger.info(f"Vector cache saved for key: {cache_key}")
        except Exception as e:
            logger.error(f"Error saving vector cache: {str(e)}")
            raise

    async def load_vector_cache(self, cache_key: str) -> Optional[Tuple[List[str], List[dict]]]:
        try:
            cache_file = VECTOR_CACHE_DIR / f"{cache_key}.json"
            if cache_file.exists():
                with open(cache_file, "r") as f:
                    data = json.load(f)
                return data["texts"], data["metadatas"]
            return None
        except Exception as e:
            logger.error(f"Error loading vector cache: {str(e)}")
            return None
