"""
Retrieval 품질 평가 스크립트.

골든 셋의 각 쿼리에 대해 HybridRetriever를 실행하고,
검색 결과를 정답(relevant_doc_ids)과 비교하여
Recall@K, Precision@K, MRR, nDCG@K 지표를 산출한다.

실행:
    python evaluation/run_retrieval_eval.py
    python evaluation/run_retrieval_eval.py --limit 10
    python evaluation/run_retrieval_eval.py --top-k 3 5 10
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가 (backend 모듈 import용)
EVAL_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = EVAL_ROOT.parent
BACKEND_ROOT = PROJECT_ROOT / "backend"
for p in (str(PROJECT_ROOT), str(BACKEND_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

# 평가 유틸
from evaluation.utils import (  # noqa: E402
    aggregate_metrics,
    build_retrieval_query,
    load_golden_dataset,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
    save_json,
)


# ==========================================
# Argument Parser
# ==========================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Job-Pocket Retrieval 평가 스크립트",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default=str(EVAL_ROOT / "datasets" / "golden_qa.jsonl"),
        help="골든 셋 JSONL 경로",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(EVAL_ROOT / "results" / "retrieval_metrics.json"),
        help="결과 JSON 출력 경로",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        nargs="+",
        default=[3, 5, 10],
        help="Recall@K의 K 값들 (공백 구분)",
    )
    parser.add_argument(
        "--initial-k",
        type=int,
        default=50,
        help="FAISS 1차 후보 수",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="처음 N개 쿼리만 실행 (테스트용)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="쿼리별 상세 출력",
    )
    return parser.parse_args()


# ==========================================
# Retriever 초기화
# ==========================================

def build_retriever(initial_k: int = 50, top_n: int = 10):
    """
    실제 HybridRetriever 인스턴스를 생성한다.

    환경변수 HOST/PORT/USER/PASSWORD/DB 기반으로 DB 접속 설정.
    """
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

    # 평가 시에는 top_n을 크게 잡아 모든 K에서 평가 가능하게 함
    index_path = os.getenv(
        "FAISS_INDEX_PATH",
        str(PROJECT_ROOT / "faiss_index_high"),
    )

    retriever = HybridRetriever(
        db_config=db_config,
        embeddings=embeddings,
        top_n=top_n,
        initial_k=initial_k,
        index_folder=index_path,
    )
    return retriever


# ==========================================
# 메인 평가 로직
# ==========================================

def evaluate_retrieval(
    dataset_path: str,
    top_k_values: list[int],
    initial_k: int,
    limit: int | None,
    verbose: bool,
) -> dict:
    """
    골든 셋의 각 쿼리에 대해 검색을 수행하고 지표를 계산한다.

    Returns:
        평가 결과 dict
    """
    print(f"[평가 시작] 데이터셋: {dataset_path}")
    print(f"[설정] top_k={top_k_values}, initial_k={initial_k}")
    print("")

    # 골든 셋 로드
    dataset = load_golden_dataset(dataset_path, limit=limit)
    print(f"✓ {len(dataset)}개 쿼리 로드")

    # Retriever 초기화 (max_k 기준 top_n 설정)
    max_k = max(top_k_values)
    print("✓ Retriever 초기화 중... (임베딩 모델 로드에 시간 소요)")
    retriever = build_retriever(initial_k=initial_k, top_n=max_k)
    print("✓ Retriever 준비 완료")
    print("")

    # 쿼리별 평가 실행
    per_query_results = []
    failed_queries = []

    start_time = time.time()

    for i, record in enumerate(dataset, start=1):
        query_id = record.get("query_id", f"Q{i:03d}")
        user_profile = record.get("user_profile", {})
        relevant_ids = record.get("relevant_doc_ids", [])

        if not relevant_ids:
            print(f"  [{query_id}] ⚠️ relevant_doc_ids 없음, 스킵")
            continue

        # 검색 쿼리 구성
        query = build_retrieval_query(user_profile)

        # Retriever 실행
        try:
            query_start = time.time()
            docs = retriever.invoke(query)
            query_elapsed = time.time() - query_start

            retrieved_ids = [doc.metadata.get("id") for doc in docs]
            retrieved_ids = [id for id in retrieved_ids if id is not None]
        except Exception as e:
            print(f"  [{query_id}] ❌ 에러: {e}")
            failed_queries.append({"query_id": query_id, "error": str(e)})
            continue

        # 지표 계산
        metrics = {}
        for k in top_k_values:
            metrics[f"recall_at_{k}"] = recall_at_k(retrieved_ids, relevant_ids, k)
            metrics[f"precision_at_{k}"] = precision_at_k(
                retrieved_ids, relevant_ids, k
            )
            metrics[f"ndcg_at_{k}"] = ndcg_at_k(retrieved_ids, relevant_ids, k)
        metrics["mrr"] = reciprocal_rank(retrieved_ids, relevant_ids)
        metrics["query_time_sec"] = query_elapsed

        per_query_results.append({
            "query_id": query_id,
            "retrieved_ids": retrieved_ids[:max_k],
            "relevant_ids": relevant_ids,
            **metrics,
        })

        if verbose:
            print(
                f"  [{query_id}] "
                f"R@3={metrics[f'recall_at_3'] if 3 in top_k_values else '-':.2f} "
                f"MRR={metrics['mrr']:.2f} "
                f"time={query_elapsed:.2f}s"
            )
        else:
            print(f"  [{i}/{len(dataset)}] {query_id} 완료")

    elapsed = time.time() - start_time

    # 집계
    aggregated = aggregate_metrics([
        {k: v for k, v in r.items() if isinstance(v, (int, float))}
        for r in per_query_results
    ])

    # 결과 구성
    result = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "dataset": dataset_path,
            "dataset_size": len(dataset),
            "evaluated": len(per_query_results),
            "failed": len(failed_queries),
            "total_time_sec": round(elapsed, 2),
            "top_k_values": top_k_values,
            "initial_k": initial_k,
        },
        "aggregated_metrics": aggregated,
        "per_query_results": per_query_results,
        "failed_queries": failed_queries,
    }

    return result


# ==========================================
# 결과 출력
# ==========================================

def print_summary(result: dict) -> None:
    """콘솔에 요약 출력."""
    print("\n" + "=" * 60)
    print("📊 Retrieval 평가 결과 요약")
    print("=" * 60)

    meta = result["metadata"]
    print(f"\n평가 일시: {meta['timestamp']}")
    print(f"평가 건수: {meta['evaluated']}/{meta['dataset_size']}")
    print(f"실패 건수: {meta['failed']}")
    print(f"소요 시간: {meta['total_time_sec']}초")

    print("\n📈 주요 지표 (평균)")
    print("-" * 60)
    agg = result["aggregated_metrics"]
    for key in sorted(agg.keys()):
        if key.endswith("_mean"):
            display_key = key.replace("_mean", "")
            print(f"  {display_key:20s}: {agg[key]:.4f}")

    # 통과 여부 판정
    print("\n🎯 목표 대비 평가")
    print("-" * 60)
    thresholds = {
        "recall_at_3_mean": (0.60, "목표", 0.50, "최소"),
        "mrr_mean": (0.45, "목표", 0.35, "최소"),
    }
    for key, (target, target_label, min_val, min_label) in thresholds.items():
        if key not in agg:
            continue
        value = agg[key]
        if value >= target:
            status = f"✅ 목표 달성 ({target})"
        elif value >= min_val:
            status = f"🟡 최소 허용 ({min_val}) 이상, 목표 ({target}) 미달"
        else:
            status = f"❌ 최소 허용 ({min_val}) 미만"
        print(f"  {key:25s}: {value:.4f}  {status}")

    print("")


# ==========================================
# 엔트리 포인트
# ==========================================

def main():
    args = parse_args()

    try:
        result = evaluate_retrieval(
            dataset_path=args.dataset,
            top_k_values=args.top_k,
            initial_k=args.initial_k,
            limit=args.limit,
            verbose=args.verbose,
        )
    except FileNotFoundError as e:
        print(f"❌ 파일을 찾을 수 없음: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ 평가 실행 실패: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # 결과 저장
    save_json(result, args.output)
    print(f"✓ 결과 저장: {args.output}")

    # 요약 출력
    print_summary(result)


if __name__ == "__main__":
    main()
