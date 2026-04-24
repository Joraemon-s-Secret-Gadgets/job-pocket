"""
평가 모듈에서 사용하는 경로, 모델 설정 및 기술 스택 사전을 관리하는 설정 파일입니다.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[4]
EVAL_DIR = Path(__file__).resolve().parents[1]

# 평가에 사용되는 파일 및 딕셔너리 경로 정의
RESOURCE_DIR = EVAL_DIR / "resources"
TECH_DICT_PATH = RESOURCE_DIR / "tech_keyword_dict.json"
BM25_INDEX_PATH = BASE_DIR / "backend" / "utils" / "bm25_index.pkl"

FAISS_INDEX_PATH = BASE_DIR / "backend" / "utils" / "faiss_index_high"
TEST_DATA_DIR = EVAL_DIR / "datasets"
TEST_DATA_PATH = TEST_DATA_DIR / "retrieval_test_dataset.json"
SAMPLE_DATA_PATH = TEST_DATA_DIR / "evaluation_df_sample.json"
RESULT_DIR = EVAL_DIR / "results"

# vector store retriever 설정
TOP_K = 3

# 기술 스택 단어사전에서 최소 포함되어야 하는 단어 수
MIN_TECH_COUNT = 5

# 임베딩 모델 설정
MODEL_NAME = "Qwen/Qwen3-Embedding-0.6B"
DEVICE = "cpu"  # or "cuda"

# 기술스택 동의어/ 한-영 매핑 사전
TECH_SYM_DICT = {
    "frontend engineer": {
        "database": "db",
        "테스트": "testing",
        "해커톤": "hackathon",
        "모바일": "mobile",
        "인턴": "intern",
    },
    "backend engineer": {
        "해커톤": "hackathon",
        "데이터베이스": "db",
        "클라우드": "cloud",
        "쿼리": "query",
        "서버": "server",
        "프레임": "framework",
        "메시징": "messaging",
        "컨테이너": "container",
    },
    "ai engineer": {
        "해커톤": "hackathon",
        "머신": "ml",
        "텍스트": "text",
        "챗봇": "chatbot",
        "벡터": "vector",
        "튜닝": "tuning",
        "데이터베이스": "db",
        "클라우드": "cloud",
        "모델": "model",
    },
}
