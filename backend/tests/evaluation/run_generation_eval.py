"""
Generation 품질 평가 스크립트.

골든 셋의 각 쿼리에 대해 파이프라인을 실행하고, 생성된 자소서의 품질을 평가한다.

지표:
    - 품질 검증 통과율 (score_local_draft 1회 시도)
    - 재생성 횟수 평균
    - 과장 표현 포함률
    - 글자 수 달성률 (char_limit ±15%)
    - LLM-as-Judge 평균 점수 (5점 척도)

실행:
    python evaluation/run_generation_eval.py
    python evaluation/run_generation_eval.py --limit 5 --skip-judge
    python evaluation/run_generation_eval.py --model "GPT-OSS-120B (Groq)"
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

# 프로젝트 루트 경로 설정
EVAL_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = EVAL_ROOT.parent
BACKEND_ROOT = PROJECT_ROOT / "backend"
for p in (str(PROJECT_ROOT), str(BACKEND_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

from evaluation.utils import (  # noqa: E402
    aggregate_metrics,
    char_limit_adherence,
    contains_overstatement,
    load_golden_dataset,
    repetition_ratio,
    save_json,
)


# ==========================================
# Argument Parser
# ==========================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Job-Pocket Generation 평가 스크립트",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default=str(EVAL_ROOT / "datasets" / "golden_qa.jsonl"),
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(EVAL_ROOT / "results" / "generation_metrics.json"),
    )
    parser.add_argument(
        "--model",
        type=str,
        default="GPT-4o-mini",
        help="생성·첨삭 모델",
    )
    parser.add_argument(
        "--judge-model",
        type=str,
        default="gpt-4o-mini",
        help="LLM-as-Judge 평가자 모델",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
    )
    parser.add_argument(
        "--skip-judge",
        action="store_true",
        help="LLM-as-Judge 스킵 (API 비용 절감용)",
    )
    return parser.parse_args()


# ==========================================
# 파이프라인 실행
# ==========================================

def build_user_info_tuple(user_profile: dict) -> list:
    """
    골든 셋의 user_profile을 chat_logic이 기대하는 5-tuple 형식으로 변환.
    """
    resume_data = {
        "personal": {"gender": user_profile.get("gender", "선택안함")},
        "education": {
            "school": user_profile.get("school", ""),
            "major": user_profile.get("major", ""),
        },
        "additional": {
            "internship": user_profile.get("exp", ""),
            "awards": user_profile.get("awards", ""),
            "tech_stack": user_profile.get("tech", ""),
        },
    }
    return [
        "평가유저",
        "hashed_pw_dummy",
        "eval@example.com",
        None,
        json.dumps(resume_data, ensure_ascii=False),
    ]


def build_prompt(record: dict) -> str:
    """골든 셋 레코드를 사용자 자연어 요청으로 변환."""
    company = record.get("company", "")
    job = record.get("job", "")
    question = record.get("question", "")
    char_limit = record.get("char_limit")

    limit_str = f"{char_limit}자 내외로" if char_limit else ""

    return f"{company}에 {job} 포지션으로 지원합니다. {question} {limit_str}".strip()


def run_pipeline(record: dict, model: str) -> dict:
    """
    단일 쿼리에 대해 자소서 생성 파이프라인을 실행한다.

    Returns:
        {
            "draft": str,
            "refined": str,
            "adjusted": str,
            "final": str,
            "regeneration_count": int,
            "draft_passed_quality_check": bool,
            ...
        }
    """
    from services import chat_logic

    prompt = build_prompt(record)
    user_info = tuple(build_user_info_tuple(record.get("user_profile", {})))

    # Step 1: Parse (자체적으로 regex + 필요 시 LLM)
    parsed = chat_logic.parse_user_request(prompt, model)

    # Step 2: Draft (재생성 메커니즘 포함)
    regeneration_count = 0
    draft = chat_logic.regenerate_local_draft_if_needed(
        user_message=prompt,
        user_profile=user_info,
        selected_model=model,
        max_attempts=3,
    )

    # Draft의 품질 판정
    passed, reason = chat_logic.score_local_draft(draft, parsed)

    # Step 3: Refine
    try:
        refined = chat_logic.refine_with_api(draft, prompt, model)
    except Exception:
        refined = draft

    # Step 4: Fit
    try:
        adjusted = chat_logic.fit_length_if_needed(refined, prompt, model)
    except Exception:
        adjusted = refined

    return {
        "parsed": parsed,
        "draft": draft,
        "refined": refined,
        "adjusted": adjusted,
        "draft_passed_quality_check": passed,
        "draft_fail_reason": reason if not passed else "",
    }


# ==========================================
# LLM-as-Judge
# ==========================================

JUDGE_PROMPT_SYSTEM = """당신은 한국어 자기소개서 평가 전문가다.
다음 자기소개서를 아래 5개 기준으로 각각 1~5점으로 평가하라.
각 기준에 대한 짧은 이유(한 문장)도 함께 제공하라.

