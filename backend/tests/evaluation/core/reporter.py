"""
평가 결과를 분석하여 통계 정보를 생성하고 리포트를 출력 및 저장하는 모듈입니다.
"""
import json
import numpy as np
from datetime import datetime
from collections import defaultdict
from .evaluation_test_config import RESULT_DIR

class EvaluationReporter:
    """
    수집된 상세 평가 데이터를 기반으로 요약 통계를 산출하고 가독성 있는 리포트를 생성하는 클래스입니다.
    """
    def __init__(self):
        """
        리포터 객체를 초기화하고 결과 저장 폴더를 생성합니다.
        """
        RESULT_DIR.mkdir(parents=True, exist_ok=True)

    def generate_summary(self, detailed_reports: list) -> dict:
        """
        상세 리포트 리스트를 바탕으로 직무별, 순위별 평균 통계를 계산합니다.
        
        Args:
            detailed_reports (list): 개별 쿼리에 대한 평가 결과 리스트
            
        Returns:
            dict: 직무별 및 전체 평균 매칭률이 포함된 요약 통계 데이터
        """
        rank_stats = defaultdict(lambda: {1: [], 2: [], 3: []})
        
        for report in detailed_reports:
            pos = report['position']
            for i, res in enumerate(report['results']):
                rank = i + 1
                if rank <= 3:
                    rank_stats[pos][rank].append(res['match_ratio'])

        summary_stats = {
            "by_position": {},
            "overall": {},
            "evaluated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sample_size": len(detailed_reports)
        }

        all_r1, all_r2, all_r3 = [], [], []

        for pos, ranks in rank_stats.items():
            r1_avg = np.mean(ranks[1]) if ranks[1] else 0
            r2_avg = np.mean(ranks[2]) if ranks[2] else 0
            r3_avg = np.mean(ranks[3]) if ranks[3] else 0

            summary_stats["by_position"][pos] = {
                "rank_1_avg": round(r1_avg, 4),
                "rank_2_avg": round(r2_avg, 4),
                "rank_3_avg": round(r3_avg, 4),
                "total_avg": round(np.mean([r1_avg, r2_avg, r3_avg]), 4)
            }

            all_r1.extend(ranks[1])
            all_r2.extend(ranks[2])
            all_r3.extend(ranks[3])

        summary_stats["overall"] = {
            "rank_1_avg": round(np.mean(all_r1), 4) if all_r1 else 0,
            "rank_2_avg": round(np.mean(all_r2), 4) if all_r2 else 0,
            "rank_3_avg": round(np.mean(all_r3), 4) if all_r3 else 0,
            "total_avg": round(np.mean(all_r1 + all_r2 + all_r3), 4) if all_r1 else 0
        }

        return summary_stats

    def print_report(self, summary: dict):
        """
        생성된 요약 통계를 콘솔에 정돈된 테이블 형식으로 출력합니다.
        
        Args:
            summary (dict): generate_summary()에서 반환된 요약 데이터
        """
        print(f"\n{'='*75}")
        print(f"🏆 [Final Report] 직무 및 순위별 기술 매칭 통계")
        print(f" {'='*75}")
        print(f" {'직무 (Position)':<25} | {'1순위':^12} | {'2순위':^12} | {'3순위':^12}")
        print(f" {'-'*75}")

        for pos, stats in summary["by_position"].items():
            print(f" {pos:<25} | {stats['rank_1_avg']*100:>10.2f}% | {stats['rank_2_avg']*100:>10.2f}% | {stats['rank_3_avg']*100:>10.2f}%")

        print(f" {'-'*75}")
        o = summary["overall"]
        print(f" {'TOTAL AVERAGE':<25} | {o['rank_1_avg']*100:>10.2f}% | {o['rank_2_avg']*100:>10.2f}% | {o['rank_3_avg']*100:>10.2f}%")
        print(f"{'='*75}\n")

    def save_results(self, final_output: dict, prefix: str = "evaluation_results"):
        """
        최종 평가 데이터를 JSON 파일로 저장합니다.
        
        Args:
            final_output (dict): 상세 결과와 요약 통계가 포함된 전체 데이터
            prefix (str): 파일 이름 접두어
        """
        timestamp = datetime.now().strftime("%m%d_%H%M")
        filename = RESULT_DIR / f"{prefix}_{timestamp}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(final_output, f, ensure_ascii=False, indent=4)
        print(f"✅ 평가 결과가 '{filename}'에 저장되었습니다.")
