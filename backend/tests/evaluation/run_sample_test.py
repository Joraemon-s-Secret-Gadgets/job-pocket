"""
샘플 데이터셋(evaluation_df_sample.json)을 사용하여 리트리벌 평가를 빠르게 테스트하는 스크립트입니다.
"""

import sys
from pathlib import Path

current_file = Path(__file__).resolve()
backend_root = str(current_file.parents[2])

if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

from tests.evaluation.core.evaluation_test_config import SAMPLE_DATA_PATH
from tests.evaluation.run_retrieval_eval import run_retrieval_evaluation


def run_sample_test():
    print(f"🚀 샘플 데이터를 이용한 테스트 시작")
    print(f"📂 샘플 경로: {SAMPLE_DATA_PATH}")

    run_retrieval_evaluation(test_data_path=SAMPLE_DATA_PATH)


if __name__ == "__main__":
    run_sample_test()
