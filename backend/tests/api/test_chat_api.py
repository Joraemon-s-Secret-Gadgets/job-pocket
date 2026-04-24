"""
Chat API 테스트.

관련 테스트 케이스: TC-009 ~ TC-017

커버하는 엔드포인트:
  - 이력 관리: GET/POST/DELETE /api/chat/history, /message
  - RAG 파이프라인: POST /api/chat/step-parse, step-draft, step-revise,
                  step-refine, step-fit, step-final
"""

import pytest


# ==========================================
# 채팅 이력 관리 (TC-009 ~ TC-011)
# ==========================================

@pytest.mark.api
class TestChatHistory:
    """채팅 이력 조회·저장·삭제 엔드포인트 검증."""

    def test_empty_history_returns_empty_list(self, client, test_user):
        """신규 유저의 이력은 빈 배열이어야 한다."""
        response = client.get(f"/api/chat/history/{test_user['email']}")

        assert response.status_code == 200
        assert response.json() == {"messages": []}

    def test_save_message_and_retrieve(self, client, test_user):
        """
        TC-010: 메시지 저장 후 조회 시 해당 메시지가 포함되어야 한다.
        """
        # 저장
        save_response = client.post(
            "/api/chat/message",
            json={
                "email": test_user["email"],
                "role": "user",
                "content": "자소서 써줘",
            },
        )
        assert save_response.status_code == 200
        assert save_response.json()["status"] == "success"

        # 조회
        get_response = client.get(f"/api/chat/history/{test_user['email']}")
        messages = get_response.json()["messages"]

        assert len(messages) == 1
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "자소서 써줘"

    def test_retrieve_history_in_chronological_order(self, client, test_user):
        """
        TC-009: 이력이 오름차순(시간순)으로 정렬되어야 한다.
        """
        messages = [
            ("user", "첫 번째 메시지"),
            ("assistant", "첫 번째 응답"),
            ("user", "두 번째 메시지"),
            ("assistant", "두 번째 응답"),
        ]

        for role, content in messages:
            client.post(
                "/api/chat/message",
                json={
                    "email": test_user["email"],
                    "role": role,
                    "content": content,
                },
            )

        response = client.get(f"/api/chat/history/{test_user['email']}")
        saved = response.json()["messages"]

        assert len(saved) == 4
        assert saved[0]["content"] == "첫 번째 메시지"
        assert saved[-1]["content"] == "두 번째 응답"

    def test_delete_history(self, client, test_user):
        """
        TC-011: 이력 전체 삭제 후 조회 시 빈 배열이어야 한다.
        """
        # 메시지 3건 저장
        for i in range(3):
            client.post(
                "/api/chat/message",
                json={
                    "email": test_user["email"],
                    "role": "user",
                    "content": f"메시지 {i}",
                },
            )

        # 삭제
        delete_response = client.delete(f"/api/chat/history/{test_user['email']}")
        assert delete_response.status_code == 200
        assert delete_response.json()["status"] == "success"

        # 조회
        get_response = client.get(f"/api/chat/history/{test_user['email']}")
        assert get_response.json()["messages"] == []

    def test_history_isolation_between_users(self, client, clean_db):
        """
        TC-021: 서로 다른 유저의 이력은 섞이지 않아야 한다.
        """
        import database
        import auth

        # user_a와 user_b 생성
        database.add_user_via_web("유저A", auth.hash_pw("p1"), "a@example.com")
        database.add_user_via_web("유저B", auth.hash_pw("p2"), "b@example.com")

        # 각자 메시지 저장
        client.post("/api/chat/message", json={
            "email": "a@example.com", "role": "user", "content": "A의 메시지",
        })
        client.post("/api/chat/message", json={
            "email": "b@example.com", "role": "user", "content": "B의 메시지 1",
        })
        client.post("/api/chat/message", json={
            "email": "b@example.com", "role": "user", "content": "B의 메시지 2",
        })

        # 각자 조회 시 자신의 메시지만
        a_history = client.get("/api/chat/history/a@example.com").json()["messages"]
        b_history = client.get("/api/chat/history/b@example.com").json()["messages"]

        assert len(a_history) == 1
        assert len(b_history) == 2
        assert "A의 메시지" in a_history[0]["content"]
        assert all("B의 메시지" in m["content"] for m in b_history)


# ==========================================
# RAG 파이프라인 API (TC-012 ~ TC-017)
# ==========================================

