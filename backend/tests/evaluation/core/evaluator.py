"""
사용자 쿼리와 검색 결과 간의 기술 스택 매칭률을 계산하는 핵심 평가 로직입니다.
"""
import pickle
from typing import List, Dict, Any
from .evaluation_test_config import BM25_INDEX_PATH
from . import KeywordProcessor

class RetrievalEvaluator:
    """
    리트리벌 시스템의 정확도를 기술 스택 매칭률 기반으로 평가하는 클래스입니다.
    """
    def __init__(self, processor: KeywordProcessor):
        """
        평가기를 초기화하고 BM25 인덱스를 로드합니다.
        
        Args:
            processor (KeywordProcessor): 키워드 추출 및 토큰화 처리를 담당하는 객체
        """
        self.processor = processor
        with open(BM25_INDEX_PATH, 'rb') as f:
            self.bm25_by_position = pickle.load(f)
        
        # 빠른 조회를 위해 db_id를 인덱스로 매핑
        self.id_to_idx_map = {}
        for pos, entry in self.bm25_by_position.items():
            db_ids = entry.get('db_ids', [])
            self.id_to_idx_map[pos] = {db_id: i for i, db_id in enumerate(db_ids)}

    def evaluate_matches(self, query_text: str, retrieved_ids: List[int], position: str) -> Dict[str, Any]:
        """
        사용자 쿼리와 검색된 문서들 간의 기술 키워드 일치 여부를 분석합니다.
        
        Args:
            query_text (str): 사용자의 원본 자소서 텍스트
            retrieved_ids (List[int]): 리트리버가 검색한 문서 ID 리스트
            position (str): 지원 직무 (예: 'backend engineer')
            
        Returns:
            Dict[str, Any]: 쿼리 기술 스택과 각 문서별 매칭 분석 결과가 포함된 딕셔너리
        """
        query_techs = self.processor.get_query_tech_profile(query_text, position)
        
        entry = self.bm25_by_position.get(position)
        if not entry or not query_techs:
            return {"query_techs": sorted(list(query_techs)), "results": []}

        bm25_obj = entry['bm25']
        pos_id_map = self.id_to_idx_map.get(position, {})
        
        analysis_results = []
        for db_id in retrieved_ids:
            idx = pos_id_map.get(db_id)
            if idx is not None:
                # BM25 인덱스에 저장된 사전 계산 토큰 활용
                doc_raw_tokens = set(bm25_obj.doc_freqs[idx].keys())
                doc_techs = self.processor.get_doc_tech_tokens(doc_raw_tokens, position)
                
                matched = query_techs.intersection(doc_techs)
                missing = query_techs - doc_techs
                match_ratio = len(matched) / len(query_techs) if query_techs else 0
                
                analysis_results.append({
                    "db_id": db_id,
                    "match_ratio": round(match_ratio, 4),
                    "matched_count": len(matched),
                    "matched_list": sorted(list(matched)),
                    "missing_list": sorted(list(missing))
                })
            else:
                # BM25 인덱스에서 ID를 찾을 수 없는 경우 처리
                analysis_results.append({
                    "db_id": db_id,
                    "match_ratio": 0,
                    "matched_count": 0,
                    "matched_list": [],
                    "missing_list": sorted(list(query_techs)),
                    "error": "ID not found in BM25 index"
                })
        
        return {
            "query_techs": sorted(list(query_techs)),
            "results": analysis_results
        }