평가 기준:
1. 문항 적합성: 질문 유형에 맞는 서술 흐름인가
2. 직무 적합성: 지원 직무와 사용자 이력의 연결이 자연스러운가
3. 이력 반영도: 사용자 정보가 자연스럽게 녹아있는가
4. 서술 완성도: 첫 문장과 마지막 문단의 완성도가 높은가
5. 문체 품질: 과장 없이 담백하고 설득력 있는가

반드시 JSON만 출력하라. 예시 형식:
{
  "문항_적합성": {"score": 4, "reason": "..."},
  "직무_적합성": {"score": 3, "reason": "..."},
  "이력_반영도": {"score": 4, "reason": "..."},
  "서술_완성도": {"score": 3, "reason": "..."},
  "문체_품질": {"score": 4, "reason": "..."}
}"""


def llm_judge(
    essay: str,
    record: dict,
    judge_model: str = "gpt-4o-mini",
) -> dict:
    """
    LLM에게 자소서 품질을 5개 기준으로 1~5점 평가 요청.

    Returns:
        {"문항_적합성": {"score": 4, "reason": "..."}, ...,
         "평균": 3.6}
    """
    try:
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_openai import ChatOpenAI

        judge_llm = ChatOpenAI(model=judge_model, temperature=0.0)

        company = record.get("company", "미기재")
        job = record.get("job", "미기재")
        question = record.get("question", "미기재")
        question_type = record.get("question_type", "general")

        prompt = ChatPromptTemplate.from_messages([
            ("system", JUDGE_PROMPT_SYSTEM),
            ("human", f"""[지원 정보]
- 회사: {company}
- 직무: {job}
- 문항: {question}
- 문항 유형: {question_type}

