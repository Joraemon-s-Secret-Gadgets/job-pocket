"""
Resume API 테스트.

관련 테스트 케이스: TC-006 ~ TC-008
커버하는 엔드포인트:
  - GET /api/resume/{email}
  - PUT /api/resume/{email}
"""

import json
import pytest


@pytest.mark.api
class TestGetResume:
    """이력 정보 조회 엔드포인트 검증."""

    def test_get_resume_returns_empty_for_new_user(self, client, test_user):
        """
        신규 유저는 resume_data가 비어 있어야 한다.
        """
        response = client.get(f"/api/resume/{test_user['email']}")

        assert response.status_code == 200
        data = response.json()
        assert "resume_data" in data
        # 신규 유저는 빈 JSON 또는 None/빈 문자열
        assert data["resume_data"] in ("{}", "", None)

    def test_get_resume_returns_saved_data(self, client, test_user):
        """
        TC-006: 저장된 이력 정보를 조회할 수 있어야 한다.
        """
        # 1. 이력 저장
        payload = {
            "personal": {"eng_name": "Hong", "gender": "남성"},
            "education": {"school": "○○대", "major": "컴공"},
            "additional": {
                "internship": "ABC 3개월",
                "awards": "",
                "tech_stack": "Python",
            },
        }
        put_response = client.put(
            f"/api/resume/{test_user['email']}",
            json=payload,
        )
        assert put_response.status_code == 200

        # 2. 조회
        get_response = client.get(f"/api/resume/{test_user['email']}")
        assert get_response.status_code == 200

        resume_str = get_response.json()["resume_data"]
        resume_data = json.loads(resume_str)

        assert resume_data["personal"]["gender"] == "남성"
        assert resume_data["education"]["school"] == "○○대"
        assert resume_data["additional"]["tech_stack"] == "Python"

    def test_get_resume_nonexistent_user_returns_404(self, client, clean_db):
        """
        TC-008: 존재하지 않는 유저 조회 시 404 반환.
        """
        response = client.get("/api/resume/ghost@example.com")

        assert response.status_code == 404
        assert "찾을 수 없" in response.json()["detail"]


@pytest.mark.api
class TestUpdateResume:
    """이력 정보 저장 엔드포인트 검증."""

    def test_update_resume_success(self, client, test_user):
        """
        TC-007: 이력 정보 저장이 성공적으로 수행되어야 한다.
        """
        payload = {
            "personal": {"gender": "여성"},
            "education": {"school": "△△대", "major": "통계학"},
            "additional": {
                "internship": "DEF 인턴",
                "awards": "장학금",
                "tech_stack": "R, Python, SQL",
            },
        }

        response = client.put(
            f"/api/resume/{test_user['email']}",
            json=payload,
        )

        assert response.status_code == 200
        assert response.json()["status"] == "success"

    def test_update_resume_overwrites_previous(self, client, test_user):
        """
        동일 이메일에 대해 PUT은 전체 덮어쓰기 동작을 해야 한다.
        """
        # 최초 저장
        first = {
            "personal": {"gender": "남성"},
            "education": {"school": "A대"},
            "additional": {},
        }
        client.put(f"/api/resume/{test_user['email']}", json=first)

        # 두 번째 저장 (전체 교체)
        second = {
            "personal": {"gender": "여성"},
            "education": {"school": "B대"},
            "additional": {"tech_stack": "Java"},
        }
        client.put(f"/api/resume/{test_user['email']}", json=second)

        # 조회 시 두 번째 값이 반영되어야 함
        response = client.get(f"/api/resume/{test_user['email']}")
        data = json.loads(response.json()["resume_data"])

        assert data["personal"]["gender"] == "여성"
        assert data["education"]["school"] == "B대"
        assert data["additional"]["tech_stack"] == "Java"

    def test_update_resume_empty_payload(self, client, test_user):
        """
        모든 섹션이 비어있는 payload도 허용되어야 한다 (빈 이력).
        """
        response = client.put(
            f"/api/resume/{test_user['email']}",
            json={
                "personal": {},
                "education": {},
                "additional": {},
            },
        )

        assert response.status_code == 200

    def test_update_resume_nonexistent_user(self, client, clean_db):
        """
        존재하지 않는 이메일에 대해 저장 시도 시 400 반환.
        (구현에 따라 404 가능)
        """
        response = client.put(
            "/api/resume/ghost@example.com",
            json={
                "personal": {},
                "education": {},
                "additional": {},
            },
        )

        # 구현에 따라 400 또는 404
        assert response.status_code in (400, 404)

    def test_update_resume_with_korean_content(self, client, test_user):
        """
        한글 콘텐츠가 UTF-8로 정상 저장·조회되어야 한다.
        """
        payload = {
            "personal": {"gender": "남성"},
            "education": {"school": "서울대학교", "major": "컴퓨터공학"},
            "additional": {
                "internship": "삼성전자 인턴 3개월 🎯",
                "awards": "대상",
                "tech_stack": "Python, SQL, 도커",
            },
        }

        client.put(f"/api/resume/{test_user['email']}", json=payload)

        response = client.get(f"/api/resume/{test_user['email']}")
        data = json.loads(response.json()["resume_data"])

        assert data["education"]["school"] == "서울대학교"
        assert "🎯" in data["additional"]["internship"]
