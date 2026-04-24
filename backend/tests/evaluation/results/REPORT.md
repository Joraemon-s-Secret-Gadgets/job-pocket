# 📊 Job-Pocket RAG 평가 결과 리포트

> **목적**: Retrieval 및 Generation 평가의 수행 결과를 통합 기록한다. 지표·분석·권고 사항을 포함한다.
> **작성일**: 2026-04-22
> **버전**: v0.2.0 (평가 준비)
> **관련 문서**: `docs/wiki/model/test.md`, `docs/wiki/test/test_plan.md`

---

## 1. 요약

### 1.1 현재 상태

v0.2.0 시점에서는 정식 평가가 수행되지 않았다. 이는 다음 전제 조건들이 충족되지 않았기 때문이다:

- `backend/main.py`의 라우터 주석 버그 (D-001)
- FAISS 인덱스 부재 (D-004)
- MySQL `applicant_records` 데이터 미적재
- 골든 셋 20~30건 목표 대비 5건 샘플만 준비됨

본 리포트는 **v0.3.0 정식 평가 시 채워질 템플릿**으로, 평가 실행 스크립트(`run_retrieval_eval.py`, `run_generation_eval.py`)가 자동으로 지표를 채워 넣을 구조다.

### 1.2 예상 일정

| 단계 | 예상 시점 |
|---|---|
| 선행 조건 해결 (D-001, D-004) | v0.2.1 |
| 데이터 적재 + FAISS 빌드 | v0.3.0 초 |
| 골든 셋 30건 구축 | v0.3.0 중 |
| 1차 평가 실행 | v0.3.0 중 |
| 개선 반영 및 재평가 | v0.3.0 말 |

---

## 2. 평가 설정

### 2.1 평가 환경 (v0.3.0 예정)

| 항목 | 값 |
|---|---|
| 골든 셋 | `evaluation/datasets/golden_qa.jsonl` |
| 목표 규모 | 20~30건 |
| 생성 모델 | EXAONE 3.5 7.8B (via RunPod) + GPT-4o-mini (Refine) |
| 임베딩 모델 | Qwen3-Embedding-0.6B (CPU) |
| FAISS `initial_k` | 50 |
| Retriever `top_n` | 3 |
| 평가자 LLM | GPT-4o-mini (temperature=0.0) |

### 2.2 평가 실행 명령

```bash
# Retrieval
python evaluation/run_retrieval_eval.py \
  --dataset evaluation/datasets/golden_qa.jsonl \
  --top-k 3 5 10 \
  --verbose

# Generation
python evaluation/run_generation_eval.py \
  --dataset evaluation/datasets/golden_qa.jsonl \
  --model GPT-4o-mini \
  --judge-model gpt-4o-mini
```

---

## 3. Retrieval 평가

### 3.1 주요 지표 (v0.3.0 실행 후 채워질 것)

| 지표 | 값 | 목표 | 최소 허용 | 판정 |
|---|---|---|---|---|
| Recall@3 | — | ≥ 0.60 | 0.50 | ⏳ |
| Recall@5 | — | ≥ 0.75 | — | ⏳ |
| Recall@10 | — | — | — | ⏳ |
| MRR | — | ≥ 0.45 | 0.35 | ⏳ |
| nDCG@3 | — | ≥ 0.55 | — | ⏳ |
| Precision@3 | — | — | — | ⏳ |

### 3.2 쿼리별 상세 결과

평가 실행 시 `results/retrieval_metrics.json`의 `per_query_results` 배열에 저장된다. 각 항목은 다음 형식:

```json
{
  "query_id": "Q001",
  "retrieved_ids": [12, 47, 31, 89, ...],
  "relevant_ids": [12, 47, 89],
  "recall_at_3": 0.67,
  "mrr": 1.00,
  "ndcg_at_3": 0.85,
  "query_time_sec": 0.42
}
```

### 3.3 예상 분석 포인트

