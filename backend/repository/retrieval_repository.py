"""
retrieval_repository.py

applicant_records 테이블에서 실제 자소서 데이터를 조회하는 Repository입니다.
"""

from typing import List, Dict
from pymysql.cursors import DictCursor
from common.db import vector_engine


def get_applicant_records_by_ids(db_ids: List[int]) -> Dict[int, Dict]:
    """
    ID 리스트를 받아 해당하는 자소서 레코드를 조회하여 맵 형태로 반환합니다.

    Args:
        db_ids: 조회할 레코드 ID 리스트

    Returns:
        { id: { "id": int, "selfintro": str }, ... } 형태의 딕셔너리
    """
    if not db_ids:
        return {}

    raw_conn = vector_engine.raw_connection()
    try:
        with raw_conn.cursor(DictCursor) as c:
            format_strings = ",".join(["%s"] * len(db_ids))
            sql = f"""
                SELECT id, selfintro
                FROM applicant_records
                WHERE id IN ({format_strings})
            """
            c.execute(sql, tuple(db_ids))
            rows = c.fetchall()

            return {row["id"]: row for row in rows}
    finally:
        raw_conn.close()