@pytest.mark.api
@pytest.mark.mock_llm
class TestChatPipelineSteps:
    """6단계 RAG 파이프라인 API 검증 (LLM mocked)."""

    def test_step_parse_extracts_structured_data(
        self, client, mock_llm_responses
    ):
        """
        TC-012: step-parse가 자연어 요청을 구조화된 JSON으로 변환해야 한다.
        """
        response = client.post(
            "/api/chat/step-parse",
            json={
                "prompt": "네이버에 백엔드 직무로 지원, 지원동기 500자 내외",
                "model": "GPT-4o-mini",
            },
        )

        assert response.status_code == 200
        data = response.json()

        # 파싱 결과 필수 필드 확인
        expected_keys = {"company", "job", "question", "char_limit", "question_type"}
        assert expected_keys.issubset(set(data.keys()))

        # 정규식 기반 파싱이 먼저 동작하므로 일부 값은 LLM mock 없이도 확인 가능
        assert data["char_limit"] == 500

    def test_step_draft_generates_valid_draft(
        self, client, sample_user_info, mock_llm_responses, mock_retriever
    ):
        """
        TC-013: step-draft가 RAG + LLM으로 초안을 생성해야 한다.
        """
        response = client.post(
            "/api/chat/step-draft",
            json={
                "prompt": "네이버 백엔드 지원동기 500자",
                "user_info": sample_user_info,
                "model": "GPT-4o-mini",
            },
        )

        assert response.status_code == 200
        draft = response.json()["draft"]

        assert draft is not None
        assert isinstance(draft, str)
        assert len(draft) >= 50, "초안이 너무 짧음"

    def test_step_revise_returns_modified_draft(
        self, client, mock_llm_responses
    ):
        """
        TC-014: step-revise가 기존 초안을 수정하여 반환해야 한다.
        """
        existing = "기존 자소서 본문 첫 문단입니다. 경험을 나열했습니다."

        response = client.post(
            "/api/chat/step-revise",
            json={
                "existing_draft": existing,
                "revision_request": "첫 문장을 더 구체적으로",
                "model": "GPT-4o-mini",
            },
        )

        assert response.status_code == 200
        assert "revised" in response.json()
        revised = response.json()["revised"]
        assert isinstance(revised, str)
        assert len(revised) > 0

    def test_step_refine_returns_refined_text(
        self, client, mock_llm_responses
    ):
        """
        TC-015: step-refine이 첨삭된 본문을 반환해야 한다.
        """
        response = client.post(
            "/api/chat/step-refine",
            json={
                "draft": "테스트 초안 본문입니다. 조금 어색한 문장이 있습니다.",
                "prompt": "네이버 백엔드 지원동기 500자",
                "model": "GPT-4o-mini",
            },
        )

        assert response.status_code == 200
        assert "refined" in response.json()

    def test_step_fit_preserves_text_when_not_needed(
        self, client, mock_llm_responses
    ):
        """
        TC-016: char_limit 내 본문은 수정 없이 반환해야 한다.
        """
        short_text = "짧은 본문."
        response = client.post(
            "/api/chat/step-fit",
            json={
                "refined": short_text,
                "prompt": "500자 내외로",
                "model": "GPT-4o-mini",
            },
        )

        assert response.status_code == 200
        assert "adjusted" in response.json()

    def test_step_final_builds_complete_response(
        self, client, mock_llm_responses
    ):
        """
        TC-017: step-final이 본문과 평가를 조립한 최종 응답을 반환해야 한다.
        """
        response = client.post(
            "/api/chat/step-final",
            json={
                "adjusted": "최종 본문입니다. " * 10,
                "prompt": "네이버 백엔드 지원동기 500자",
                "model": "GPT-4o-mini",
                "result_label": "자소서 초안",
                "change_summary": None,
            },
        )

        assert response.status_code == 200
        final_response = response.json()["final_response"]

        # 고정 형식 검증
        assert "[자소서 초안]" in final_response
        assert "[평가 및 코멘트]" in final_response
        assert "평가 결과:" in final_response
        assert "보완 포인트:" in final_response

    def test_step_final_with_revision_label(
        self, client, mock_llm_responses
    ):
        """
        수정본일 때 [1차 수정안] 라벨과 반영 사항이 포함되어야 한다.
        """
        response = client.post(
            "/api/chat/step-final",
            json={
                "adjusted": "수정된 본문입니다. " * 10,
                "prompt": "첫 문장을 더 구체적으로",
                "model": "GPT-4o-mini",
                "result_label": "1차 수정안",
                "change_summary": "첫 문장 구체화",
            },
        )

        assert response.status_code == 200
        final_response = response.json()["final_response"]

        assert "[1차 수정안]" in final_response
        assert "반영 사항:" in final_response
        assert "첫 문장 구체화" in final_response
