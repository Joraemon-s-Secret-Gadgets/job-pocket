"""
리트리벌 정밀 평가 실행 모듈

이 모듈은 자소서 데이터셋을 기반으로 리트리벌(검색) 시스템의 정확도를 정량적으로 평가합니다.
사용자 쿼리에서 기술 스택을 추출하고, 검색된 결과와의 매칭률(Keyword Match Rate)을 계산하여 리포트를 생성합니다.
"""

import sys
import argparse
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# 프로젝트 루트 경로를 sys.path에 추가하여 패키지 임포트가 가능하게 설정
current_file = Path(__file__).resolve()
backend_root = str(current_file.parents[2])
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

# 모듈화된 구성 요소 임포트
from tests.evaluation.core.evaluation_test_config import (
    MODEL_NAME,
    DEVICE,
    FAISS_INDEX_PATH,
    TEST_DATA_PATH,
    TEST_DATA_DIR,
    TOP_K,
)
from tests.evaluation.core import (
    KeywordProcessor,
    RetrievalEvaluator,
    EvaluationReporter,
)


def run_retrieval_evaluation(test_data_path=None):
    """
    리트리벌 시스템에 대한 정밀 평가를 수행하고 결과를 저장합니다.

    Args:
        test_data_path (str or Path, optional): 평가용 데이터셋(.json) 경로
    """
    # 1. 데이터셋 로드
    if test_data_path is None:
        test_data_path = TEST_DATA_PATH

    print(f"📂 평가 데이터셋 로딩: {test_data_path}")
    try:
        test_df = pd.read_json(test_data_path, orient="records", encoding="utf-8")
    except Exception as e:
        print(f"❌ 데이터셋 로드 실패: {e}")
        return

    # 2. 필수 컴포넌트 초기화
    print("⏳ 임베딩 모델 및 FAISS 인덱스 로딩 중...")
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name=MODEL_NAME,
            model_kwargs={"device": DEVICE},
            encode_kwargs={"normalize_embeddings": True},
        )

        # FAISS 인덱스 로드 (allow_dangerous_deserialization=True는 신뢰할 수 있는 로컬 파일용)
        vectorstore = FAISS.load_local(
            folder_path=str(FAISS_INDEX_PATH),
            embeddings=embeddings,
            allow_dangerous_deserialization=True,
        )
    except Exception as e:
        print(f"❌ 검색 엔진 초기화 실패: {e}")
        return

    # 형태소 분석기, 평가기, 리포터 초기화
    processor = KeywordProcessor()
    evaluator = RetrievalEvaluator(processor)
    reporter = EvaluationReporter()

    # 3. 평가 루프 실행
    detailed_reports = []
    test_limit = len(test_df)
    print(f"🔍 HybridRetriever 평가 시작 (총 {test_limit}건)")

    for idx, row in tqdm(test_df.iterrows(), total=test_limit):
        position = row["position_type"]
        query_text = row["resume_cleaned"]
        query_id = idx + 1

        # FAISS 검색 수행 (상위 TOP_K개 후보 추출)
        try:
            # metadata['id']를 page_content로 사용
            docs = vectorstore.similarity_search(query_text, k=TOP_K)
            retrieved_ids = [int(d.page_content) for d in docs]
        except Exception as e:
            print(f"⚠️ 검색 실패 (Query ID {query_id}): {e}")
            retrieved_ids = []

        # 매칭 분석 (기술 스택 매칭률 계산)
        analysis = evaluator.evaluate_matches(query_text, retrieved_ids, position)

        # 개별 결과 수집
        detailed_reports.append(
            {
                "query_id": query_id,
                "position": position,
                "query_techs": analysis["query_techs"],
                "results": analysis["results"],
            }
        )

    # 4. 통계 산출 및 결과 출력
    summary = reporter.generate_summary(detailed_reports)
    reporter.print_report(summary)

    # 5. 결과 파일 저장
    final_output = {"summary": summary, "details": detailed_reports}
    reporter.save_results(final_output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Job-Pocket HybridRetriever 정밀 평가 스크립트"
    )
    parser.add_argument(
        "--file",
        "-f",
        type=str,
        help="평가에 사용할 데이터셋 파일명 (datasets/ 폴더 기준)",
    )

    args = parser.parse_args()

    target_path = None
    if args.file:
        file_name = args.file if args.file.endswith(".json") else f"{args.file}.json"
        target_path = TEST_DATA_DIR / file_name

    run_retrieval_evaluation(test_data_path=target_path)