**쿼리 유형별 성능 차이**: 지원동기·성장·문제해결 등 `question_type`별로 Recall이 다를 수 있다. 특정 유형이 낮으면 해당 유형 샘플을 추가 수집하거나 쿼리 구성 방식을 조정한다.

**실패 케이스 패턴 분석**: Recall@3 = 0인 쿼리들에서 공통점을 찾아 개선 방향을 도출한다. 흔한 원인은 다음과 같다:
- 직무 유사성 낮음 (예: 개발자 → 데이터 분석 직무)
- 이력 키워드 부족 (사용자 프로필이 너무 짧음)
- 임베딩 모델의 도메인 적합성 한계

**쿼리 시간 분포**: 평균 지연이 1초를 초과하면 CPU 임베딩 병목이 원인. GPU 전환 또는 모델 교체 검토.

---

## 4. Generation 평가

### 4.1 주요 지표 (v0.3.0 실행 후 채워질 것)

| 지표 | 값 | 목표 | 최소 허용 | 판정 |
|---|---|---|---|---|
| 품질 통과율 (`score_local_draft`) | — | ≥ 75% | 60% | ⏳ |
| 재생성 횟수 평균 | — | ≤ 1.3 | 2.0 | ⏳ |
| 과장 표현 포함률 | — | ≤ 5% | 10% | ⏳ |
| 글자수 달성률 (±15%) | — | ≥ 90% | 80% | ⏳ |
| LLM-as-Judge 평균 점수 | — | ≥ 3.5/5 | 3.0/5 | ⏳ |
| 평균 파이프라인 실행 시간 | — | ≤ 60초 | 90초 | ⏳ |

### 4.2 LLM-as-Judge 5가지 기준별 점수

평가자 LLM은 각 자소서를 다음 5개 기준으로 1~5점 평가한다:

| 기준 | 평균 점수 | 최저 | 최고 |
|---|---|---|---|
| 문항 적합성 | — | — | — |
| 직무 적합성 | — | — | — |
| 이력 반영도 | — | — | — |
| 서술 완성도 | — | — | — |
| 문체 품질 | — | — | — |

### 4.3 예상 분석 포인트

**품질 통과율이 낮은 경우**: 프롬프트의 지시가 불명확하거나, `score_local_draft`의 임계값이 현실과 괴리됨을 시사한다. 임계값 재조정 또는 프롬프트 보강 검토.

**과장 표현 검출이 빈번**: 9종 금지 표현에 대응하는 의미 기반 필터 추가 고려. 단순 문자열 매칭의 한계를 보완한다.

**글자수 달성률 낮음**: Fit 단계의 효과 부족. 글자수 조정 프롬프트를 더 강하게 작성하거나, 초안 생성 단계에서 목표 길이를 더 엄격히 반영하도록 프롬프트를 개선한다.

**LLM-as-Judge 편향 주의**: GPT-4o-mini로 평가하면 같은 계열 모델(GPT-4o-mini)이 생성한 결과를 편애하는 경향이 있을 수 있다. 평가자와 생성자를 다르게 구성(예: EXAONE 생성 → GPT-4o 평가)하여 공정성 확보.

---

## 5. 베이스라인 비교 (v0.3.0 예정)

### 5.1 BM25 vs FAISS (Retrieval)

| 지표 | BM25 | FAISS + Qwen3 | 개선 폭 |
|---|---|---|---|
| Recall@3 | — | — | — |
| MRR | — | — | — |
| 지연 시간 | — | — | — |

### 5.2 RAG vs LLM 단독 (Generation)

| 지표 | LLM 단독 | RAG 적용 | 개선 폭 |
|---|---|---|---|
| LLM-as-Judge 평균 | — | — | — |
| 품질 통과율 | — | — | — |
| 구체성 (정성 평가) | — | — | — |

### 5.3 모델 간 비교

