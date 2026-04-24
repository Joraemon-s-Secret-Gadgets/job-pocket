"""
Authentication API 테스트.

관련 테스트 케이스: TC-001 ~ TC-005
커버하는 엔드포인트:
  - POST /api/auth/signup
  - POST /api/auth/login
  - POST /api/auth/reset-pw
"""

import pytest


@pytest.mark.api
class TestSignup:
    """회원가입 엔드포인트 검증."""

    def test_signup_success(self, client, clean_db):
        """
        TC-001: 신규 이메일로 회원가입이 성공해야 한다.

        기대 결과:
            - HTTP 200
            - {"status": "success", "detail": "회원가입 성공"}
            - DB에 해당 이메일이 저장됨
        """
        response = client.post(
            "/api/auth/signup",
            json={
                "name": "신규유저",
                "email": "newuser@example.com",
                "password": "pass123",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "회원가입 성공" in data["detail"]

        # DB 검증
        import database
        user = database.get_user("newuser@example.com")
        assert user is not None, "DB에 유저가 생성되지 않음"
        assert user[0] == "신규유저"

    def test_signup_password_is_hashed(self, client, clean_db):
        """비밀번호가 평문으로 저장되지 않고 SHA-256 해시로 저장되어야 한다."""
        plain_password = "pass123"
        client.post(
            "/api/auth/signup",
            json={
                "name": "해시테스트",
                "email": "hash@example.com",
                "password": plain_password,
            },
        )

        import database
        user = database.get_user("hash@example.com")
        stored_password = user[1]

        assert stored_password != plain_password, "비밀번호가 평문 저장됨"
        assert len(stored_password) == 64, "SHA-256 해시 길이가 아님"

        # 같은 값 해싱 시 일치 확인
        import auth
        assert stored_password == auth.hash_pw(plain_password)

    def test_signup_duplicate_email_returns_400(self, client, test_user):
        """
        TC-002: 이미 가입된 이메일로 재가입 시도 시 400 에러.
        """
        response = client.post(
            "/api/auth/signup",
            json={
                "name": "중복유저",
                "email": test_user["email"],  # 이미 가입된 이메일
                "password": "anotherpass",
            },
        )

        assert response.status_code == 400
        assert "이미" in response.json()["detail"]

    @pytest.mark.parametrize("invalid_payload", [
        {},  # 빈 바디
        {"email": "incomplete@example.com"},  # name, password 누락
        {"name": "a", "email": "b", "password": ""},  # 빈 비밀번호
    ])
    def test_signup_invalid_payload_returns_422(self, client, clean_db, invalid_payload):
        """Pydantic 검증 실패 시 422 반환."""
        response = client.post("/api/auth/signup", json=invalid_payload)
        assert response.status_code in (400, 422), (
            f"예상 상태 코드가 아님: {response.status_code}"
        )


@pytest.mark.api
class TestLogin:
    """로그인 엔드포인트 검증."""

    def test_login_success(self, client, test_user):
        """
        TC-003: 올바른 자격증명으로 로그인 성공.
        """
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user["email"],
                "password": test_user["password"],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "user_info" in data
        assert data["user_info"][2] == test_user["email"]

    def test_login_user_info_structure(self, client, test_user):
        """로그인 응답의 user_info가 5-tuple 구조여야 한다."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user["email"],
                "password": test_user["password"],
            },
        )

        user_info = response.json()["user_info"]
        assert len(user_info) == 5, (
            "user_info는 [username, password_hash, email, reset_token, resume_data] 5-tuple이어야 함"
        )

    def test_login_wrong_password_returns_401(self, client, test_user):
        """
        TC-004: 잘못된 비밀번호로 로그인 실패 시 401.
        """
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user["email"],
                "password": "wrong_password",
            },
        )

        assert response.status_code == 401
        assert "일치하지 않" in response.json()["detail"]

    def test_login_nonexistent_email_returns_401(self, client, clean_db):
        """존재하지 않는 이메일로 로그인 시도 시 401 반환."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "pass123",
            },
        )

        assert response.status_code == 401


@pytest.mark.api
class TestResetPassword:
    """비밀번호 재설정 엔드포인트 검증."""

    def test_reset_password_success(self, client, test_user):
        """
        TC-005: 비밀번호 재설정 후 새 비밀번호로 로그인 성공.
        """
        new_password = "new_password_456"

        # 1. 비밀번호 변경
        response = client.post(
            "/api/auth/reset-pw",
            json={
                "email": test_user["email"],
                "new_password": new_password,
            },
        )
        assert response.status_code == 200
        assert response.json()["status"] == "success"

        # 2. 새 비밀번호로 로그인 성공 확인
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": test_user["email"],
                "password": new_password,
            },
        )
        assert login_response.status_code == 200

    def test_reset_password_old_password_fails(self, client, test_user):
        """재설정 후 기존 비밀번호로 로그인 시도 시 실패해야 한다."""
        new_password = "new_password_456"

        client.post(
            "/api/auth/reset-pw",
            json={
                "email": test_user["email"],
                "new_password": new_password,
            },
        )

        # 기존 비밀번호로 로그인 시도
        old_login = client.post(
            "/api/auth/login",
            json={
                "email": test_user["email"],
                "password": test_user["password"],  # 기존 비밀번호
            },
        )
        assert old_login.status_code == 401

    def test_reset_password_nonexistent_email(self, client, clean_db):
        """존재하지 않는 이메일에 대해 재설정 시도 시 400 반환."""
        response = client.post(
            "/api/auth/reset-pw",
            json={
                "email": "nonexistent@example.com",
                "new_password": "something",
            },
        )
        assert response.status_code == 400
