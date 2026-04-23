from pymysql import Error
from pymysql.cursors import DictCursor
from typing import Any, List, Dict
from langchain_community.vectorstores import FAISS
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document

# from langsmith import traceable # LangSmith 추적용
from pydantic import ConfigDict
from common.db import vector_engine


class HybridRetriever(BaseRetriever):
    embeddings: Any = None
    top_k: int = 3
    vectorstore: FAISS = None
    index_folder: str = "faiss_index"

    @property
    def _engine(self):
        return vector_engine

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    def _get_vector_index(self):
        """서버 기동 시 빌드된 FAISS index를 불러옴"""
        self.vectorstore = FAISS.load_local(
            folder_path=self.index_folder,
            embeddings=self.embeddings,
            allow_dangerous_deserialization=True,
        )

    # @traceable(name="Vector Search", process_inputs=lambda x: {}, process_outputs=lambda x: {})
    def _get_relevant_documents(self, query: str) -> List[Document]:
        """similarity_search로 상위 k개를 반환"""
        if self.vectorstore is None:
            self._get_vector_index()

        # 1. FAISS 유사도 검색 (상위 top_k개 후보 추출)
        # LangChain의 similarity_search_with_score는 내부적으로 쿼리 벡터를 정규화하여 검색함
        docs_and_scores = self.vectorstore.similarity_search_with_score(
            query, k=self.top_k
        )

        # 이력서 유사도 점수와 자소서 평가 점수를 하나의 map으로 관리
        score_map = {
            int(doc.page_content): (
                doc.metadata.get("selfintro_score", 0),
                float(score),
            )
            for doc, score in docs_and_scores
        }

        # 검색된 이력서의 DB row index 추출
        target_db_ids = [int(doc.page_content) for doc, _ in docs_and_scores]

        # DB에서 '진짜 자소서 본문' 페치
        return self._fetch_final_documents(target_db_ids, score_map)

    def _fetch_final_documents(
        self, db_ids: List[int], score_map: Dict[int, float]
    ) -> List[Document]:
        """db_ids에 해당하는 실제 자소서를 반환"""
        if not db_ids:
            return []

        conn = self._engine.raw_connection()

        try:
            with conn.cursor(DictCursor) as c:
                format_strings = ",".join(["%s"] * len(db_ids))

                # DB에서 자소서 원문 가져오기
                sql = f"""
                SELECT id, selfintro
                FROM applicant_records
                WHERE id IN ({format_strings})
                """
                c.execute(sql, tuple(db_ids))
                rows = c.fetchall()

                id_map = {r["id"]: r for r in rows}

                # 원래 유사도 순서(db_ids)를 유지하며 Document 객체 생성
                final_docs = []
                for db_id in db_ids:
                    if db_id in id_map:
                        record = id_map[db_id]

                        # Document 객체 생성
                        doc = Document(
                            # 실제 검색에 사용될 메인 텍스트 (자소서)
                            page_content=record["selfintro"],
                            metadata={
                                "id": db_id,  # 컬럼 추가 조회가 필요할 시 활용 가능
                                "selfintro_score": score_map.get(db_id)[
                                    0
                                ],  # 자소서 평가 점수 (최대 60점)
                                "relevance_score": score_map.get(db_id)[
                                    1
                                ],  # 리트리버가 계산한 유사도 점수
                            },
                        )
                        final_docs.append(doc)

                return final_docs
        except Error as e:
            print(f"❌ MySQL 에러: {e}")
            return []
        finally:
            conn.close()