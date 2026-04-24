"""
Job-Pocket RAG 평가 공용 유틸리티.

Retrieval 지표 계산, 골든 셋 로딩, 쿼리 구성, 파일 I/O를 담당한다.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Iterator


# ==========================================
# 경로 상수
# ==========================================

EVAL_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = EVAL_ROOT.parent

DEFAULT_DATASET = EVAL_ROOT / "datasets" / "golden_qa.jsonl"
RESULTS_DIR = EVAL_ROOT / "results"


# ==========================================
# 데이터 로딩
# ==========================================

def load_golden_dataset(
    path: str | Path = DEFAULT_DATASET,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """
    골든 셋을 JSONL에서 로드한다.

    Args:
        path: 파일 경로
        limit: 처음 N개만 로드 (테스트용, None이면 전체)

    Returns:
        각 레코드의 dict 리스트
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"골든 셋을 찾을 수 없음: {path}")

    records = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"골든 셋 {i+1}번째 줄 파싱 실패: {e}"
                )

            if limit is not None and len(records) >= limit:
                break

    return records


def build_retrieval_query(user_profile: dict[str, str]) -> str:
    """
    사용자 프로필 dict을 검색 쿼리 문자열로 변환한다.
    chat_logic.get_sample_context와 동일한 포맷을 사용한다.
    """
    return (
        f"[최종학력] {user_profile.get('school', '')} "
        f"{user_profile.get('major', '')}\n"
        f"[경력 및 경험]\n"
        f"{user_profile.get('exp', '')}\n"
        f"{user_profile.get('awards', '')}\n"
        f"[기술 및 역량]\n"
        f"{user_profile.get('tech', '')}"
    )


# ==========================================
# Retrieval 지표
# ==========================================

def recall_at_k(
    retrieved_ids: list[int],
    relevant_ids: list[int],
    k: int,
) -> float:
    """
    Recall@K: 상위 K개 중 정답이 포함된 비율.

    정답이 여러 개일 수 있으므로, 정답 셋에 있는 ID 중 상위 K에 든 비율.
    """
    if not relevant_ids:
        return 0.0

    top_k = set(retrieved_ids[:k])
    hit = top_k & set(relevant_ids)
    return len(hit) / len(relevant_ids)


def precision_at_k(
    retrieved_ids: list[int],
    relevant_ids: list[int],
    k: int,
) -> float:
    """Precision@K: 상위 K개 중 관련 문서의 비율."""
    if k == 0:
        return 0.0

    top_k = set(retrieved_ids[:k])
    hit = top_k & set(relevant_ids)
    return len(hit) / k


def reciprocal_rank(
    retrieved_ids: list[int],
    relevant_ids: list[int],
) -> float:
    """
    정답 중 가장 먼저 나오는 문서의 역순위.
    정답이 하나도 없으면 0.
    """
    relevant_set = set(relevant_ids)
    for idx, doc_id in enumerate(retrieved_ids, start=1):
        if doc_id in relevant_set:
            return 1.0 / idx
    return 0.0


def dcg_at_k(
    retrieved_ids: list[int],
    relevant_ids: list[int],
    k: int,
) -> float:
    """Discounted Cumulative Gain@K. 관련 문서는 relevance=1로 처리."""
    relevant_set = set(relevant_ids)
    dcg = 0.0
    for idx, doc_id in enumerate(retrieved_ids[:k], start=1):
        if doc_id in relevant_set:
            # log_2(idx + 1)로 나눔
            dcg += 1.0 / math.log2(idx + 1)
    return dcg


def ndcg_at_k(
    retrieved_ids: list[int],
    relevant_ids: list[int],
    k: int,
) -> float:
    """Normalized DCG@K. 이상적 순서(IDCG)로 정규화."""
    dcg = dcg_at_k(retrieved_ids, relevant_ids, k)

    # IDCG: 모든 정답이 최상단에 있는 경우
    ideal_count = min(len(relevant_ids), k)
    idcg = sum(1.0 / math.log2(i + 2) for i in range(ideal_count))

    if idcg == 0:
        return 0.0
    return dcg / idcg


# ==========================================
# Generation 지표
# ==========================================

def char_limit_adherence(
    text: str,
    target: int | None,
    tolerance: float = 0.15,
) -> bool:
    """글자 수가 목표의 ±tolerance 이내인가."""
    if not target:
        return True  # 목표 없으면 통과
    actual = len(text)
    return abs(actual - target) / target <= tolerance


def contains_overstatement(text: str) -> tuple[bool, list[str]]:
    """
    chat_logic.OVERSTATEMENT_PATTERNS와 동일한 9종 금지 표현을 검사한다.
    """
    patterns = [
        "차별화된 경쟁력을 확보",
        "사회적 영향력을 확대",
        "혁신을 선도",
        "업계를 선도",
        "압도적인 성과",
        "무궁한 발전",
        "최고의 인재",
        "실현하겠습니다",
        "주도하겠습니다",
    ]
    found = [p for p in patterns if p in text]
    return bool(found), found


def repetition_ratio(text: str) -> float:
    """
    문장 반복률 계산. chat_logic.repetition_ratio와 동일.
    """
    import re

    sentences = re.split(r"(?<=[.!?다요])\s+", text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]
    if not sentences:
        return 1.0
    unique = len(set(sentences))
    return 1 - (unique / len(sentences))


# ==========================================
# 집계 통계
# ==========================================

def aggregate_metrics(
    per_query_results: list[dict[str, float]],
) -> dict[str, float]:
    """
    개별 쿼리별 지표 dict 리스트를 받아 평균·표준편차를 계산한다.
    """
    if not per_query_results:
        return {}

    keys = per_query_results[0].keys()
    aggregated = {}

    for key in keys:
        values = [r.get(key, 0.0) for r in per_query_results]
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        std = math.sqrt(variance)
        aggregated[f"{key}_mean"] = round(mean, 4)
        aggregated[f"{key}_std"] = round(std, 4)

    return aggregated


# ==========================================
# 결과 저장
# ==========================================

def save_json(data: Any, path: str | Path) -> None:
    """결과 dict을 JSON으로 저장. 디렉토리가 없으면 생성."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def iter_jsonl(path: str | Path) -> Iterator[dict[str, Any]]:
    """JSONL 파일을 줄 단위 iterator로 로드."""
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


# ==========================================
# 리포트 생성 보조
# ==========================================

def format_metric_table(metrics: dict[str, float]) -> str:
    """
    metrics dict을 Markdown 표로 변환.

    예: {"recall_at_3_mean": 0.67, "mrr_mean": 0.51}
    """
    lines = ["| 지표 | 값 |", "|---|---|"]
    for key, value in metrics.items():
        if isinstance(value, float):
            lines.append(f"| {key} | {value:.4f} |")
        else:
            lines.append(f"| {key} | {value} |")
    return "\n".join(lines)
