"""
retrieval_service.py

FAISS 검색과 Repository를 조합하여 최종 검색 결과를 제공하는 서비스 계층입니다.
"""

from typing import List, Any
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from repository.retrieval_repository import get_applicant_records_by_ids
from schemas.retrieval_schemas import RetrievalResult


class RetrievalService:
    def __init__(self, embeddings: Any, index_folder: str, top_k: int = 3):
        self.embeddings = embeddings
        self.index_folder = index_folder
        self.top_k = top_k
        self.vectorstore = self._load_vectorstore()

    def _load_vectorstore(self) -> FAISS:
        """FAISS 인덱스 로드"""
        return FAISS.load_local(
            folder_path=self.index_folder,
            embeddings=self.embeddings,
            allow_dangerous_deserialization=True,
        )

    def search(self, query: str) -> List[Document]:
        """
        유사도 검색 수행 후 LangChain Document 객체 리스트 반환 (호환성 유지용)
        """
        # 1. FAISS 유사도 검색
        docs_and_scores = self.vectorstore.similarity_search_with_score(
            query, k=self.top_k
        )

        # 2. 결과 ID 및 메타데이터 추출
        db_ids = []
        score_map = {}
        for doc, score in docs_and_scores:
            db_id = int(doc.page_content)
            db_ids.append(db_id)
            score_map[db_id] = {
                "selfintro_score": doc.metadata.get("selfintro_score", 0),
                "relevance_score": float(score),
            }

        # 3. Repository를 통한 실제 본문 조회
        record_map = get_applicant_records_by_ids(db_ids)

        # 4. Document 객체로 변환 (기존 코드와의 호환성 위해)
        final_docs = []
        for db_id in db_ids:
            if db_id in record_map:
                record = record_map[db_id]
                scores = score_map[db_id]

                doc = Document(
                    page_content=record["selfintro"],
                    metadata={
                        "id": db_id,
                        "selfintro_score": scores["selfintro_score"],
                        "relevance_score": scores["relevance_score"],
                    },
                )
                final_docs.append(doc)

        return final_docs

    def search_as_schema(self, query: str) -> List[RetrievalResult]:
        """
        검색 결과를 정의된 Pydantic 스키마 리스트로 반환
        """
        docs = self.search(query)
        return [
            RetrievalResult(
                id=doc.metadata["id"],
                content=doc.page_content,
                selfintro_score=doc.metadata["selfintro_score"],
                relevance_score=doc.metadata["relevance_score"],
            )
            for doc in docs
        ]
