"""
BM25 인덱스 빌더 모듈

이 모듈은 데이터베이스의 데이터를 활용하여 직무별 BM25 인덱스를 구축하고 저장하는 기능을 제공합니다.
사용자의 자소서와 지원 공고 간의 키워드 유사도를 계산하기 위한 검색 엔진의 기반이 됩니다.
"""

import pickle
import numpy as np
from pathlib import Path
from pymysql.cursors import DictCursor
from typing import List, Dict
from rank_bm25 import BM25Okapi
from kiwipiepy import Kiwi

# 내부 의존성
from common.db import vector_engine

# 상수 정의
BASE_DIR = Path(__file__).resolve().parents[1]
BM25_INDEX_PATH = BASE_DIR / "utils" / "bm25_index.pkl"

class BM25IndexBuilder:
    """
    데이터베이스 데이터를 기반으로 BM25 인덱스를 구축하는 클래스입니다.
    """
    def __init__(self):
        self.kiwi = Kiwi()
        self.bm25_by_position = {}

    def tokenize(self, text: str) -> List[str]:
        """
        BM25 인덱싱을 위한 일반적인 토큰화 프로세스입니다.
        명사, 동사, 형용사, 영어 및 숫자를 추출합니다.
        """
        target_pos = {
            'NNG', 'NNP',  # 명사
            'VV', 'VA',    # 동사, 형용사
            'SL',          # 영어
            'SN',          # 숫자
        }
        tokenized_text = self.kiwi.tokenize(text)
        return [token.form.lower() for token in tokenized_text if token.tag in target_pos]

    def build_from_db(self):
        """
        DB에서 정제된 자소서와 직무 타입을 가져와 BM25 인덱스를 생성합니다.
        """
        conn = vector_engine.raw_connection()
        try:
            with conn.cursor(DictCursor) as cursor:
                sql = """
                SELECT
                    j.position_type,
                    r.id,
                    r.resume_cleaned
                FROM job_posts j
                JOIN applicant_records r ON j.id = r.jobpost_id
                """
                cursor.execute(sql)
                rows = cursor.fetchall()

            if not rows:
                print("⚠️ DB에 데이터가 없습니다.")
                return

            print(f"✅ DB에서 {len(rows)}건 로드 완료")
            
            # 직무별로 데이터 그룹화
            position_data = {}
            for row in rows:
                pos = row['position_type']
                if pos not in position_data:
                    position_data[pos] = {'db_ids': [], 'resumes': []}
                position_data[pos]['db_ids'].append(row['id'])
                position_data[pos]['resumes'].append(row['resume_cleaned'])

            # 각 직무별로 BM25 인덱스 빌드
            for pos, data in position_data.items():
                print(f"⏳ [{pos}] BM25 인덱싱 중...")
                tokenized = [self.tokenize(r) for r in data['resumes']]
                self.bm25_by_position[pos] = {
                    'bm25': BM25Okapi(tokenized),
                    'db_ids': data['db_ids']
                }
                print(f"✅ [{pos}] 빌드 완료: {len(data['db_ids'])}건")

        except Exception as e:
            print(f"❌ DB 조회 에러: {e}")
            raise e
        finally:
            conn.close()

    def save(self):
        """구축된 BM25 인덱스를 기본 경로에 저장합니다."""
        BM25_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(BM25_INDEX_PATH, 'wb') as f:
            pickle.dump(self.bm25_by_position, f)
        print(f"💾 BM25 인덱스 저장 완료: {BM25_INDEX_PATH}")

    def load(self) -> bool:
        """저장된 BM25 인덱스가 존재하면 이를 로드합니다."""
        if not BM25_INDEX_PATH.exists():
            return False
        with open(BM25_INDEX_PATH, 'rb') as f:
            self.bm25_by_position = pickle.load(f)
        print(f"📂 BM25 인덱스 로드 완료: {BM25_INDEX_PATH}")
        return True

if __name__ == "__main__":
    builder = BM25IndexBuilder()
    builder.build_from_db()
    builder.save()
