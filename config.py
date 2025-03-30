from pathlib import Path

VECTOR_CACHE_DIR = Path("./vector_cache")
VECTOR_CACHE_DIR.mkdir(exist_ok=True)

CHROMA_SETTINGS = {
    "persist_directory": str(VECTOR_CACHE_DIR / "chroma_db"),
    "anonymized_telemetry": False
}

BATCH_SIZE = 3
TIMEOUT = 180.0
TOP_K = 3