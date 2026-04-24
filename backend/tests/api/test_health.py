"""
Health 엔드포인트 API 테스트.

관련 테스트 케이스: TC-028
"""

import pytest


@pytest.mark.api
class TestHealthAPI:
    """GET /health/z 엔드포인트 검증."""

    def test_health_check_returns_200(self, client):
        """TC-028: /health/z가 HTTP 200과 헬스 정보를 반환해야 한다."""
        response = client.get("/health/z")

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}. "
            f"Body: {response.text}"
        )

    def test_health_check_response_schema(self, client):
        """/health/z 응답에 필수 필드가 모두 포함되어야 한다."""
        response = client.get("/health/z")
        data = response.json()

        required_fields = {"status", "service", "version", "message"}
        missing = required_fields - set(data.keys())
        assert not missing, f"응답에서 누락된 필드: {missing}"

    def test_health_check_status_is_healthy(self, client):
        """status 필드가 healthy 상태를 나타내야 한다."""
        response = client.get("/health/z")
        data = response.json()

        assert "healthy" in data["status"].lower(), (
            f"status가 healthy를 포함하지 않음: {data['status']}"
        )

    def test_health_check_service_name(self, client):
        """service 필드가 job-pocket이어야 한다."""
        response = client.get("/health/z")
        data = response.json()

        assert data["service"] == "job-pocket"

    @pytest.mark.slow
    def test_health_check_response_time(self, client):
        """/health/z는 1초 이내로 응답해야 한다."""
        import time

        start = time.time()
        response = client.get("/health/z")
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 1.0, f"응답 시간 초과: {elapsed:.3f}s"
