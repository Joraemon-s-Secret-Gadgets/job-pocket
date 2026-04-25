"""
run_exaone.py

RunPod Serverless 엔드포인트를 통해 EXAONE 모델 추론을 수행하는 모듈입니다.
비동기 처리(Async)와 폴링(Polling) 로직을 결합하여 대규모 언어 모델의 생성 응답을 안정적으로 가져옵니다.

주요 기능:
- RunPod /run 엔드포인트를 이용한 비동기 추론 작업 시작
- 작업 완료(COMPLETED) 시까지 /status 엔드포인트 주기적 폴링
- 최초 요청 시 즉시 완료된 결과 처리 (Zero-wait response)
- LangSmith Tracing 연동을 통한 추론 과정 모니터링
"""

import os
import asyncio
import httpx
from typing import Any, List, Dict
from langsmith import traceable

async def _call_exaone_async(messages: List[Dict[str, str]], temperature: float) -> Dict[str, Any]:
    """
    내부 비동기 처리 로직:
    최초 실행 요청의 응답을 먼저 확인하고, 미완료 시에만 폴링을 수행합니다.
    폴링 시마다 로그를 출력합니다.
    """
    api_key = os.getenv("RUNPOD_API_KEY")
    endpoint_id = os.getenv("RUNPOD_ENDPOINT_ID")
    
    if not api_key or not endpoint_id:
        return {"status": "FAILED", "error": "환경 변수 미설정"}

    url_run = f"https://api.runpod.ai/v2/{endpoint_id}/run"
    url_status_base = f"https://api.runpod.ai/v2/{endpoint_id}/status"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "input": {
            "messages": messages,
            "temperature": temperature
        }
    }

    async with httpx.AsyncClient(timeout=300.0) as client:
        # 1. 작업 실행 요청
        try:
            print(f"📡 [RunPod Launch] 요청을 보냅니다... (Model: EXAONE)")
            res = await client.post(url_run, json=payload, headers=headers)
            res.raise_for_status()
            launch_data = res.json()
        except Exception as e:
            print(f"❌ [RunPod Launch] 실행 요청 실패: {str(e)}")
            return {"status": "FAILED", "error": f"실행 요청 실패: {str(e)}"}

        # 최초 요청 응답에서 이미 완료/실패 여부 확인
        status = launch_data.get("status")
        job_id = launch_data.get("id")
        
        if status in ["COMPLETED", "FAILED", "CANCELLED"]:
            print(f"✅ [RunPod Launch] 즉시 완료되었습니다. (Status: {status})")
            return launch_data

        if not job_id:
            print(f"⚠️ [RunPod Launch] Job ID를 받지 못했습니다.")
            return launch_data

        # 2. 미완료 상태인 경우에만 폴링 수행
        print(f"⏳ [RunPod Polling] 시작 (Job ID: {job_id})")
        max_retries = 150
        for attempt in range(max_retries):
            await asyncio.sleep(2)
            try:
                status_res = await client.get(f"{url_status_base}/{job_id}", headers=headers)
                status_res.raise_for_status()
                status_data = status_res.json()
                
                status = status_data.get("status")
                print(f"🔄 [RunPod Polling] {attempt+1}/{max_retries} - 현재 상태: {status}")
                
                if status in ["COMPLETED", "FAILED", "CANCELLED"]:
                    print(f"🏁 [RunPod Polling] 작업이 종료되었습니다. (Status: {status})")
                    return status_data
                
            except Exception as e:
                print(f"⚠️ [RunPod Polling] {attempt+1}차 조회 중 일시적 오류: {str(e)}")
                continue
            
        print(f"⏰ [RunPod Polling] 최대 대기 시간을 초과했습니다.")
        return status_data if 'status_data' in locals() else launch_data

@traceable(run_type="llm", name="EXAONE_RunPod_Inference")
def call_exaone(messages: List[Dict[str, str]], temperature: float = 0.7) -> Dict[str, Any]:
    """
    외부 인터페이스 (동기)
    """
    try:
        return asyncio.run(_call_exaone_async(messages, temperature))
    except Exception as e:
        return {
            "status": "FAILED", 
            "error": f"비동기 실행 예외: {str(e)}"
        }
