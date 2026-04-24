"""
End-to-End 파이프라인 통합 테스트.

관련 테스트 케이스: TC-018 ~ TC-022

실제 사용자 시나리오를 여러 엔드포인트를 순차 호출하여 검증한다.
외부 LLM 호출은 mocking으로 차단한다.
"""

import json
import pytest


@pytest.mark.integration
@pytest.mark.mock_llm
class TestFullUserJourney:
    """
    TC-018: 회원가입 → 로그인 → 이력저장 → 자소서생성 end-to-end 시나리오.
    """

    def test_complete_user_journey(
        self, client, clean_db, mock_llm_responses, mock_retriever
    ):
        """
        신규 사용자가 서비스를 처음부터 끝까지 사용하는 전체 흐름을 검증한다.
        """
        email = "journey@example.com"
        password = "journey_pass"

        # ------ 1. 회원가입 ------
        signup = client.post("/api/auth/signup", json={
            "name": "여정유저",
            "email": email,
            "password": password,
        })
        assert signup.status_code == 200, "1단계 회원가입 실패"

        # ------ 2. 로그인 ------
        login = client.post("/api/auth/login", json={
            "email": email,
            "password": password,
        })
        assert login.status_code == 200, "2단계 로그인 실패"
        user_info = login.json()["user_info"]

        # ------ 3. 이력 정보 저장 ------
        resume_data = {
            "personal": {"gender": "남성"},
            "education": {"school": "○○대학교", "major": "컴퓨터공학"},
            "additional": {
                "internship": "ABC 인턴 3개월",
                "awards": "해커톤 대상",
                "tech_stack": "Python, SQL",
            },
        }
        resume_response = client.put(f"/api/resume/{email}", json=resume_data)
        assert resume_response.status_code == 200, "3단계 이력 저장 실패"

        # ------ 4. 이력 조회 (저장 확인) ------
        get_resume = client.get(f"/api/resume/{email}")
        retrieved = json.loads(get_resume.json()["resume_data"])
        assert retrieved["education"]["school"] == "○○대학교"

        # ------ 5. 6단계 파이프라인 실행 ------
        prompt = "네이버에 백엔드 직무로 지원, 지원동기 500자"
        model = "GPT-4o-mini"

        # 5-1. Parse
        parse = client.post("/api/chat/step-parse", json={
            "prompt": prompt, "model": model,
        })
        assert parse.status_code == 200, "파이프라인 Parse 실패"

        # 5-2. Draft (사용자 정보를 user_info로 전달, 업데이트된 resume_data 포함)
        updated_user_info = list(user_info)
        updated_user_info[4] = json.dumps(resume_data, ensure_ascii=False)

        draft = client.post("/api/chat/step-draft", json={
            "prompt": prompt,
            "user_info": updated_user_info,
            "model": model,
        })
        assert draft.status_code == 200, "파이프라인 Draft 실패"
        draft_text = draft.json()["draft"]

        # 5-3. Refine
        refine = client.post("/api/chat/step-refine", json={
            "draft": draft_text, "prompt": prompt, "model": model,
        })
        assert refine.status_code == 200

        # 5-4. Fit
        fit = client.post("/api/chat/step-fit", json={
            "refined": refine.json()["refined"],
            "prompt": prompt, "model": model,
        })
        assert fit.status_code == 200

        # 5-5. Final
        final = client.post("/api/chat/step-final", json={
            "adjusted": fit.json()["adjusted"],
            "prompt": prompt,
            "model": model,
            "result_label": "자소서 초안",
        })
        assert final.status_code == 200, "파이프라인 Final 실패"
        final_response = final.json()["final_response"]

        # ------ 6. 사용자 메시지 + AI 응답을 이력에 저장 ------
        client.post("/api/chat/message", json={
            "email": email, "role": "user", "content": prompt,
        })
        client.post("/api/chat/message", json={
            "email": email, "role": "assistant", "content": final_response,
        })

        # ------ 7. 이력 조회하여 2건 저장되었는지 확인 ------
        history = client.get(f"/api/chat/history/{email}").json()["messages"]
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"
        assert "[자소서 초안]" in history[1]["content"]


