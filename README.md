<div align="center">

# 👛 Job Pocket

### 조라에몽의 만능 도구들처럼, 취업 준비생에게 필요한 모든 도구를 한 주머니에

**RAG(Retrieval-Augmented Generation) 기반 AI 자소서 초안 생성 서비스**

취업준비생이 자기소개서를 작성하기 위한 정보를 입력하면, <br/>채용 공고 데이터를 기반으로 맞춤형 피드백을 제공합니다. <br/>단순한 맞춤법 교정이 아닌, 직무 적합성과 표현의 설득력까지 분석합니다.

<br/>

[🚀 빠른 시작](#-설치--실행) · [📖 사용 가이드](#-사용-가이드) · [🏗️ 아키텍처](#️-아키텍처)

</div>

---

## ✨ 주요 기능

<table style="width:100%; table-layout:fixed; border-collapse:collapse;">
  <colgroup>
    <col style="width:30%;">
    <col style="width:70%;">
  </colgroup>
  <thead>
    <tr>
      <th style="padding:8px; text-align:left;">기능</th>
      <th style="padding:8px; text-align:left;">설명</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="padding:8px;">📄 <b>자소서 초안 생성</b></td>
      <td style="padding:8px;">업로드한 정보를 기반으로 섹션별로 파싱하여 구조화 후 생성</td>
    </tr>
    <tr>
      <td style="padding:8px;">🔍 <b>RAG 기반 피드백</b></td>
      <td style="padding:8px;">채용 공고 DB에서 관련 내용을 검색하여 맞춤 피드백 생성</td>
    </tr>
    <tr>
      <td style="padding:8px;">🤖 <b>AI 피드백 생성</b></td>
      <td style="padding:8px;">EXAONE 3.5 7.8B 모델을 통한 구체적이고 실용적인 개선안 제시</td>
    </tr>
    <tr>
      <td style="padding:8px;">💬 <b>대화형 인터페이스</b></td>
      <td style="padding:8px;">피드백 결과에 대해 AI와 분석 및 보완 가능</td>
    </tr>
    <tr>
      <td style="padding:8px;">📊 <b>대화 기록</b></td>
      <td style="padding:8px;">대화 내역 기록</td>
    </tr>
  </tbody>
</table>

---

## 👥 팀원

> **조라에몽** 팀 — SK Networks 26기 3차 프로젝트

<table align="center">
  <tr>
    <td align="center" valign="top" width="120">
      <a href="https://github.com/dhksrlghd">
        <img src="./docs/wiki/src/assets/images/profile/홍완기.png" width="80" height="80" style="border-radius:50%; object-fit:cover;" /><br/>
        <sub><b>홍완기</b></sub><br/>
        <sub>@dhksrlghd</sub>
      </a>
    </td>
    <td align="center" valign="top" width="120">
      <a href="https://github.com/sooa02">
        <img src="./docs/wiki/src/assets/images/profile/최수아.png" width="80" height="80" style="border-radius:50%; object-fit:cover;" /><br/>
        <sub><b>최수아</b></sub><br/>
        <sub>@sooa02</sub>
      </a>
    </td>
    <td align="center" valign="top" width="120">
      <a href="https://github.com/rusidian">
        <img src="./docs/wiki/src/assets/images/profile/장한재.png" width="80" height="80" style="border-radius:50%; object-fit:cover;" /><br/>
        <sub><b>장한재</b></sub><br/>
        <sub>@rusidian</sub>
      </a>
    </td>
    <td align="center" valign="top" width="120">
      <a href="https://github.com/Gloveman">
        <img src="./docs/wiki/src/assets/images/profile/이창우.png" width="80" height="80" style="border-radius:50%; object-fit:cover;" /><br/>
        <sub><b>이창우</b></sub><br/>
        <sub>@Gloveman</sub>
      </a>
    </td>
    <td align="center" valign="top" width="120">
      <a href="https://github.com/nobrain711">
        <img src="./docs/wiki/src/assets/images/profile/조동휘.png" width="80" height="80" style="border-radius:50%; object-fit:cover;" /><br/>
        <sub><b>조동휘</b></sub><br/>
        <sub>@nobrain711</sub>
      </a>
    </td>
    <td align="center" valign="top" width="120">
      <a href="https://github.com/JJonyeok2">
        <img src="./docs/wiki/src/assets/images/profile/전종혁.png" width="80" height="80" style="border-radius:50%; object-fit:cover;" /><br/>
        <sub><b>전종혁</b></sub><br/>
        <sub>@JJonyeok2</sub>
      </a>
    </td>
  </tr>
</table>

---

## 🛠️ 기술 스택

### Language & Framework

| 분류 | 기술 | 버전 | 용도 |
|---|---|---|---|
| Language | ![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) | 3.12 | 전체 백엔드 |
| Frontend | ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white) | 1.56.0 | 사용자 인터페이스 |
| Backend | ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white) | 0.115.0 | REST API 서버 |

### Database

