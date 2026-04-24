# Job-Pocket 테스트 실행 가이드

## 📋 개요

본 디렉토리는 Job-Pocket 백엔드의 **통합·API 테스트**를 포함한다. 테스트 계획서(`docs/wiki/test/test_plan.md`)의 전략에 따라 단위 테스트는 수행하지 않고, 실제 사용자 시나리오 중심의 통합 테스트로 구성된다.

---

## 🗂️ 디렉토리 구조

```
backend/tests/
├── conftest.py              # 공용 fixture 정의
├── api/                     # API 엔드포인트 테스트
│   ├── test_health.py       # /health/z
│   ├── test_auth_api.py     # /api/auth/*
│   ├── test_resume_api.py   # /api/resume/*
│   └── test_chat_api.py     # /api/chat/*
├── integration/             # 다중 모듈 시나리오
│   ├── test_e2e_pipeline.py # End-to-End 자소서 생성 흐름
│   └── test_retriever.py    # HybridRetriever 동작
└── fixtures/                # 테스트 데이터
    └── test_users.json
```

---

## 🚀 실행 방법

### 1. 선결 조건

다음 결함이 해결되어 있어야 한다:

- **D-001**: `backend/main.py`의 라우터 등록 복구 (삼중따옴표 블록 제거)
- **D-002**: `backend/database.py`의 MySQL 9 전환 (또는 테스트용 SQLite 유지)
- **D-004**: 테스트용 FAISS mini 인덱스 준비 (Retriever 테스트만 해당)

### 2. 의존성 설치

```bash
cd job-pocket
pip install -r docker/backend/requirements.txt
```

`requirements.txt`에 pytest, httpx가 이미 포함되어 있다.

### 3. 환경변수 설정

테스트 전용 `.env.test` 파일을 만들거나, 아래 환경변수를 export한다:

```bash
export PYTEST_MOCK_LLM=true
export OPENAI_API_KEY=sk-fake-for-test
export GROQ_API_KEY=fake-for-test
```

### 4. 실행

```bash
# 전체 테스트
pytest

# 특정 카테고리
pytest backend/tests/api/         # API 테스트만
pytest backend/tests/integration/ # 통합 테스트만

# 특정 마커
pytest -m api                     # @pytest.mark.api가 붙은 것만
pytest -m "not slow"              # 느린 테스트 제외
pytest -m "not retriever"         # FAISS 인덱스 없이 실행

# 특정 테스트 케이스 ID (test_cases.md 기준)
pytest -k "TC_001"
pytest -k "auth"

# 커버리지 리포트
pytest --cov=backend --cov-report=html
```

### 5. 기대 출력

정상 실행 시:

```
========================= test session starts =========================
collected 25 items

backend/tests/api/test_health.py::test_health_check PASSED [  4%]
backend/tests/api/test_auth_api.py::test_signup_success PASSED [  8%]
...
backend/tests/integration/test_e2e_pipeline.py::test_full_pipeline PASSED [100%]

========================= 25 passed in 4.32s =========================
```

---

## 🏷️ 마커 활용

pytest.ini에 정의된 커스텀 마커를 활용하여 실행 범위를 조절할 수 있다.

| 마커 | 용도 | 예시 |
|---|---|---|
| `@pytest.mark.api` | API 테스트만 실행 | `pytest -m api` |
| `@pytest.mark.integration` | 통합 테스트만 | `pytest -m integration` |
| `@pytest.mark.slow` | 느린 테스트 제외 | `pytest -m "not slow"` |
| `@pytest.mark.retriever` | FAISS 인덱스 필요 | `pytest -m "not retriever"` |
| `@pytest.mark.mock_llm` | LLM mocked | (기본값) |
| `@pytest.mark.requires_llm` | 실제 API 호출 | CI에서 제외 |

---

## 🛠️ Fixture 개요

`conftest.py`에 정의된 주요 fixture:

| Fixture | 스코프 | 용도 |
|---|---|---|
| `client` | module | FastAPI TestClient 인스턴스 |
| `clean_db` | function | 테스트 간 DB 초기화 |
| `test_user` | function | 사전 가입된 테스트 유저 |
| `mock_llm_responses` | function | LLM 호출을 고정 응답으로 mocking |
| `sample_user_info` | session | 샘플 user_info 튜플 |
| `mock_retriever` | function | Retriever를 mock Document 반환 |

---

## 🔧 일반적인 문제

### "ModuleNotFoundError: No module named 'backend'"

`pytest.ini`에 `pythonpath = backend` 설정이 되어있는지 확인. 또는 루트에서 실행:

```bash
cd job-pocket
pytest  # 루트에서 실행해야 함
```

### "sqlite3.OperationalError: no such table"

`conftest.py`의 `clean_db` fixture가 DB 초기화를 담당한다. fixture 호출이 빠졌는지 확인.

### "ConnectionError: Max retries exceeded"

LLM mocking이 안 된 상태. `@pytest.mark.mock_llm` 마커 또는 `mock_llm_responses` fixture 사용.

### "FileNotFoundError: faiss_index_high"

Retriever 테스트는 FAISS 인덱스가 필요. 다음 중 하나:
- `pytest -m "not retriever"` 로 제외
- `scripts/embed/build_faiss_index.py` 실행하여 인덱스 생성
- 테스트용 mini 인덱스를 `backend/tests/fixtures/`에 배치

---

## 📊 CI 통합

GitHub Actions (`.github/workflows/ci.yml`)에서 자동 실행된다. PR 생성 시:

1. MySQL 9 서비스 컨테이너 기동
2. Python 3.12 설정
3. 의존성 설치
4. `pytest -m "not requires_llm and not retriever"` 실행
5. 커버리지 리포트 업로드

---

## 📖 관련 문서

- `docs/wiki/test/test_plan.md` — 테스트 전략
- `docs/wiki/test/test_cases.md` — 32개 케이스 명세
- `docs/wiki/test/test_report_final.md` — 결과 보고서
