"""
텍스트에서 기술 키워드를 추출하고 정규화하는 데이터 처리 엔진입니다.
"""
import json
from typing import Set, List
from kiwipiepy import Kiwi
from .evaluation_test_config import TECH_DICT_PATH, TECH_SYM_DICT

from backend.utils.bm25_index_builder import BM25IndexBuilder

class KeywordProcessor:
    """
    사용자 자소서와 검색 문서에서 기술 스택 키워드를 정밀하게 추출하는 클래스입니다.
    """
    def __init__(self):
        """
        Kiwi 형태소 분석기를 초기화하고 기술 키워드 사전을 로드합니다.
        """
        self.kiwi = Kiwi()
        self.builder = BM25IndexBuilder()
        with open(TECH_DICT_PATH, "r", encoding="utf-8") as f:
            self.tech_dict = json.load(f)

    def tokenize(self, text: str) -> List[str]:
        """
        입력 텍스트를 BM25 인덱싱에 적합한 토큰 리스트로 변환합니다.
        일관성을 위해 BM25IndexBuilder의 로직을 재사용합니다.
        
        Args:
            text (str): 분석할 원본 텍스트
            
        Returns:
            List[str]: 추출된 명사, 동사, 형용사 등의 토큰 리스트
        """
        return self.builder.tokenize(text)

    def get_query_tech_profile(self, text: str, position: str) -> Set[str]:
        """
        사용자 쿼리(자소서)에서 해당 직무에 유효한 기술 키워드 집합을 추출합니다.
        
        Args:
            text (str): 사용자의 자소서 텍스트
            position (str): 지원 직무
            
        Returns:
            Set[str]: 정규화된 기술 키워드 집합
        """
        valid_techs = set(self.tech_dict.get(position, []))
        if not valid_techs:
            # 해당 직무가 없을 경우 전체 사전의 합집합을 사용
            valid_techs = set(word for techs in self.tech_dict.values() for word in techs)

        tokens = self.kiwi.tokenize(text)
        found_techs = set()

        pos_synonyms = TECH_SYM_DICT.get(position, {})

        for t in tokens:
            word = t.form.lower()
            # 동의어 사전을 사용하여 키워드 정규화
            normalized_word = pos_synonyms.get(word, word)

            if normalized_word in valid_techs:
                found_techs.add(normalized_word)

        return found_techs

    def get_doc_tech_tokens(self, tokens: Set[str], position: str) -> Set[str]:
        """
        문서의 전체 토큰 집합에서 해당 직무의 유효한 기술 키워드만 필터링합니다.
        
        Args:
            tokens (Set[str]): 문서에서 추출된 전체 토큰 집합
            position (str): 지원 직무
            
        Returns:
            Set[str]: 필터링된 기술 키워드 집합
        """
        valid_techs = set(self.tech_dict.get(position, []))
        return tokens.intersection(valid_techs)