| 분류 | 기술 | 용도 |
|---|---|---|
| RDBMS | ![MySQL](https://img.shields.io/badge/MySQL_9.3-4479A1?style=flat-square&logo=mysql&logoColor=white) | 사용자 정보, 이력서 메타데이터 저장 |
| Vector Store | MySQL (Vector type) | 임베딩 벡터 저장 및 유사도 검색 |
| Document Store | MySQL NoSQL(Json) | 채용 공고 원문 및 피드백 이력 저장 |

> MySQL 9의 Vector 및 NoSQL 기능을 활용하여 별도의 Vector DB 없이 단일 DB로 통합 관리합니다.

### AI / ML

| 분류 | 모델 | 제공처 | 용도 |
|---|---|---|---|
| LLM | **EXAONE 3.5 7.8B** | LG AI Research via RunPod | 이력서 피드백 생성 |
| Embedding | **Qwen3 Embedding 0.6B** | Alibaba Cloud via RunPod | 텍스트 임베딩 |

### Infrastructure

| 기술 | 용도 |
|---|---|
| ![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white) | 컨테이너 환경 구성 |
| ![Docker Compose](https://img.shields.io/badge/Docker_Compose-2496ED?style=flat-square&logo=docker&logoColor=white) | 멀티 컨테이너 오케스트레이션 |
| ![RunPod](https://img.shields.io/badge/RunPod-673AB7?style=flat-square&logo=RunPod&logoColor=white) | GPU 기반 LLM / Embedding 서버 호스팅 |

### Co-Tools

| 기술 | 용도 |
|---|---|
| ![JIRA](https://img.shields.io/badge/Jira-0052CC?style=flat&logo=Jira&logoColor=white) | 애자일 프로젝트 스프린트 설정 |
| ![Notion](https://img.shields.io/badge/Notion-000000?style=flat&logo=notion&logoColor=white)| 업무 및 프로젝트 관리 |
| ![Discord](https://img.shields.io/badge/Discord-5865F2?style=flat&logo=discord&logoColor=white) | 업무 메신저 |

---

## 🏗️ 아키텍처

<div align="center">
    <img src="./docs/wiki/src/assets/images/architecture/logical_layered_architecture.png" width="80%" alt="Logical Architecture">
</div>

### RAG 파이프라인

<div align="center">
    <img src="./docs/wiki/src/assets/images/model/rag_pipeline.png" width="70%" alt="Logical Architecture">
</div>

### 데이터베이스 설계 (ERD)

<div align="center">
  <img src="./docs/wiki/src/assets/images/backend/jobpocket_erd.png" width="90%" alt="Database ERD">
</div>

---

## 프로젝트 구조 📁

```
job-pocket/
├── .github/                # GitHub Issue/PR 템플릿 및 CI/CD 워크플로우
├── backend/                # FastAPI 백엔드
│   ├── common/             # 공통 설정 및 유틸리티 (DB 연결, API 요청 등)
│   ├── middlewares/        # FastAPI 미들웨어 (CORS 설정 등)
│   ├── repository/         # DB 접근 계층 (Base, Chat, User, Retrieval)
│   ├── routers/            # API 엔드포인트 라우팅 (Auth, Chat, Resume 등)
│   ├── schemas/            # Pydantic 데이터 검증 및 변환 스키마
│   ├── services/           # 핵심 비즈니스 로직 (RAG, Resume 서비스 등)
│   │   └── chat/           # LLM 분석/평가/생성 엔진 (Analyzer, Generator 등)
│   ├── tests/              # 테스트 코드 (API, Integration, Evaluation 등)
│   ├── utils/              # 백엔드 유틸리티 (FAISS/BM25 인덱스, 보안 등)
│   └── main.py             # FastAPI 애플리케이션 진입점
├── database/               # 데이터베이스 관련 설정 및 데이터 적재
│   ├── ingestion/          # 데이터 수집, 가공 및 적재 파이프라인
│   ├── init/               # DB 초기화 SQL 스크립트 (RDB, Vector Table 등)
│   └── my.cnf              # MySQL 설정 파일
├── docker/                 # 서비스별 Docker 구성 파일
│   ├── backend/            # 백엔드 Dockerfile 및 패키지 목록
│   ├── database/           # 데이터베이스 Dockerfile
│   └── frontend/           # 프론트엔드 Dockerfile 및 패키지 목록
├── docs/                   # 프로젝트 문서 및 위키
│   └── wiki/               # 아키텍처, 컨벤션 등 상세 가이드
├── frontend/               # Streamlit 프론트엔드
│   ├── .streamlit/         # Streamlit 환경 설정
│   ├── public/             # 로고 등 정적 리소스
│   ├── utils/              # UI 컴포넌트 및 API 클라이언트
│   ├── views/              # 기능별 화면 UI (Auth, Chat, Resume)
│   └── app.py              # Streamlit 메인 실행 파일
├── models/                 # Runpod Serverless에 배포한 LLM 서빙 및 모델 관련 코드
│   ├── common/             # RunPod 연동 및 공통 유틸리티
│   ├── schemas/            # 모델 입출력 데이터 스키마
│   └── exaone.py           # EXAONE 3.5 모델 인터페이스
├── .env.example            # 환경변수 설정 예시
├── docker-compose.dev.yaml # 개발용 Docker Compose 설정
├── docker-compose.yaml     # 운영용 Docker Compose 설정
├── LICENSE                 # 프로젝트 라이선스 (MIT)
└── README.md               # 프로젝트 메인 설명서
```

---

## 🖥️ 서비스 화면

<div align="center">
  <h3>1. 스펙 입력 화면</h3>
  <img src="./docs/wiki/src/assets/images/frontend/screenshot_resume.png" alt="Resume">
  <p><i>사용자의 기본 정보와 기술 스택, 프로젝트 경험을 입력하는 화면입니다.</i></p>
  
  <br/>

  <h3>2. AI 피드백 및 분석 결과</h3>
  <img src="./docs/wiki/src/assets/images/frontend/screenshot_draft.png" alt="Draft">
  <img src="./docs/wiki/src/assets/images/frontend/screenshot_evaluation.png" alt="Result Screen">
  <p><i>생성된 초안과 함께 평가 결과 및 보완 포인트를 답변합니다.</i></p>

  <br/>

  <h3>3. 대화형 수정 워크플로우</h3>
  <img src="./docs/wiki/src/assets/images/frontend/screenshot_revise.png" alt="Chat Screen">
  <p><i>추가 대화를 통해 특정 문항을 수정하거나 내용을 보완합니다.</i></p>
</div>

---

## 🚀 설치 & 실행

### 사전 요구사항

- **Docker & Docker Compose**: 컨테이너 환경 실행을 위해 필수입니다.
- **Git**: 레포지토리 클론 및 소스 관리를 위해 필요합니다.
- **RunPod API Key & Endpoint**: GPU 기반 LLM/Embedding 서버리스 API 접근을 위해 필요합니다.
- **HuggingFace Token (HF_TOKEN)**: 모델 가중치 및 라이브러리 접근을 위해 필요합니다.
- **LangSmith API Key** (선택): AI 파이프라인 모니터링 및 트레이싱을 원할 경우 필요합니다.
- **사전 구축된 인덱스 데이터**: FAISS 및 BM25 검색을 위한 인덱스 파일이 준비되어 있어야 합니다. ([직접 생성 방법](./docs/wiki/src/backend/faiss_index_build.md) 또는 `INDEX_URL` 참고)

### 방법: Clone하여 실행을 권장

```bash
# 1. 레포지토리 클론
git clone https://github.com/Joraemon-s-Secret-Gadgets/job-pocket.git
cd job-pocket

# 2. 환경 변수 설정
cp .env.example .env
# .env 파일을 열어 필요한 값을 입력 (아래 환경 변수 섹션 참고)

# 3. Docker Compose로 전체 서비스 실행
docker compose up -d

# 4. 서비스 접속
# Streamlit UI: http://localhost:8501
# FastAPI Docs: http://localhost:8000/docs
```

### 환경 변수 설정 (`.env`)

```env
# Frontend & API
API_BASE_URL=http://localhost:8000

# LLM / External APIs 
OPENAI_API_KEY=your_openai_api_key
GROQ_API_KEY=your_groq_api_key
HF_TOKEN=your_huggingface_token

# RunPod (LLM & Embedding)
RUNPOD_API_KEY=your_runpod_api_key
RUNPOD_ENDPOINT=your_runpod_endpoint_id

# LangSmith (Tracing & Monitoring)
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=Job-pocket

# Database - RDB (MySQL)
# rdb_user, rdb_password 등을 실제 사용할 값으로 변경하세요.
RDB_URL=mysql+pymysql://rdb_user:rdb_password@localhost:3306/job_pocket_rdb
MYSQL_RDB_USER=rdb_user
MYSQL_RDB_PASSWORD=rdb_password

# Database - Vector (MySQL Vector Store)
VECTOR_DB_URL=mysql+pymysql://vector_user:vector_password@localhost:3306/job_pocket_vector
MYSQL_VECTOR_USER=vector_user
MYSQL_VECTOR_PASSWORD=vector_password

# MySQL Container
MYSQL_ROOT_PASSWORD=your_root_password
TIMEZONE=Asia/Seoul

# External Resource (FAISS/BM25 Index 등)
INDEX_URL=your_google_drive_index_folder_url
```

### 서비스 상태 확인

```bash
# 전체 컨테이너 상태 확인
docker compose ps

# 로그 확인
docker compose logs -f

# 특정 서비스 로그만 확인
docker compose logs -f backend
docker compose logs -f frontend
```

### 서비스 종료

```bash
# 컨테이너 + 볼륨 삭제 (DB 데이터 포함)
docker compose down -v
```

---

## 📖 사용 가이드

### 1. 회원가입 / 로그인

서비스 접속 후(`http://localhost:8501`) 우측 상단 **[회원가입]** 버튼을 클릭하여 계정을 생성합니다.

### 2. 이력서 업로드

1. 좌측 사이드바에서 **[내 스펙 보관함]** 메뉴 선택
2. 내 정보와 기술 스택, 프로젝트 경험 등 입력
3. 지원하고자 하는 **직무/포지션/문항 정보** 입력 (예: "프론트/백엔드 개발자", "AI 관련 직무")
4. **[채팅 시작]** 버튼 클릭

### 3. AI 피드백 확인

분석이 완료되면 다음 항목별 피드백을 확인할 수 있습니다:

| 항목 | 내용 |
|---|---|
| **직무 적합도** | 입력한 포지션과 이력서 내용의 매칭 점수 및 분석 |
| **경험 기술 방식** | 성과 중심 표현, 수치화, 구체성 개선 제안 |
| **핵심 키워드** | 채용 공고 기반 누락 키워드 및 추가 권장 사항 |
| **항목별 피드백** | 자기소개, 경력, 프로젝트 섹션별 세부 의견 |

### 4. 대화형 심층 분석

피드백 화면 하단의 채팅 입력창을 통해 AI와 추가 대화가 가능합니다.

```
예시 질문:
- "3번 프로젝트 경험을 더 임팩트 있게 표현하려면 어떻게 해야 할까요?"
- "Java 백엔드 포지션에 맞게 기술 스택 섹션을 수정해줄 수 있어요?"
- "현재 이력서의 가장 큰 약점이 뭔가요?"
```

---

## 한계

### 1. 사용자 정보가 부족할 때 결과 일반화 가능성 존재

현재 구조는 문항 유형을 파싱하고 그에 맞게 초안을 생성하도록 되어 있지만, 사용자가 입력하는 정보가 짧거나 스펙 보관함 정보가 충분하지 않으면 결과가 추상적인 문장이나 범용적인 표현으로 흐를 가능성이 있다. 특히 자소서 생성 모델은 빈 정보를 그럴듯한 문장으로 메우려는 경향이 있어서, 이를 프롬프트 제약으로 줄이고 있지만 완전히 해결되지는 않는다.

### 2. 초기 초안 품질이 로컬 모델 성능에 영향력

초기 초안 생성은 비용 절감을 위해 LG EXAONE 3.5 7.8B 기반 로컬 모델로 처리하도록 설계했다. 이 방식은 장문 초안을 API로 계속 생성하는 것보다 비용 측면에서 유리하지만, 반대로 말하면 첫 초안의 품질은 로컬 모델의 한계에 직접 영향을 받는다. 따라서 표현의 자연스러움이나 문항 적합도 면에서는 후처리 단계에 의존하는 비중이 크다.

### 3. 수정 흐름은 자연스럽지만, 수정 범위 판단은 아직 단순

현재는 사용자의 후속 입력이 수정 요청인지 키워드 기반으로 판별하고, 직전 결과를 기준으로 수정안을 생성하는 방식이다. 사용자가 실제로는 새 문항을 입력했는데도 수정 요청으로 해석되거나, 반대로 수정 요청인데 새 초안 생성으로 넘어갈 가능성이 있다. 즉 생성과 수정의 분리는 구현했지만, 두 흐름을 구분하는 판단 로직은 아직 정교하지 않다.

### 4. 평가 결과와 수정 흐름 연결은 구현했지만 평가 자체의 정밀도는 더 보완 필요

현재 결과는 평가 및 코멘트, 보완 포인트, 그리고 보완 포인트를 바로 수정 요청으로 연결하는 흐름까지 갖추고 있다. 다만 평가 자체는 여전히 모델이 만든 텍스트에 의존하는 부분이 있어, 실제 문항 적합성·사실성·문체 안정성 같은 항목을 더 세밀하게 규칙화할 필요가 있다.

---

## 확장 방향

### 1. 사용자 정보 입력 구조 세분화할 필요성 존재

현재는 경험, 수상, 기술 스택 정도를 큰 텍스트 단위로 받는 구조인데, 이를 프로젝트명, 역할, 문제 상황, 해결 방식, 결과처럼 더 잘게 구조화하면 생성 품질이 올라갈 수 있다. 이렇게 되면 모델이 없는 경험을 추론하기보다, 이미 구조화된 정보를 더 정확하게 조합할 수 있다.

### 2. 평가를 규칙 기반 점검과 결합 가능

지금은 평가와 보완 포인트도 모델 중심으로 생성되지만, 향후에는 문항 적합성, 글자 수 충족 여부, 과장 표현 여부, 사실성 위반 가능성 등을 규칙 기반으로 함께 점검할 수 있다. 그러면 단순한 자연어 평가보다 더 신뢰도 높은 피드백 구조로 확장할 수 있다.

### 3. 비용 최적화 구조를 더 발전 가능성 존재

지금도 초기 장문 생성은 로컬 모델, 수정과 정제는 API 모델로 나누어 비용을 줄이는 구조를 적용했다. 앞으로는 문항 유형이나 입력 길이에 따라 어떤 단계까지 로컬에서 처리하고, 어느 시점에만 API를 호출할지 더 세밀하게 분기하면 비용 효율을 더 높일 수 있다. 즉 단순한 모델 분리가 아니라, 요청 특성에 따라 동적으로 생성 비용을 제어하는 방향으로 확장할 수 있다.

### 4. 결과 화면을 출력이 아니라 작성 워크플로우로 확장 필요

현재, 생성 → 평가 → 보완 포인트 → 수정안 생성 흐름은 구현되어 있다. 이후에는 수정 이력 비교, 버전별 저장, 특정 문단만 선택 수정, 문체 옵션 선택 같은 기능을 붙이면 단순 생성 서비스가 아니라 실제 작성 도구에 가까운 구조로 확장할 수 있다.

---

## 🔍 사전 조사 레포지토리

본 프로젝트를 위해 팀원들이 각자 진행한 사전 기술 조사 및 프로토타입 레포지토리입니다.

- **[chainlit_playground](https://github.com/Joraemon-s-Secret-Gadgets/chainlit_playground)** (`전종혁`) - streamlit 기반 UI/UX 디자인과 FastAPI 연동
- **[mysqy-faiss-retriever-playground](https://github.com/Joraemon-s-Secret-Gadgets/mysql-faiss-retriever-playground)** (`이창우`) - ETL 파이프라인 구축, MySQL과 FAISS를 통한 벡터 검색 retriever 구현
- **[mysql9_playground](https://github.com/Joraemon-s-Secret-Gadgets/mysql9_playground)** (`조동휘`) - mysql9.3 기반 벡터 연산 최적화 db 설정 및 docker 환경
- **[resume-draft-playground](https://github.com/Joraemon-s-Secret-Gadgets/resume-draft-playground)** (`장한재`) - 사용자의 이력 정보와 유사한 배경을 가진 지원자들의 자소서 예시를 참고해, LLM이 자기소개서 초안을 생성하는 방식 실험
- **[llm-length-control-playground](https://github.com/Joraemon-s-Secret-Gadgets/llm-length-control-playground)** (`홍완기`) - 성된 자기소개서를 원하는 글자 수에 맞게 정밀하게 재조정하고, 사용자 피드백 기반으로 대화형 수정
- **[SSH_playground](https://github.com/Joraemon-s-Secret-Gadgets/SSH_placyground)** (`조동휘`) - - Runpod 연동 대비 SSH 터널링 및 jumpserver구현

---

## 📌 버전 히스토리

| 버전 | 설명 | 상태 |
|---|---|---|
| `v0.1.0` | Docker Compose 기반 전체 서비스 스택 구축 | ✅ 완료 |
| `v0.2.0` | BE · FE · LLM 통합 | ✅ 완료 |
| `v0.3.0` | 버그 수정 및 안정화 | ✅ 완료 |
| `v0.4.0` | 코드 리팩토링 및 성능 개선 | ✅ 완료 |
| `v0.5.0` | 배포 및 발표 준비 | ✅ 완료 |

---

## 🔗 관련 문서

- [전체 아키텍처 및 데이터 흐름](./docs/wiki/src/architecture/overview.md)
- [백엔드 아키텍처 상세](./docs/wiki/src/backend/architecture.md)
- [DB 설계 (ERD)](./docs/wiki/src/backend/database.md)
- [데이터 전처리 및 인제션 상세](./docs/wiki/src/backend/data_ingestion.md)
- [RAG 파이프라인 설계](./docs/wiki/src/model/rag_pipeline.md)
- [프롬프트 엔지니어링 전략](./docs/wiki/src/model/prompt.md)
- [개발 컨벤션 가이드](./docs/wiki/src/conventions/development.md)
- [트러블슈팅 리포트](./docs/wiki/src/troubles/README.md)
- [Retriever 성능 보고서](./docs/wiki/src/tests/evaluation_report.md)

---

## 프로젝트 회고

### 개인 회고

<table style="width: 100%; border-collapse: collapse; border: 1px solid #ddd;">
    <thead>
        <tr style="background-color: #f8f9fa;">
            <th style="width: 20%; border: 1px solid #ddd; padding: 10px;">이름</th>
            <th style="border: 1px solid #ddd; padding: 10px;">회고</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">이창우</td>
            <td style="border: 1px solid #ddd; padding: 10px;">
                기존에 RAG 시스템을 구축해본 경험을 바탕으로 벡터 유사도를 사용한 리트리버를 구축하고, ‘기술 스택 매칭률’ 지표를 도입해 검색 성능을 정량적으로 검증했습니다. 원본 문서를 모두 담는 기존 vectorstore와 달리, MySQL에 원본 데이터와 임베딩 벡터를 적재해두고 이를 기반으로 빌드한 faiss 인덱스에는 해당 row id와 임베딩 벡터만을 매핑하는 경량화 전략을 차별점으로 두었습니다. Retriever 설계의 경우 처음에는 벡터 검색과 db 원본 문서 조회를 하나의 클래스로 묶었지만, 코드 리펙토링을 거치며 schema/service/repository로 분리하여 유지보수성을 높였습니다.<br />
                이후 하나로 묶여 있던 chat_logic을 위 구조로 분리하는 과정에서 두 가지의 결정적인 문제점을 찾아 해결했습니다. 첫번째는 모든 비즈니스 로직이 단일 파일에 밀집된 ‘god object’ 구조로 인해 코드 가독성이 저하되어, 오케스트레이터 패턴을 도입하여 파싱, 생성, 평가 모듈로 분리하여 해결했습니다. 프롬포트 역시 별도 파일로 관리하여 각 단계에서 사용되는 항목을 빠르게 확인할 수 있도록 했습니다. 둘째는 생성 루프 내 동일한 검색 및 서술 구조 추출 연산이 반복되어 추가적인 비용이 발생하는 문제가 있어, 이를 루프 외부로 이동시켜 불필요한 토큰 사용을 없앴습니다. 또한 기존에 사용자 요구 메시지를 파싱할때 정규표현식의 한계를 LLM을사용한 파싱으로 해결했는데, 이 과정에서 StroutputParser를 JonOutputParser로 전환하여 사용자의 다양한 입력에 대해 정확한 파싱이 가능하도록 했습니다. 이번 프로젝트는 저에게 있어 기능 구현을 넘어 프로젝트의 운영 효율성과 확장성을 고민하고 최적화된 파이프라인을 구축하는 AI 백엔드 엔지니어로서의 설계 철학을 더욱 발전시킬 수 있었던 소중한 성장의 시간이었습니다.
            </td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">장한재</td>
            <td style="border: 1px solid #ddd; padding: 10px;">
                이번 프로젝트를 하면서 단순히 결과를 생성하는 것보다, 초안 이후 수정이 자연스럽게 이어지는 흐름을 설계하는 일이 더 중요하다는 점을 배웠다.<br />
                특히 로컬 오픈소스 모델과 API 모델의 역할을 나누면서, 성능만이 아니라 비용, 응답 속도, 수정 효율까지 함께 고려해야 실제 서비스 구조가 된다는 점을 많이 느꼈다.<br />
                또 프롬프트를 잘 쓰는 것만으로 끝나는 게 아니라, 사용자의 입력이 부족할 때 어떤 한계가 생기는지, 그리고 그 한계를 어떻게 보완할지까지 같이 설계해야 한다는 점이 인상적이었다.<br />
                개인적으로는 모델 선택보다도, 생성·수정·평가를 하나의 흐름으로 연결하는 구조를 설계한 경험이 가장 의미 있었다.
            </td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">전종혁</td>
            <td style="border: 1px solid #ddd; padding: 10px;">
                JobPocket 프로젝트 초기에 Chainlit을 활용한 신속한 UI 구축을 시도했으나, 커스텀 로그인 페이지 구현과 인터페이스 확장성의 한계를 느껴 Streamlit으로의 전면 이관 및 고도화를 결정했습니다.<br />
                단순한 데이터 대시보드 형태를 넘어선 모던한 웹 서비스를 위해 Figma를 활용한 서비스 아키텍처 설계를 선행했으며, 이를 실제 서비스에 녹여내기 위해 커스텀 CSS를 적극적으로 도입하여 심미성과 사용성을 동시에 확보했습니다.<br />
                특히, FastAPI 백엔드와의 효율적인 통신을 위해 API 엔드포인트를 설정하고 api_client를 모듈화함으로써 아키텍처의 견고한 기반을 다졌습니다.<br />
                무엇보다 Streamlit의 세션 상태를 정교하게 설계하여, 복잡한 단계별 자소서 생성 과정에서도 데이터 유실 없이 매끄러운 사용자 경험(UX)을 구현해낸 것이 이번 프로젝트의 가장 큰 기술적 성과라고 생각합니다.
            </td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">조동휘</td>
            <td style="border: 1px solid #ddd; padding: 10px;">
                이번 프로젝트는 대학 졸업 프로젝트 이후 처음으로
                업데이트를 실시간으로 추적하며 진행한 프로젝트였다.<br />
                RunPod 환경에서 예상치 못한 문제들이 연속으로 터졌을 때는
                솔직히 팀에 발목을 잡는 건 아닐까 불안했다.<br />
                그래도 끝내 환경을 잡아냈을 때, 팀이 원하는 기능을
                막힘 없이 올려줄 수 있었을 때는 오랜만에 느껴보는
                짜릿함이었다.<br />
                LLM과 RAG를 연결하면서 할루시네이션을 어떻게
                줄일 수 있을까 고민했던 시간도 인상 깊었다.<br />
                정답을 찾았다기보다, 서비스 설계 측면에서
                어떤 구조가 사용자에게 더 올바른 응답을 줄 수 있는지
                스스로 고민하고 방향을 잡아본 경험이
                나에게 큰 성장이었다.
            </td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">최수아</td>
            <td style="border: 1px solid #ddd; padding: 10px;">
            이번 프로젝트에서 PL을 맡아 일정 조율, Git 브랜치 전략 수립과 협업 환경 세팅을 담당했다. 처음 맡은 PL 역할에서 개발과 소통을 동시에 챙기는 어려움을 체감했고, 우선순위와 변경 시나리오까지 고려한 초기 설계의 중요성을 직접 느꼈다.<br />
            기술 명세서를 기반으로 MECE 분류 → WBS → Jira 에픽/스토리/하위작업 3단계 구조를 설계했다.<br />
            모든 작업을 PR·커밋 단위로 추적 가능하게 만들었고, Gitflow 브랜치 전략과 연결해 개발 흐름을 통일한 것이 주요 성과였다.<br />
            Git 측면에서는 Gitflow를 도메인 단위(infra/be/fe)로 재설계하고, Jira 연동 커밋 컨벤션·PR 템플릿까지 협업 기반을 직접 구축했다.<br />
            에픽 단위와 도메인 단위 브랜치의 장단점을 비교하며 팀 상황에 맞는 방식을 선택하는 과정에서 Git에 대한 이해가 깊어졌다.<br />
            다음 프로젝트에서는 PM을 맡는 만큼 초반 환경 세팅을 빠르게 마치고 프로젝트 진행과 협업이 더 원활하게 이루어질 수 있도록 노력하고 싶다. 
            </td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">홍완기</td>
            <td style="border: 1px solid #ddd; padding: 10px;">
            이번 프로젝트에서는 핵심 기능을 직접 구현하기보다, 팀이 만든 시스템이 외부에서 이해되고 내부적으로 검증될 수 있도록 만드는 일을 맡았습니다.<br />
            아키텍처·백엔드·모델 등 전 도메인의 위키 문서를 작성하며 흩어져 있던 설계 의도를 한곳에 정리했고, 테스트와 품질 평가 인프라를 구축하면서 "LLM 서비스의 품질을 어떻게 객관적으로 측정할 것인가"라는 질문에 답을 만들어가는 경험이 가장 의미 있었습니다.
            </td>
        </tr>
    </tbody>
</table>

---

### 팀원 회고

<table style="width: 100%; border-collapse: collapse; border: 1px solid #ddd; margin-bottom: 30px;">
    <thead>
        <tr style="background-color: #f8f9fa;">
            <th style="width: 15%; border: 1px solid #ddd; padding: 10px;">대상자</th>
            <th style="width: 15%; border: 1px solid #ddd; padding: 10px;">작성자</th>
            <th style="border: 1px solid #ddd; padding: 10px;">회고 내용</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td rowspan="5" style="text-align: center; font-weight: bold; border: 1px solid #ddd;">이창우</td>
            <td style="text-align: center; border: 1px solid #ddd;">장한재</td>
            <td style="border: 1px solid #ddd; padding: 10px;">
                RAG 구축과 데이터 수집·전처리를 맡아 프로젝트의 기반을 안정적으로 만들어 주셨다.<br />
                특히 결과 품질이 결국 데이터 구조와 전처리 수준에 크게 좌우된다는 점에서, 초기에 필요한 데이터를 정리하고 활용 가능한 형태로 다듬어 준 역할이 매우 중요했다고 생각한다.<br />
                프로젝트가 실제로 동작할 수 있는 바탕을 탄탄하게 잡아 주셨다는 점이 인상적이었다.
             </td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">전종혁</td>
            <td style="border: 1px solid #ddd; padding: 10px;">
            MySQL 기반의 벡터 DB 통합을 주도하며 서비스의 데이터 기반을 다졌습니다.<br />
            비정형 데이터인 이력서 스펙을 효율적으로 추출하고 전처리하는 파이프라인을 설계했으며,<br />
            특히 백엔드 로직의 세부 모듈화를 통해 코드의 가독성과 유지보수성을 극대화했습니다.<br />
            덕분에 대규모 데이터 처리 상황에서도 안정적인 응답 속도를 유지할 수 있는 견고한 시스템을 완성했습니다.
            </td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">조동휘</td>
            <td style="border: 1px solid #ddd; padding: 10px;">
            프로젝트 초반부터 데이터셋과 RAG 설계에 적극적으로 임하며
            할루시네이션을 줄이기 위한 방법을 스스로 탐구하고
            지속적으로 성능을 개선해 나갔다.<br />
            프로젝트 마무리 단계에서 테스트 과정에서 평가에 영향을 줄 수 있는
            큰 버그가 발생했음에도 포기하기보다는 수정을 통해 해결하여
            프로젝트를 정상적으로 마무리하는 데 핵심적인 역할을 해주어서 프로젝트를 마무리하는 현재 가장 고마운 존재로 생각이 난다.
            </td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">최수아</td>
            <td style="border: 1px solid #ddd; padding: 10px;"></td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">홍완기</td>
            <td style="border: 1px solid #ddd; padding: 10px;">
            이번 프로젝트에서는 핵심 기능을 직접 구현하기보다, 팀이 만든 시스템이 외부에서 이해되고 내부적으로 검증될 수 있도록 만드는 일을 맡았습니다.<br />
            아키텍처·백엔드·모델 등 전 도메인의 위키 문서를 작성하며 흩어져 있던 설계 의도를 한곳에 정리했고, 테스트와 품질 평가 인프라를 구축하면서 "LLM 서비스의 품질을 어떻게 객관적으로 측정할 것인가"라는 질문에 답을 만들어가는 경험이 가장 의미 있었습니다.</td>
        </tr>
    </tbody>
</table>
<table style="width: 100%; border-collapse: collapse; border: 1px solid #ddd; margin-bottom: 30px;">
    <thead>
        <tr style="background-color: #f8f9fa;">
            <th style="width: 15%; border: 1px solid #ddd; padding: 10px;">대상자</th>
            <th style="width: 15%; border: 1px solid #ddd; padding: 10px;">작성자</th>
            <th style="border: 1px solid #ddd; padding: 10px;">회고 내용</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td rowspan="5" style="text-align: center; font-weight: bold; border: 1px solid #ddd;">장한재</td>
            <td style="text-align: center; border: 1px solid #ddd;">이창우</td>
            <td style="border: 1px solid #ddd; padding: 10px;">
            자소서 생성 로직의 전 과정을 설계하고 구현하며 기술적으로 까다로운 과제들을 주도적으로 해결해 주셨습니다. 단순한 모델 호출을 넘어 사용자 요청 파싱부터 검색 컨텍스트 결합, 최종 품질 평가에 이르기까지 정교한 다단계 파이프라인을 설계하여 복잡한 생성 로직을 실제 백엔드 서비스로 옮기는 과정이 매우 수월하고 효율적으로 진행될 수 했습니다. 저 역시 생성 과정을 믿고 맡기고 검색 과정에 더욱 집중할 수 있었습니다. 특히 제한된 자원 안에서 성능을 극대화하기 위해 로컬 모델과 외부 api를 병행 사용하여 토큰 사용을 절약하고, 수많은 실험을 통해 한국어 자기소개서에 가장 적합한 최적의 모델 조합을 찾아 주셔서 프로젝트의 질적 완성도를 높이는데 결정적인 역할을 수행하셨습니다.
            </td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">전종혁</td>
            <td style="border: 1px solid #ddd; padding: 10px;">
            '10년 차 대기업 인사담당자'라는 정교한 AI 페르소나를 설정하고, 
            고품질의 자기소개서를 생성하기 위한 프롬프트 알고리즘을 구축했습니다.<br />
            단순히 정보를 출력하는 것 뿐 아니라, 사용자의 경험을 심층적으로 끌어내는 '티키타카 역질문 로직'을 안착시켜 서비스의 대화 품질을 비약적으로 상승시켰으며, RAG 기반 답변의 신뢰도를 확보하는 데 핵심적인 공을 세웠습니다.<br />
            특히 사용자가 AI의 작업 단계를 신뢰할 수 있도록 'AI 모델 실행 과정 시각화(Progress Step)' 아이디어를 제안하고 구현하여 서비스의 투명성과 사용자 경험을 한 차원 높였습니다. 
            </td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">조동휘</td>
            <td style="border: 1px solid #ddd; padding: 10px;">
            요번에 model을 혼자서 담당을 해주셨는데도 힘들다고 말하기보다는 열심히 보겠다는 말을 꺼내주어서 개인적으로는 프로젝트 초반기에 가장 큰 도움이 되어주셨다.<br />
            LLM Model을 job pocket프로젝트에 맞게 끔 hugging face에서 모델을 찾아서 도입을 해주셔서 프로젝트가 올바른 방향으로 나아가게끔 만들어 준 결과는 개인적으로 본 받아서 활용해야 겠다고 생각이 날 정도록 프로젝트에 열정이 넘치셔서 그 만큼 이 프로젝트가 원하는 목표에 도달했다고 생각이 듭니다.
            </td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">최수아</td>
            <td style="border: 1px solid #ddd; padding: 10px;"></td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">홍완기</td>
            <td style="border: 1px solid #ddd; padding: 10px;">
            자소서 초안 생성이라는, 까다롭고 어려운 부분을 맡아 끝까지 완성해 주었습니다. "이게 퀄리티가 잘 나올까?" 싶은 의구심이 있었는데, 수많은 프롬프트 실험과 로컬 모델·API 활용을 통해 실제 서비스에 적용해도 될 만큼의 결과물을 만들어냈습니다. 막히는 순간에도 끝까지 해내는 모습이 인상 깊었고, 우리 서비스의 핵심 기능 하나를 완성해 준 점이 정말 고마웠습니다.</td>
        </tr>
    </tbody>
</table>
<table style="width: 100%; border-collapse: collapse; border: 1px solid #ddd; margin-bottom: 30px;">
    <thead>
        <tr style="background-color: #f8f9fa;">
            <th style="width: 15%; border: 1px solid #ddd; padding: 10px;">대상자</th>
            <th style="width: 15%; border: 1px solid #ddd; padding: 10px;">작성자</th>
            <th style="border: 1px solid #ddd; padding: 10px;">회고 내용</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td rowspan="5" style="text-align: center; font-weight: bold; border: 1px solid #ddd;">전종혁</td>
            <td style="text-align: center; border: 1px solid #ddd;">이창우</td>
            <td style="border: 1px solid #ddd; padding: 10px;">
            프론트(streamlit) 파트를 홀로 맡아 단순한 UI 구성을 넘어 백엔드와 유기적으로 소통하는 ‘시스템 통합’에 기여했습니다. 별도로 api 클라이언트 계층을 구축하여 시스템의 확장성과 유지보수성을 동시에 확보하고, 서비스에 필요한 session state 적절히 설계해 리펙토링 작업에서도 백엔드 스키마 변경에 따른 적용 외에 수정할 부분이 거의 없었습니다. 대화 히스토리와 이용자 정보 관리 역시 sqlite를 적용한 저장/불러오기 로직을 구현해 두어, mysql로 옮길 때 훨씬 수월했던 것 같습니다.
            </td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">장한재</td>
            <td style="border: 1px solid #ddd; padding: 10px;">
            프런트를 맡아 사용자가 실제로 결과를 확인하고 활용하는 화면을 구현해 주셨다. 기능이 단순히 동작하는 수준을 넘어서, 사용 흐름이 자연스럽게 이어질 수 있도록 화면 구성을 정리해 준 점이 좋았다. 사용자가 서비스를 직접 경험하는 부분을 맡아 프로젝트 결과를 더 접근성있게 보여줄 수 있게 해 주셨다고 생각한다.
            </td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">조동휘</td>
            <td style="border: 1px solid #ddd; padding: 10px;">
            요번 프로젝트에서 가장 보이지 않는 곳에서 가장 열심히 본인의 역할에 충실했던 팀원으로 기억에 남는다.<br />
            본 프로젝트는 어찌 보면 LLM과 RAG 구조에 힘을 더 주어야 하는데, 개별적으로 우리 프로젝트가 현재 시장에 있는 비슷한 서비스와 어떠한 차별점을 가지고 있는가를 발굴해서 팀이 어떠한 방향으로 나아가야 시장에 나와도 경쟁력을 가지는지를 제시해주었다.<br />
            또한 Streamlit과 FastAPI의 기본적인 틀을 잡아주어서 프로젝트에서 LLM 이외의 개발 기간이 효과적으로 줄어드는 효과를 보여주었고, 해당 팀원이 없었으면 과연 해당 프로젝트는 사용자에게 우리의 비전을 제대로 보여주는 것이 가능했을까라는 생각이 날 만큼 요번 프로젝트에서 LLM 이외에도 영향력을 많이 준 팀원으로 생각이 난다.
            </td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">최수아</td>
            <td style="border: 1px solid #ddd; padding: 10px;"></td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">홍완기</td>
            <td style="border: 1px solid #ddd; padding: 10px;">
            Streamlit 기반 UI/UX와 FastAPI 연동, 디자인 전반을 혼자서 끝까지 완성해 냈습니다.<br />
            화면 하나하나를 직접 다듬고 백엔드와 자연스럽게 이어지도록 신경 써 준 덕분에, 우리 프로젝트가 단순한 기능 모음이 아니라 진짜 서비스처럼 보일 수 있었습니다. 특히 코드를 모듈 단위로 깔끔하게 정리해 두어 이후 관리와 협업이 정말 편했고, 끝까지 책임지고 마무리해 준 점이 인상 깊었습니다.
            </td>
        </tr>
    </tbody>
</table>
<table style="width: 100%; border-collapse: collapse; border: 1px solid #ddd; margin-bottom: 30px;">
    <thead>
        <tr style="background-color: #f8f9fa;">
            <th style="width: 15%; border: 1px solid #ddd; padding: 10px;">대상자</th>
            <th style="width: 15%; border: 1px solid #ddd; padding: 10px;">작성자</th>
            <th style="border: 1px solid #ddd; padding: 10px;">회고 내용</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td rowspan="5" style="text-align: center; font-weight: bold; border: 1px solid #ddd;">조동휘</td>
            <td style="text-align: center; border: 1px solid #ddd;">이창우</td>
            <td style="border: 1px solid #ddd; padding: 10px;">
            runpod 환경이 급격히 변화하여 모델 서빙 부분에 있어 계획보다 훨씬 많은 난제들이 있었는데, 수많은 시도를 통해 결국 방법을 찾아내 서비스에 성공적으로 적용할 수 있었습니다. 또한 백엔드와 프론트, db각각에 최적화된 docker image를 구성하고 배포하여 container 기반 개발을 통해 package dependency와 같은 문제를 원천적으로 차단할 수 있었습니다. 또한 기존 json dict을 활용하던 구조를 pydantic schema로 전환하고, db 조회 부분을 repository로 분리하여 schema/repository/service의 레이어 구조를 작성하여 코드 유지보수가 더 쉽도록 만들었습니다. 각 부분에 대해 pytest도 작성하여 모든 컴포넌트들이 정상적으로 작동하는지 쉽게 점검해 볼 수 있도록 해 오류가 나는 부분을 빠르게 찾을 수도 있었습니다. 덕분에 구조 설계에 있어 또 하나를 배워가는 뜻깊은 경험을 할 수 있었던 것 같습니다.
            </td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">장한재</td>
            <td style="border: 1px solid #ddd; padding: 10px;">
            인프라와 db를 담당하면서 프로젝트가 실제로 연결되고 실행될 수 있는 환경을 구축해 주셨다. 기능 구현만큼이나 실행 환경과 연결 구조를 안정적으로 맞추는 일이 중요했는데, 이 부분을 꾸준히 받쳐 주신 덕분에 전체 시스템이 돌아갈 수 있었다. 눈에 바로 드러나지 않는 부분까지 책임감 있게 챙겨 주신 점이 인상적이었다.
            </td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">전종혁</td>
            <td style="border: 1px solid #ddd; padding: 10px;">
            Docker와 Docker Compose를 이용한 서비스 컨테이너화를 주도하여 복잡한 실행 환경을 단일화했습니다.<br />
            특히 RunPod의 GPU 자원을 안정적으로 확보하고 외부 배포 환경을 완벽하게 구축함으로써,<br />
            팀원들이 각자의 OS나 로컬 사양에 구애받지 않고 실시간으로 개발 및 테스트를 진행할 수 있는 '무중단 협업 인프라'를 제공해 준 것이 프로젝트 가속화의 핵심이었습니다.<br />
            또한 Github Wiki 작업과, CI/CD 자동화 작업 또한 훌륭하게 해냈습니다.
            </td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">최수아</td>
            <td style="border: 1px solid #ddd; padding: 10px;"></td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">홍완기</td>
            <td style="border: 1px solid #ddd; padding: 10px;">
            MySQL 9.3 기반 벡터 연산 최적화 DB 구성, Docker 환경 세팅, RunPod 연동을 위한 SSH 터널링·점프 서버까지 인프라 전반을 혼자 끝까지 책임져 주었습니다.<br />
            가장 까다롭고 눈에 잘 보이지 않는 영역을 묵묵히 챙겨 준 덕분에 우리 모두가 흔들림 없이 개발에 집중할 수 있었습니다. 팀의 기반을 단단하게 잡아 준 점이 정말 든든했습니다.
            </td>
        </tr>
    </tbody>
</table>
<table style="width: 100%; border-collapse: collapse; border: 1px solid #ddd; margin-bottom: 30px;">
    <thead>
        <tr style="background-color: #f8f9fa;">
            <th style="width: 15%; border: 1px solid #ddd; padding: 10px;">대상자</th>
            <th style="width: 15%; border: 1px solid #ddd; padding: 10px;">작성자</th>
            <th style="border: 1px solid #ddd; padding: 10px;">회고 내용</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td rowspan="5" style="text-align: center; font-weight: bold; border: 1px solid #ddd;">최수아</td>
            <td style="text-align: center; border: 1px solid #ddd;">이창우</td>
            <td style="border: 1px solid #ddd; padding: 10px;">
             프로젝트 운영의 근간이 되는 세부 일정과 문서를 세세하게 관리하며 팀의 ‘나침반’과 같은 역할을 수행해 주셨습니다. 처음 작성해 보는 Jira를 통해 세세하게 작업을 설정하고, WBS와 회의록을 체계적으로 관리해 협업 효율을 극대화했습니다. 리트리버의 성능 향상과 검색 성능 평가에 활용할 수 있는 bm25와 토크나이저 기반 점수 계산 로직을 구현해 주셔서 이를 기반으로 ‘기술 키워드 매칭률’이라는 평가 지표를 도출해 낼 수 있었고 관련 코드 구현 시간을 크게 줄일 수 있었습니다. 무엇보다도 프로젝트의 변경 사항을 빠르게 발표 자료에 반영하여 40분이라는 긴 시간 동안 복잡한 기술적 내용들을 성공적으로 발표해 주셔서 훌륭한 마무리가 되었던 것 같습니다.
             </td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">장한재</td>
            <td style="border: 1px solid #ddd; padding: 10px;">
            PM 역할을 맡아 프로젝트의 전체 흐름을 정리하고, 각자의 작업이 한 방향으로 이어질 수 있도록 잘 조율해 주셨다. 진행 과정에서 일정이나 우선순위를 정리해 주신 덕분에 팀원들이 각자 맡은 일에 더 집중할 수 있었고, 프로젝트도 크게 흔들리지 않고 안정적으로 진행될 수 있었다. 전체를 보는 시각으로 팀을 잘 이끌어 주셨다고 생각한다.
            </td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">전종혁</td>
            <td style="border: 1px solid #ddd; padding: 10px;">
                프로젝트의 전체적인 방향성을 잡는 컨트롤 타워 역할을 훌륭히 수행했습니다.<br />
                일정 관리 툴을 활용한 체계적인 마일스톤 관리와 요구사항 명세서 작성을 통해 팀의 리소스 낭비를 막았으며,
                기술적 이슈로 난항을 겪을 때마다 명확한 우선순위를 제시했습니다.<br />
                또한, 팀의 대표 발표자로서 복잡한 기술 스택을 청중이 이해하기 쉽게 전달하는 최선의 역량을 보여주었습니다.
            </td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">조동휘</td>
            <td style="border: 1px solid #ddd; padding: 10px;">
            요번 프로젝트는 개발적인 내용보다는 개발 외적으로 어떻게 해야 하는가에 대한 고민이 많았지만, 해당 팀원 덕분에 그 고민을 많이 덜어낼 수 있었다.<br />
            프로젝트의 일정 관리를 어떻게 해야 하는가를 개인적으로 공부해서 해당 프로젝트에 적용해주어서 현재 프로젝트의 현황을 파악할 수 있었으며, 일정이 밀릴 것 같으면 계속 말을 해주어서 일정이 최대한 밀리지 않도록 조절해주어서 감사하다.<br />
            프로젝트를 학원 동기분들에게 발표해주어야 했는데, 개인적인 생각으로는 기술적인 부분이 많이 어려워서 어떻게든 쉽게 풀어서 설명해주어야 한다고 생각했다. 그런데 그 역할을 완벽하게 진행해주어서 우리의 프로젝트가 남들에게도 공유되는 성과를 만들어 주셔서 고맙다고 생각이 듭니다.
            </td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">홍완기</td>
            <td style="border: 1px solid #ddd; padding: 10px;">
            프로젝트 전반의 운영 관리(PM)부터 각종 문서 제작, PPT와 최종 발표까지 전적으로 도맡아 주었습니다.<br />
            일정 조율과 방향 정리처럼 눈에 잘 드러나지 않지만 팀이 흔들리지 않게 잡아 주는 역할을 묵묵히 해 준 덕분에, 우리 모두가 각자 맡은 부분에 집중할 수 있었습니다.<br />
            특히 발표 자료와 발표까지 책임지고 마무리해 준 모습이 정말 인상 깊었고, 팀 입장에서 큰 힘이 되었습니다.
            </td>
        </tr>
    </tbody>
</table>
<table style="width: 100%; border-collapse: collapse; border: 1px solid #ddd; margin-bottom: 30px;">
    <thead>
        <tr style="background-color: #f8f9fa;">
            <th style="width: 15%; border: 1px solid #ddd; padding: 10px;">대상자</th>
            <th style="width: 15%; border: 1px solid #ddd; padding: 10px;">작성자</th>
            <th style="border: 1px solid #ddd; padding: 10px;">회고 내용</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td rowspan="5" style="text-align: center; font-weight: bold; border: 1px solid #ddd;">홍완기</td>
            <td style="text-align: center; border: 1px solid #ddd;">이창우</td>
            <td style="border: 1px solid #ddd; padding: 10px;">
            이용자가 체감하는 서비스의 가치를 높이기 위해 LLM의 가장 까다로운 과제 중 하나인 ‘글자 수 조절 문제’에 대해 해결책을 찾기 위해 다방면으로 노력하셨습니다. 다양한 프롬포트 기법을 테스트하며 최적의 분량 조절 노하우를 도출해 실제 생성 로직에 적용할 수 있었습니다. 또한 수아님과 협업하며 프로젝트에서 도출된 여러 산출물에 대해 체계적인 문서를 작성해 주셨고 개발 과정에서 서비스의 목적을 잃지 않도록 조언을 아끼지 않으셨습니다. 또 직접 프로토타입을 테스트하며 사용자 중심의 디테일과 개선 방안을 상세히 제공해 주셔서 프로젝트가 더욱 견고하고 입체적으로 성장할 수 있었던 것 같습니다.
            </td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">장한재</td>
            <td style="border: 1px solid #ddd; padding: 10px;">발표자료 준비와 글자 수, 문항 조건 등 세부 기준 검토를 맡아 결과물을 한층 더 정돈되게 만들어 주셨다. 단순히 내용을 정리하는 데서 끝나지 않고, 발표와 제출 상황에 맞게 결과를 다듬는 부분까지 꼼꼼하게 챙겨 주셔서 전체 완성도를 높이는 데 큰 도움이 되었다. 세부 조건을 놓치지 않고 계속 점검해 준 점이 특히 인상 깊었다.
            </td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">전종혁</td>
            <td style="border: 1px solid #ddd; padding: 10px;">
            사용자 관점에서의 철저한 UX 테스트를 통해 서비스의 완성도를 한 차원 높였습니다.<br /> 
            개발자가 간과하기 쉬운 세밀한 버그들을 날카롭게 포착하여 수정함으로써 사용자 친화적인 디테일을 구현하는 데 결정적인 역할을 했습니다.<br />
            또한, 프로젝트의 성과를 효과적으로 전달하기 위해 발표 자료의 논리적인 프레임워크를 설계하고 내용을 풍성하게 채워 넣어 팀의 기술력을 대외적으로 입증하는 데 기여했습니다.
            </td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">조동휘</td>
            <td style="border: 1px solid #ddd; padding: 10px;">
            요번 프로젝트에서 문서와 test를 도맡아서 이끌어 주셔서 개발을 한 이후에 어떻게 테스트를 진행해야 하는지에 대한 고민을 완벽하게 덜어 주셨다.<br />
            일본에서 직장을 다닐 때 테스트가 얼마나 중요한지 깨닫고 있어서 테스트가 평가 항목에 있어서 어떻게 해야 하는가를 고민하고 있었는데, 이러한 부분에 대한 방법과 기준을 찾아서 sample code를 만들어 주셔서 해당 코드를 기반으로 test 파일을 만들어 프로젝트의 품질을 조금 더 높이는 데 지대한 영향을 주었다고 생각합니다.<br />
            또한 문서 정리도 도맡아서 해주셔서 개발을 마무리하고 문서 작성을 해야 하는 시간에 작성해주신 문서를 기반으로 수정 작업을 해서 조금은 문서 작업을 원활하게 진행한 것으로 생각이 납니다.
            </td>
        </tr>
        <tr>
            <td style="text-align: center; border: 1px solid #ddd;">최수아</td>
            <td style="border: 1px solid #ddd; padding: 10px;"></td>
        </tr>
    </tbody>
</table>

---

## 📜 License

본 프로젝트는 **MIT License**를 따릅니다.<br/>
모든 소스 코드 및 관련 문서의 사용 및 배포 규정은 [LICENSE](./LICENSE) 파일에서 확인하실 수 있습니다.
<div align= "center">
Copyright (c) 2026 SK Networks 26th 팀 조라에몽 (Team Joraemon)</div>
