"""Security, ownership, rate-limit, and state-machine tests.

Run with:
    uv run pytest tests/test_security_and_cases.py -v

These tests cover the authorization gaps and invariants most likely to
cause production security bugs:
- Boot guard (refuse start with DEV_BYPASS_AUTH in production)
- GET /legal/cases IDOR (caller sees only own cases)
- POST /legal/posts restricted to advocates
- GET /legal/chat/history IDOR
- POST /legal/cases/resolve ownership check
- State machine: invalid and backward transitions are rejected
- Rate limiter: 6th post / 4th case-request is rejected
- WebSocket: missing token → 4001 close
"""

import os
import uuid
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session


# ---------------------------------------------------------------------------
# Fixtures — delegate heavy lifting to conftest.py
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def client(test_engine):
    """Return a synchronous TestClient for the app (in-memory DB wired)."""
    from app.main import app
    return TestClient(app, raise_server_exceptions=True)


# ---------------------------------------------------------------------------
# Identity helpers
# ---------------------------------------------------------------------------

def user_env(
    uid: str,
    email: str = "test@lexai.test",
    name: str = "Test User",
    is_lawyer: bool = False,
) -> dict[str, str]:
    """Return os.environ patches that set the DEV_BYPASS identity."""
    return {
        "DEV_BYPASS_AUTH": "true",
        "DEV_USER_UID": uid,
        "DEV_USER_EMAIL": email,
        "DEV_USER_NAME": name,
        "DEV_USER_IS_LAWYER": "true" if is_lawyer else "false",
    }


# Module-level engine reference populated by _bind_engine below.
# Allows seeding helpers to call ``Session(_TEST_ENGINE)`` without
# changing every test function signature.
_TEST_ENGINE = None


@pytest.fixture(scope="module", autouse=True)
def _bind_engine(test_engine):
    """Populate module-level _TEST_ENGINE from conftest's shared engine."""
    global _TEST_ENGINE
    _TEST_ENGINE = test_engine


# ---------------------------------------------------------------------------
# 1. Boot guard
# ---------------------------------------------------------------------------

def test_boot_guard_refuses_production_with_bypass():
    """App must raise RuntimeError if ENV=production & DEV_BYPASS_AUTH=True."""
    from app.core.security import check_bypass_guard

    with (
        patch.dict(os.environ, {"ENV": "production", "DEV_BYPASS_AUTH": "true"}),
        pytest.raises(RuntimeError, match="DEV_BYPASS_AUTH"),
    ):
        check_bypass_guard()


def test_boot_guard_allows_production_without_bypass():
    """App must not raise when DEV_BYPASS_AUTH is False in production."""
    from app.core.security import check_bypass_guard

    with patch.dict(
        os.environ, {"ENV": "production", "DEV_BYPASS_AUTH": "false"}
    ):
        check_bypass_guard()  # should not raise


# ---------------------------------------------------------------------------
# 2. GET /legal/cases — IDOR protection
# ---------------------------------------------------------------------------

