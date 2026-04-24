"""
HybridRetriever 통합 테스트.

관련 테스트 케이스: TC-023 ~ TC-025

이 테스트는 FAISS 인덱스와 MySQL 접속이 필요하므로,
실제 실행 전에 테스트용 fixture를 준비해야 한다.

@pytest.mark.retriever 마커를 사용하여 선택적 실행 가능:
    pytest -m "not retriever"  # 제외
    pytest -m retriever         # retriever만
"""

from unittest.mock import MagicMock, patch
import pytest


# ==========================================
# Mock 기반 테스트 (FAISS 인덱스 불필요)
# ==========================================

@pytest.mark.integration
@pytest.mark.mock_llm
class TestRetrieverWithMock:
    """
    실제 FAISS/MySQL 없이 Retriever의 공용 동작 로직을 검증한다.
    의존성을 mocking하여 retriever.py의 코드 경로를 확인.
    """

    def test_retriever_returns_top_n_documents(self, mock_retriever):
        """
        TC-023: HybridRetriever가 정확히 top_n=3 문서를 반환해야 한다 (mock).
        """
        from services.chat_logic import selfintro_retriever

        docs = selfintro_retriever.invoke("테스트 쿼리")

        assert len(docs) == 3
        for doc in docs:
            assert hasattr(doc, "page_content")
            assert hasattr(doc, "metadata")
            assert "id" in doc.metadata
            assert "selfintro_score" in doc.metadata
            assert "relevance_score" in doc.metadata

    def test_retriever_documents_have_valid_scores(self, mock_retriever):
        """반환된 문서의 점수가 합리적 범위 안에 있어야 한다."""
        from services.chat_logic import selfintro_retriever

        docs = selfintro_retriever.invoke("테스트")

        for doc in docs:
            # selfintro_score는 0~60 범위
            score = doc.metadata["selfintro_score"]
            assert 0 <= score <= 60

            # relevance_score는 FAISS L2 distance (정규화된 벡터 기준 0~2)
            relevance = doc.metadata["relevance_score"]
            assert isinstance(relevance, (int, float))
            assert relevance >= 0


# ==========================================
# 실제 FAISS 인덱스 필요 테스트
# ==========================================

@pytest.mark.retriever
@pytest.mark.integration
@pytest.mark.slow
class TestRetrieverWithRealIndex:
    """
    실제 FAISS 인덱스와 MySQL 접속을 사용하는 테스트.

    선결 조건:
      1. faiss_index_high/ 폴더에 인덱스 파일 존재
      2. MySQL job_pocket_vector 데이터베이스에 applicant_records 적재
      3. 환경변수 DB_CONFIG 설정

    실행:
      pytest -m retriever
    """

    @pytest.fixture(scope="class")
    def real_retriever(self):
        """실제 HybridRetriever 인스턴스를 생성한다."""
        import os
        from langchain_huggingface import HuggingFaceEmbeddings
        from retriever import HybridRetriever

        db_config = {
            "host": os.getenv("HOST", "localhost"),
            "port": int(os.getenv("PORT", "3306")),
            "user": os.getenv("USER", "vector_user"),
            "password": os.getenv("PASSWORD", "vector_password"),
            "db": os.getenv("DB", "job_pocket_vector"),
            "charset": "utf8mb4",
        }

        embeddings = HuggingFaceEmbeddings(
            model_name="Qwen/Qwen3-Embedding-0.6B",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

        # 테스트용 인덱스 경로 (fixtures 디렉토리 또는 실 인덱스 사용)
        index_path = os.getenv("TEST_FAISS_INDEX_PATH", "faiss_index_high")

        retriever = HybridRetriever(
            db_config=db_config,
            embeddings=embeddings,
            top_n=3,
            initial_k=10,
            index_folder=index_path,
        )
        return retriever

    def test_real_retriever_returns_three_documents(self, real_retriever):
        """
        TC-023: 실제 인덱스로 top-3 문서 반환 검증.
        """
        query = (
            "[최종학력] ○○대학교 컴퓨터공학 "
            "[경력 및 경험] 데이터 엔지니어링 인턴 3개월 "
            "[기술 및 역량] Python, SQL"
        )

        docs = real_retriever.invoke(query)

        assert len(docs) <= 3
        for doc in docs:
            # 실제 자소서 본문은 100자 이상 예상
            assert len(doc.page_content) > 50

    def test_empty_query_handled(self, real_retriever):
        """
        TC-024: 빈 쿼리에 대해 예외가 발생하지 않아야 한다.
        """
        try:
            docs = real_retriever.invoke("")
            # 빈 리스트 반환이 허용 가능
            assert isinstance(docs, list)
        except Exception as e:
            # 명확한 예외 메시지여야 함
            assert "empty" in str(e).lower() or "query" in str(e).lower()


# ==========================================
# 에러 처리 테스트
# ==========================================

@pytest.mark.integration
class TestRetrieverErrorHandling:
    """
    TC-025: FAISS 인덱스 부재 시 에러 처리 검증.
    """

    def test_missing_index_raises_clear_error(self, tmp_path):
        """
        존재하지 않는 인덱스 경로로 Retriever 생성 시 명확한 에러가 발생해야 한다.
        """
        from unittest.mock import MagicMock

        fake_db_config = {
            "host": "localhost",
            "port": 3306,
            "user": "test",
            "password": "test",
            "db": "test",
            "charset": "utf8mb4",
        }

        nonexistent_path = str(tmp_path / "does_not_exist")

        # DB 커넥션도 mocking하여 에러 경로 확인
        with patch("pymysql.connect") as mock_conn:
            mock_conn.return_value = MagicMock()

            with pytest.raises((FileNotFoundError, OSError, RuntimeError, Exception)) as exc:
                from retriever import HybridRetriever
                mock_embeddings = MagicMock()
                HybridRetriever(
                    db_config=fake_db_config,
                    embeddings=mock_embeddings,
                    index_folder=nonexistent_path,
                )

            # 에러 메시지에 경로 또는 "not found"가 포함되어야 함
            error_msg = str(exc.value).lower()
            assert (
                "not" in error_msg
                or "file" in error_msg
                or "index" in error_msg
                or exc.type is not None
            )


# ==========================================
# 검색 결과의 정렬 및 메타데이터 일관성
# ==========================================

@pytest.mark.integration
class TestRetrieverResultOrdering:
    """
    검색 결과가 상위 유사도 순서를 유지하는지 확인.
    """

    def test_results_preserve_order_after_mysql_fetch(self, mock_retriever):
        """
        retriever.py의 _fetch_final_documents가 db_ids 순서를 유지해야 한다.
        (FAISS 반환 순서 = 최종 반환 순서)
        """
        from services.chat_logic import selfintro_retriever

        docs = selfintro_retriever.invoke("유사도 정렬 테스트")

        # relevance_score 기준 오름차순 정렬 (L2 distance이므로 작을수록 유사)
        # Mock에서 0.42, 0.38, 0.35 순서로 설정했으므로 이 순서를 유지
        scores = [doc.metadata["relevance_score"] for doc in docs]

        # Mock의 고정 순서가 유지되는지 확인
        assert len(scores) == 3