[평가 대상 자소서]
{essay}
""")
        ])

        chain = prompt | judge_llm | StrOutputParser()
        raw = chain.invoke({}).strip()

        # JSON 추출
        start = raw.find("{")
        end = raw.rfind("}")
        if start == -1 or end == -1:
            return {"error": "JSON 파싱 실패", "raw": raw[:200]}

        parsed = json.loads(raw[start:end + 1])

        # 평균 계산
        scores = []
        for key, val in parsed.items():
            if isinstance(val, dict) and "score" in val:
                scores.append(val["score"])
        avg = sum(scores) / len(scores) if scores else 0.0
        parsed["평균"] = round(avg, 2)

        return parsed

    except Exception as e:
        return {"error": str(e)}


# ==========================================
# 단일 쿼리 평가
# ==========================================

def evaluate_single_query(
    record: dict,
    model: str,
    judge_model: str,
    skip_judge: bool,
) -> dict:
    """단일 쿼리에 대해 전체 평가를 수행한다."""
    query_id = record.get("query_id", "unknown")

    # 파이프라인 실행
    t_start = time.time()
    try:
        pipeline_result = run_pipeline(record, model)
    except Exception as e:
        return {
            "query_id": query_id,
            "error": f"파이프라인 실패: {e}",
        }
    elapsed = time.time() - t_start

    final_essay = pipeline_result["adjusted"]
    draft_essay = pipeline_result["draft"]

    # 정량 지표 계산
    char_limit = record.get("char_limit")
    has_overstatement, found_patterns = contains_overstatement(final_essay)

    metrics = {
        "query_id": query_id,
        "char_count": len(final_essay),
        "target_char_limit": char_limit,
        "char_limit_adherence": char_limit_adherence(final_essay, char_limit),
        "has_overstatement": has_overstatement,
        "overstatement_patterns": found_patterns,
        "repetition_ratio": round(repetition_ratio(final_essay), 4),
        "draft_passed_quality_check": pipeline_result["draft_passed_quality_check"],
        "draft_fail_reason": pipeline_result.get("draft_fail_reason", ""),
        "pipeline_time_sec": round(elapsed, 2),
        "final_essay_sample": final_essay[:150] + "..." if len(final_essay) > 150 else final_essay,
    }

    # LLM-as-Judge
    if not skip_judge:
        judge_result = llm_judge(final_essay, record, judge_model)
        metrics["judge"] = judge_result
        if "평균" in judge_result:
            metrics["judge_avg_score"] = judge_result["평균"]

    return metrics


# ==========================================
# 메인 평가 루프
# ==========================================

def evaluate_generation(
    dataset_path: str,
    model: str,
    judge_model: str,
    limit: int | None,
    skip_judge: bool,
) -> dict:
    """골든 셋 전체에 대해 생성 품질을 평가한다."""
    print(f"[평가 시작] 데이터셋: {dataset_path}")
    print(f"[설정] model={model}, judge={judge_model}, skip_judge={skip_judge}")
    print("")

    dataset = load_golden_dataset(dataset_path, limit=limit)
    print(f"✓ {len(dataset)}개 쿼리 로드")
    print("")

    per_query_results = []
    failed = []

    t_start = time.time()

    for i, record in enumerate(dataset, start=1):
        query_id = record.get("query_id", f"Q{i:03d}")
        print(f"  [{i}/{len(dataset)}] {query_id} 평가 중...")

        result = evaluate_single_query(record, model, judge_model, skip_judge)

        if "error" in result:
            print(f"    ❌ {result['error']}")
            failed.append(result)
        else:
            passed_msg = "✓" if result["draft_passed_quality_check"] else "✗"
            judge_msg = (
                f"judge={result.get('judge_avg_score', '-')}"
                if not skip_judge else "judge=skip"
            )
            print(
                f"    {passed_msg} "
                f"chars={result['char_count']}/{result.get('target_char_limit', '-')} "
                f"overstate={result['has_overstatement']} "
                f"{judge_msg} "
                f"time={result['pipeline_time_sec']}s"
            )
            per_query_results.append(result)

    elapsed = time.time() - t_start

    # 집계
    quality_pass_count = sum(
        1 for r in per_query_results if r.get("draft_passed_quality_check")
    )
    overstatement_count = sum(
        1 for r in per_query_results if r.get("has_overstatement")
    )
    char_limit_hit = sum(
        1 for r in per_query_results if r.get("char_limit_adherence")
    )

    n = len(per_query_results) if per_query_results else 1

    aggregated = {
        "quality_check_pass_rate": round(quality_pass_count / n, 4),
        "overstatement_rate": round(overstatement_count / n, 4),
        "char_limit_hit_rate": round(char_limit_hit / n, 4),
        "avg_pipeline_time_sec": round(
            sum(r.get("pipeline_time_sec", 0) for r in per_query_results) / n, 2
        ),
        "avg_char_count": round(
            sum(r.get("char_count", 0) for r in per_query_results) / n, 1
        ),
    }

    if not skip_judge:
        judge_scores = [
            r.get("judge_avg_score", 0)
            for r in per_query_results
            if r.get("judge_avg_score")
        ]
        if judge_scores:
            aggregated["judge_avg_score"] = round(
                sum(judge_scores) / len(judge_scores), 2
            )

    result = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "dataset": dataset_path,
            "dataset_size": len(dataset),
            "evaluated": len(per_query_results),
            "failed": len(failed),
            "total_time_sec": round(elapsed, 2),
            "model": model,
            "judge_model": judge_model if not skip_judge else None,
        },
        "aggregated_metrics": aggregated,
        "per_query_results": per_query_results,
        "failed_queries": failed,
    }

    return result


# ==========================================
# 결과 출력
# ==========================================

def print_summary(result: dict) -> None:
    """요약을 콘솔에 출력."""
    print("\n" + "=" * 60)
    print("📊 Generation 평가 결과 요약")
    print("=" * 60)

    meta = result["metadata"]
    print(f"\n평가 일시: {meta['timestamp']}")
    print(f"평가 건수: {meta['evaluated']}/{meta['dataset_size']}")
    print(f"모델: {meta['model']}")
    print(f"소요 시간: {meta['total_time_sec']}초")

    print("\n📈 지표")
    print("-" * 60)
    for key, value in result["aggregated_metrics"].items():
        if isinstance(value, float):
            print(f"  {key:30s}: {value:.4f}")
        else:
            print(f"  {key:30s}: {value}")

    # 판정
    print("\n🎯 목표 대비 평가")
    print("-" * 60)
    agg = result["aggregated_metrics"]
    checks = [
        ("quality_check_pass_rate", 0.75, "품질 통과율 ≥ 75%"),
        ("overstatement_rate", 0.05, "과장 표현률 ≤ 5%", True),  # 낮을수록 좋음
        ("char_limit_hit_rate", 0.90, "글자수 달성률 ≥ 90%"),
    ]
    if "judge_avg_score" in agg:
        checks.append(("judge_avg_score", 3.5, "LLM-as-Judge ≥ 3.5/5"))

    for check in checks:
        key = check[0]
        target = check[1]
        label = check[2]
        lower_is_better = check[3] if len(check) > 3 else False

        if key not in agg:
            continue
        value = agg[key]
        if lower_is_better:
            ok = value <= target
        else:
            ok = value >= target
        symbol = "✅" if ok else "❌"
        print(f"  {symbol} {label:35s} (현재: {value})")

    print("")


# ==========================================
# 엔트리 포인트
# ==========================================

def main():
    args = parse_args()

    try:
        result = evaluate_generation(
            dataset_path=args.dataset,
            model=args.model,
            judge_model=args.judge_model,
            limit=args.limit,
            skip_judge=args.skip_judge,
        )
    except FileNotFoundError as e:
        print(f"❌ 파일을 찾을 수 없음: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ 평가 실행 실패: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

    save_json(result, args.output)
    print(f"✓ 결과 저장: {args.output}")

    print_summary(result)


if __name__ == "__main__":
    main()
