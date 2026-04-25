import httpx
from typing import Any, Dict, Optional

def send_api_request(
    url: str, 
    headers: Dict[str, str], 
    payload: Optional[Dict[str, Any]] = None, 
    method: str = "POST", 
    timeout: float = 300.0
) -> Dict[str, Any]:
    """
    전달받은 URL, 헤더, 페이로드를 사용하여 API 요청(GET/POST)을 보내고 JSON 응답을 반환합니다.
    """
    with httpx.Client(timeout=timeout, follow_redirects=True) as client:
        if method.upper() == "POST":
            response = client.post(url, json=payload, headers=headers)
        else:
            response = client.get(url, headers=headers)
        
        response.raise_for_status() # HTTP 에러 발생 시 예외 발생
        return response.json()