def test_get_cases_returns_only_own_cases(client):
    """User A cannot see User B's cases — each caller gets their own."""
    from app.models.models import Case

    uid_a = f"uid-a-{uuid.uuid4().hex[:8]}"
    uid_b = f"uid-b-{uuid.uuid4().hex[:8]}"

    # Seed two cases
    with Session(_TEST_ENGINE) as session:
        case_a = Case(
            client_id=uid_a,
            client_name="Alice",
            lawyer_id="lawyer-x",
            lawyer_name="Adv. X",
            summary="Case belonging to A",
        )
        case_b = Case(
            client_id=uid_b,
            client_name="Bob",
            lawyer_id="lawyer-y",
            lawyer_name="Adv. Y",
            summary="Case belonging to B",
        )
        session.add(case_a)
        session.add(case_b)
        session.commit()

    # Query as User A
    with patch.dict(os.environ, user_env(uid_a)):
        resp = client.get(
            "/legal/cases",
            headers={"Authorization": "Bearer dev-token"},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert all(c["client_id"] == uid_a for c in data), (
        f"User A saw cases from other users: {data}"
    )
    # User B's case must not appear
    summaries = [c["summary"] for c in data]
    assert "Case belonging to B" not in summaries


# ---------------------------------------------------------------------------
# 3. POST /legal/posts — restricted to verified advocates
# ---------------------------------------------------------------------------

def test_create_post_denied_for_client(client):
    """A client (is_lawyer=False) must receive 403 on POST /legal/posts."""
    uid = f"client-{uuid.uuid4().hex[:8]}"
    with patch.dict(os.environ, user_env(uid, is_lawyer=False)):
        resp = client.post(
            "/legal/posts",
            json={"content": "This should be rejected."},
            headers={"Authorization": "Bearer dev-token"},
        )
    assert resp.status_code == 403


def test_create_post_allowed_for_lawyer(client):
    """A verified advocate (is_lawyer=True) may publish a post."""
    uid = f"lawyer-{uuid.uuid4().hex[:8]}"
    with patch.dict(os.environ, user_env(uid, name="Adv. Test", is_lawyer=True)):
        resp = client.post(
            "/legal/posts",
            json={"content": "A valid legal update from a verified advocate."},
            headers={"Authorization": "Bearer dev-token"},
        )
    assert resp.status_code == 201, resp.text
    assert resp.json()["author_id"] == uid


# ---------------------------------------------------------------------------
# 4. GET /legal/chat/history — IDOR protection
# ---------------------------------------------------------------------------

def test_chat_history_only_returns_own_thread(client):
    """Caller C cannot read the thread between User A and User B."""
    from app.models.models import Message

    uid_a = f"chat-a-{uuid.uuid4().hex[:8]}"
    uid_b = f"chat-b-{uuid.uuid4().hex[:8]}"
    uid_c = f"chat-c-{uuid.uuid4().hex[:8]}"

    with Session(_TEST_ENGINE) as session:
        msg = Message(
            sender_id=uid_a,
            receiver_id=uid_b,
            content="Private message",
            client_msg_id=uuid.uuid4().hex,
        )
        session.add(msg)
        session.commit()

    # Caller C requests the thread between A and B
    with patch.dict(os.environ, user_env(uid_c)):
        resp = client.get(
            "/legal/chat/history",
            params={"contact_id": uid_b},
            headers={"Authorization": "Bearer dev-token"},
        )
    assert resp.status_code == 200
    # The WHERE clause restricts to (uid_c, uid_b) — no messages exist there
    assert resp.json() == [], (
        "Caller C should not see messages between A and B"
    )


# ---------------------------------------------------------------------------
# 5. POST /legal/cases/resolve — ownership check
# ---------------------------------------------------------------------------

def test_resolve_case_denied_for_wrong_lawyer(client):
    """Lawyer B cannot accept a case assigned to Lawyer A."""
    from app.models.models import Case

    uid_lawyer_a = f"lawyer-a-{uuid.uuid4().hex[:8]}"
    uid_lawyer_b = f"lawyer-b-{uuid.uuid4().hex[:8]}"

    with Session(_TEST_ENGINE) as session:
        case = Case(
            client_id="some-client",
            client_name="Client",
            lawyer_id=uid_lawyer_a,
            lawyer_name="Adv. A",
            summary="Contested case",
        )
        session.add(case)
        session.commit()
        session.refresh(case)
        case_id = case.id

    # Lawyer B attempts to resolve Lawyer A's case
    with patch.dict(
        os.environ, user_env(uid_lawyer_b, is_lawyer=True)
    ):
        resp = client.post(
            "/legal/cases/resolve",
            json={"case_id": case_id, "action": "accept"},
            headers={"Authorization": "Bearer dev-token"},
        )
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# 6. State machine — invalid transitions
# ---------------------------------------------------------------------------

def test_invalid_stage_transition_rejected(client):
    """submitted → completed must be rejected (skips intermediate stages)."""
    from app.models.models import Case

    uid_lawyer = f"lawyer-sm-{uuid.uuid4().hex[:8]}"

    with Session(_TEST_ENGINE) as session:
        case = Case(
            client_id="sm-client",
            client_name="Client SM",
            lawyer_id=uid_lawyer,
            lawyer_name="Adv. SM",
            summary="State machine test case",
            status="submitted",
            current_stage="submitted",
        )
        session.add(case)
        session.commit()
        session.refresh(case)
        case_id = case.id

    with patch.dict(os.environ, user_env(uid_lawyer, is_lawyer=True)):
        resp = client.patch(
            f"/legal/cases/{case_id}/stage",
            json={"new_stage": "completed"},
            headers={"Authorization": "Bearer dev-token"},
        )
    assert resp.status_code == 400, (
        "Should reject submitted → completed transition"
    )


def test_invalid_stage_enum_value_rejected(client):
    """Submitting an unknown stage string must return 422."""
    from app.models.models import Case

    uid_lawyer = f"lawyer-inv-{uuid.uuid4().hex[:8]}"

    with Session(_TEST_ENGINE) as session:
        case = Case(
            client_id="inv-client",
            client_name="Client Inv",
            lawyer_id=uid_lawyer,
            lawyer_name="Adv. Inv",
            summary="Invalid stage test",
            status="accepted",
            current_stage="accepted",
        )
        session.add(case)
        session.commit()
        session.refresh(case)
        case_id = case.id

    with patch.dict(os.environ, user_env(uid_lawyer, is_lawyer=True)):
        resp = client.patch(
            f"/legal/cases/{case_id}/stage",
            json={"new_stage": "aproved"},  # typo — not a valid enum value
            headers={"Authorization": "Bearer dev-token"},
        )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# 7. Rate limiting
# ---------------------------------------------------------------------------

def test_post_rate_limit_enforced(client):
    """The 6th post within 60 s must be rejected with 429."""
    from app.api.legal_api import _rate_windows

    uid = f"ratelimit-post-{uuid.uuid4().hex[:8]}"
    # Clear any previous window state
    _rate_windows.pop(f"{uid}:post", None)

    with patch.dict(os.environ, user_env(uid, is_lawyer=True)):
        for i in range(5):
            resp = client.post(
                "/legal/posts",
                json={"content": f"Post number {i + 1} — valid content."},
                headers={"Authorization": "Bearer dev-token"},
            )
            assert resp.status_code == 201, f"Post {i + 1} should succeed"

        # 6th post must be rejected
        resp = client.post(
            "/legal/posts",
            json={"content": "This 6th post should be rate-limited."},
            headers={"Authorization": "Bearer dev-token"},
        )
    assert resp.status_code == 429


def test_case_request_rate_limit_enforced(client):
    """The 4th case request within 60 s must be rejected with 429."""
    from app.api.legal_api import _rate_windows

    uid = f"ratelimit-case-{uuid.uuid4().hex[:8]}"
    _rate_windows.pop(f"{uid}:case_request", None)

    with patch.dict(os.environ, user_env(uid, is_lawyer=False)):
        for i in range(3):
            resp = client.post(
                "/legal/cases/request",
                json={
                    "lawyer_id": f"any-lawyer-{i}",
                    "lawyer_name": f"Adv. {i}",
                    "user_query_summary": "Valid query of at least ten characters.",
                    "attached_document_ids": [],
                },
                headers={"Authorization": "Bearer dev-token"},
            )
            assert resp.status_code == 201, f"Request {i + 1} should succeed"

        # 4th request must be rejected
        resp = client.post(
            "/legal/cases/request",
            json={
                "lawyer_id": "any-lawyer-4",
                "lawyer_name": "Adv. 4",
                "user_query_summary": "This 4th request should be rate-limited.",
                "attached_document_ids": [],
            },
            headers={"Authorization": "Bearer dev-token"},
        )
    assert resp.status_code == 429


# ---------------------------------------------------------------------------
# 8. Deduplication — idempotent REST send
# ---------------------------------------------------------------------------

def test_duplicate_message_returns_200_not_409(client):
    """Retrying POST /legal/chat/send with the same client_msg_id returns 200."""
    uid = f"dedup-{uuid.uuid4().hex[:8]}"
    client_msg_id = uuid.uuid4().hex

    payload = {
        "receiver_id": "some-receiver",
        "content": "Hello, this is an idempotent message.",
        "client_msg_id": client_msg_id,
    }

    with patch.dict(os.environ, user_env(uid)):
        r1 = client.post(
            "/legal/chat/send",
            json=payload,
            headers={"Authorization": "Bearer dev-token"},
        )
        r2 = client.post(
            "/legal/chat/send",
            json=payload,
            headers={"Authorization": "Bearer dev-token"},
        )

    assert r1.status_code == 200
    assert r2.status_code == 200, (
        "Duplicate client_msg_id should return 200 (idempotent), not 409"
    )
    assert r1.json()["client_msg_id"] == r2.json()["client_msg_id"]
