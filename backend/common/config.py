import os

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

MYSQL_RDB_USER = os.getenv('MYSQL_RDB_USER')

MYSQL_VECTOR_USER = os.getenv('MYSQL_VECTOR_USER')

OPENAI_API_CONFIG = {
    "model": "gpt-4o-mini",
    "temperature": 0.55,
}

GROQ_API_CONFIG = {
    "model": "openai/gpt-oss-120b",
    "temperature": 0.65,
    "top_p": 1,
    "stop": None,
}

EMBEDDING_CONFIG = {
    "model_name": "Qwen/Qwen3-Embedding-0.6B",
    "model_kwargs": {"device": "cpu"},
    "encode_kwargs": {"normalize_embeddings": True},
}

RETRIEVER_CONFIG = {
    'top_k': 3,
    'index_folder': str(BASE_DIR / "data")
}