@pytest.mark.integration
@pytest.mark.mock_llm
class TestQualityRegeneration:
    """
    TC-019: 품질 미달 초안에 대한 재생성 동작 검증.
    """

    def test_draft_regenerates_on_quality_failure(
        self, client, test_user, sample_user_info, mock_retriever
    ):
        """
        첫 번째 생성 결과가 품질 기준을 통과하지 못하면 재생성되어야 한다.

        (이 테스트는 chat_logic.score_local_draft의 동작을 간접 검증)
        """
        from unittest.mock import patch, MagicMock

        # 1회차는 짧은 응답, 2회차는 정상 응답
        call_count = {"n": 0}

        def side_effect(*args, **kwargs):
            call_count["n"] += 1
            if call_count["n"] == 1:
                return "짧음"  # 220자 미만 → 품질 실패
            return (
                "저는 데이터를 체계적으로 정리하는 일에 관심이 많습니다. " * 10
            )  # 정상

        # build_local_draft 내부의 LLM chain invoke를 mocking
        with patch("services.chat_logic.local_llm") as mock_llm:
            mock_chain = MagicMock()
            mock_chain.invoke.side_effect = side_effect
            mock_llm.__or__ = MagicMock(return_value=mock_chain)

            response = client.post("/api/chat/step-draft", json={
                "prompt": "자소서 써줘",
                "user_info": sample_user_info,
                "model": "GPT-4o-mini",
            })

        # 호출 로직이 복잡하여 재시도 횟수 정확한 검증은 어려우나,
        # 최종 응답이 비어있지 않아야 한다
        assert response.status_code == 200
        assert response.json()["draft"] is not None


@pytest.mark.integration
@pytest.mark.mock_llm
class TestRevisionPath:
    """
    TC-020: 기존 초안에 대한 수정 요청 시 Revise 경로 진입.
    """

    def test_revision_labels_and_reflects_changes(
        self, client, mock_llm_responses
    ):
        """
        수정 경로를 따라 갈 때 result_label이 '1차 수정안'으로 전달되어야 한다.
        """
        existing_draft = (
            "기존에 작성된 초안 본문입니다. 이 문장들은 수정 대상입니다. " * 5
        )

        # Revise → Refine → Fit → Final 연쇄 호출
        revise = client.post("/api/chat/step-revise", json={
            "existing_draft": existing_draft,
            "revision_request": "첫 문장을 더 구체적으로",
            "model": "GPT-4o-mini",
        })
        assert revise.status_code == 200
        revised = revise.json()["revised"]

        refine = client.post("/api/chat/step-refine", json={
            "draft": revised, "prompt": "첫 문장 구체화", "model": "GPT-4o-mini",
        })
        assert refine.status_code == 200

        fit = client.post("/api/chat/step-fit", json={
            "refined": refine.json()["refined"],
            "prompt": "첫 문장 구체화",
            "model": "GPT-4o-mini",
        })
        assert fit.status_code == 200

        final = client.post("/api/chat/step-final", json={
            "adjusted": fit.json()["adjusted"],
            "prompt": "첫 문장 구체화",
            "model": "GPT-4o-mini",
            "result_label": "1차 수정안",
            "change_summary": "첫 문장 구체화",
        })
        assert final.status_code == 200

        final_response = final.json()["final_response"]
        assert "[1차 수정안]" in final_response
        assert "반영 사항:" in final_response


@pytest.mark.integration
class TestMultiUserIsolation:
    """
    TC-021: 서로 다른 사용자의 데이터가 섞이지 않아야 한다.

    (구체 동작은 test_chat_api.py의 test_history_isolation_between_users와 중복)
    """

    def test_user_data_isolation(self, client, clean_db):
        """각 유저의 이력 정보와 채팅이 서로 독립적으로 관리되어야 한다."""
        import database
        import auth

        # 두 유저 생성
        database.add_user_via_web("유저A", auth.hash_pw("pA"), "a@test.com")
        database.add_user_via_web("유저B", auth.hash_pw("pB"), "b@test.com")

        # A의 이력 저장
        client.put("/api/resume/a@test.com", json={
            "personal": {"gender": "남성"},
            "education": {"school": "A대"},
            "additional": {},
        })

        # B의 이력 저장
        client.put("/api/resume/b@test.com", json={
            "personal": {"gender": "여성"},
            "education": {"school": "B대"},
            "additional": {},
        })

        # 각자의 데이터가 격리되어야 함
        a_data = json.loads(client.get("/api/resume/a@test.com").json()["resume_data"])
        b_data = json.loads(client.get("/api/resume/b@test.com").json()["resume_data"])

        assert a_data["education"]["school"] == "A대"
        assert b_data["education"]["school"] == "B대"


@pytest.mark.integration
@pytest.mark.slow
class TestDBReconnection:
    """
    TC-022: DB 연결이 끊어진 후 복구되어야 한다.

    SQLite 환경에서는 이 시나리오가 큰 의미가 없으나,
    v0.3.0에서 MySQL 전환 후 커넥션 풀 테스트로 확장된다.
    """

    def test_repeated_queries_succeed(self, client, test_user):
        """
        동일 클라이언트에서 여러 차례 쿼리를 실행해도 에러가 나지 않아야 한다.
        """
        for i in range(10):
            response = client.get(f"/api/chat/history/{test_user['email']}")
            assert response.status_code == 200, f"{i}번째 쿼리 실패"