| 조합 | 품질 통과율 | Judge 평균 | 지연 | 월간 비용 |
|---|---|---|---|---|
| EXAONE → GPT-4o-mini | — | — | — | — |
| EXAONE → GPT-OSS-120B (Groq) | — | — | — | — |
| GPT-4o-mini 단독 (RAG 제외) | — | — | — | — |

---

## 6. 실패 케이스 분석

### 6.1 파이프라인 실행 실패

| 원인 | 건수 |
|---|---|
| LLM API 타임아웃 | — |
| 프롬프트 컨텍스트 초과 | — |
| JSON 파싱 실패 (Parse 단계) | — |
| 기타 | — |

### 6.2 품질 검증 실패 유형

| 실패 사유 | 건수 |
|---|---|
| 초안 길이가 너무 짧음 | — |
| 문장 반복이 많음 | — |
| 글자 수가 목표 대비 짧음 | — |
| 지원동기인데 회사명 없음 | — |
| 과장 표현 포함 | — |

---

## 7. 개선 권고

### 7.1 즉시 적용 가능 (v0.2.1 ~ v0.3.0 초)

평가 결과를 수령한 뒤 즉시 적용할 수 있는 개선 방향을 여기에 기록한다. 예시:

- 프롬프트 금지 표현 추가
- `score_local_draft` 임계값 재조정
- 쿼리 구성 방식 변경 (예: 섹션 헤더 추가/제거)

### 7.2 중기 개선 (v0.3.0 ~ v0.4.0)

- 임베딩 모델 교체 실험 (BGE-M3, KoSimCSE)
- Reranker 도입 (cross-encoder 기반)
- Peer-First 필터링 활성화 (`retriever.py`의 grade 조건)

### 7.3 장기 개선 (v0.4.0 ~ v0.5.0)

- EXAONE 도메인 적응 파인튜닝 (LoRA)
- Multi-Vector 임베딩 (자소서 섹션별 분리)
- 사용자 피드백 루프 (생성 결과에 대한 평점 수집 후 재학습)

---

## 8. 관측 및 트래킹

### 8.1 LangSmith 연동

`retriever.py`에 주석 처리된 `@traceable` 데코레이터를 v0.3.0에서 활성화하면, LangSmith 대시보드에서 다음을 확인할 수 있다:

- 쿼리별 소요 시간
- 검색된 문서 ID 및 스코어
- LLM 호출 토큰 사용량

### 8.2 회귀 모니터링

프롬프트 또는 모델 변경 시, 본 리포트의 지표를 기준값으로 회귀 테스트를 실행한다. 주요 지표가 5% 이상 하락하면 해당 변경을 되돌리거나 상세 조사한다.

---

## 9. 개정 이력

| 버전 | 날짜 | 주요 변경 |
|---|---|---|
| 0.1 | 2026-04-22 | v0.2.0 템플릿 작성 |
| 0.2 (예정) | v0.3.0 | 1차 평가 결과 기입 |
| 0.3 (예정) | v0.3.0 말 | 개선 반영 후 재평가 결과 |
| 1.0 (예정) | v0.5.0 | 배포 전 최종 평가 |

---

## 10. 관련 문서 및 산출물

| 종류 | 경로 |
|---|---|
| 평가 계획 | `docs/wiki/model/test.md` |
| 테스트 계획서 | `docs/wiki/test/test_plan.md` |
| 골든 셋 | `evaluation/datasets/golden_qa.jsonl` |
| Retrieval 스크립트 | `evaluation/run_retrieval_eval.py` |
| Generation 스크립트 | `evaluation/run_generation_eval.py` |
| Retrieval 결과 (JSON) | `evaluation/results/retrieval_metrics.json` |
| Generation 결과 (JSON) | `evaluation/results/generation_metrics.json` |
| RAG 파이프라인 상세 | `docs/wiki/model/rag_pipeline.md` |
| Retriever 구현 상세 | `docs/wiki/backend/rag_retriever.md` |

---

*last updated: 2026-04-22 | 조라에몽 팀*
