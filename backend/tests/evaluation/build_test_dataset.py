"""
HuggingFace 데이터셋을 로드하고 정제하여 리트리벌 평가용 테스트 데이터셋을 생성하는 도구입니다.
"""

import sys
import os
from pathlib import Path

# 1. 프로젝트 루트 및 경로 설정
current_file = Path(__file__).resolve()
project_root = current_file.parents[3]  # /app
ingestion_path = project_root / "database" / "ingestion"

# sys.path 최적화 (Shadowing 방지를 위해 backend/ 폴더 자체는 추가하지 않음)
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(ingestion_path) not in sys.path:
    sys.path.insert(0, str(ingestion_path))

# 2. 모듈 alising (backend 하위 모듈들이 서로를 찾을 수 있게 함)
try:
    import backend.common as common

    sys.modules["common"] = common
    import backend.utils as utils

    sys.modules["utils"] = utils
except ImportError:
    pass

import argparse
import pandas as pd
from tqdm import tqdm

try:
    from database.ingestion.loaders.data_loader import fetch_dataset
    from database.ingestion.processors.data_processor import DataProcessor
    from database.ingestion.processors.cleaners.company_cleaner import (
        CompanyNameCleaner,
    )
    from database.ingestion.processors.mappings import (
        COMPANY_EN_TO_KO_MAP,
        COMPANY_TYPO_FIX_MAP,
        COMPANY_CONFLICT_GROUPS,
        COMPANY_PROTECTED_KEYWORDS,
    )
    from backend.tests.evaluation.core.evaluation_test_config import (
        TEST_DATA_PATH,
        TEST_DATA_DIR,
        MIN_TECH_COUNT,
    )
    from backend.tests.evaluation.core import KeywordProcessor
except ImportError as e:
    print(f"❌ 임포트 에러: {e}")
    sys.exit(1)


class TestDatasetBuilder:
    def __init__(self, keyword_processor: KeywordProcessor):
        self.keyword_processor = keyword_processor
        self.company_cleaner = CompanyNameCleaner(
            en_to_ko_map=COMPANY_EN_TO_KO_MAP,
            typo_fix_map=COMPANY_TYPO_FIX_MAP,
            conflict_groups=COMPANY_CONFLICT_GROUPS,
            protected_keywords=COMPANY_PROTECTED_KEYWORDS,
        )
        self.data_processor = DataProcessor(self.company_cleaner)
        TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)

    def build_and_save(
        self, min_tech: int = MIN_TECH_COUNT, limit: int = None, output_name: str = None
    ):
        print(
            f"🚀 테스트셋 생성 시작 (기술 스택 최소 {min_tech}개, 최대 {limit if limit else '전체'}건)"
        )
        try:
            raw_dataset = fetch_dataset(data_split="test")
        except Exception as e:
            print(f"❌ 데이터 로드 실패: {e}")
            return

        print("⏳ Ingestion 전처리 파이프라인 실행 중...")
        processed_df = self.data_processor.run_preprocess_pipeline(raw_dataset)

        print("🔍 기술 키워드 추출 및 필터링 중...")
        refined_rows = []
        for _, row in tqdm(processed_df.iterrows(), total=len(processed_df)):
            position = row["position_type"]
            resume_text = row["resume_cleaned"]
            found_techs = self.keyword_processor.get_query_tech_profile(
                resume_text, position
            )
            if len(found_techs) >= min_tech:
                refined_rows.append(
                    {
                        "position_type": position,
                        "resume_cleaned": resume_text,
                        "found_tech_list": sorted(list(found_techs)),
                        "found_tech_count": len(found_techs),
                    }
                )
                if limit and len(refined_rows) >= limit:
                    break

        if not refined_rows:
            print("⚠️ 조건에 맞는 데이터가 없습니다.")
            return

        evaluation_df = pd.DataFrame(refined_rows)
        save_name = output_name if output_name else "retrieval_test_dataset"
        if not save_name.endswith(".json"):
            save_name += ".json"
        save_path = TEST_DATA_DIR / save_name

        evaluation_df.to_json(save_path, orient="records", force_ascii=False, indent=4)
        print(f"\n✅ 테스트셋 생성 완료! 💾 저장 경로: {save_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", "-n", type=int, default=None)
    parser.add_argument("--min-tech", "-m", type=int, default=MIN_TECH_COUNT)
    parser.add_argument("--output", "-o", type=str, default=None)
    args = parser.parse_args()

    # os.environ['HF_HOME'] = "/app/backend/hf_cache"

    kw_processor = KeywordProcessor()
    builder = TestDatasetBuilder(kw_processor)
    builder.build_and_save(
        min_tech=args.min_tech, limit=args.limit, output_name=args.output
    )
