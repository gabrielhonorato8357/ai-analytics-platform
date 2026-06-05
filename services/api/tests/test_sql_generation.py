import json
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_audit_log_repository, get_current_user
from app.core.config import Settings, get_settings
from app.main import create_app
from app.schemas.query import NaturalLanguageQueryRequest
from app.services.sql_generation import (
    LocalSqlGenerator,
    SqlGenerationError,
    _parse_openai_json_response,
)


class FakeUser:
    def __init__(self) -> None:
        self.id = uuid4()
        self.email = "analyst@example.com"
        self.full_name = "Ada Analyst"
        self.hashed_password = "unused"
        self.is_active = True
        self.is_superuser = False
        self.created_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)


class FakeAuditLogRepository:
    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    async def create(self, **payload: Any) -> dict[str, Any]:
        self.events.append(payload)
        return payload


def create_test_client(settings: Settings, audit_logs: FakeAuditLogRepository) -> TestClient:
    app = create_app()
    user = FakeUser()

    async def override_current_user() -> FakeUser:
        return user

    async def override_audit_log_repository():
        yield audit_logs

    app.dependency_overrides[get_current_user] = override_current_user
    app.dependency_overrides[get_audit_log_repository] = override_audit_log_repository
    app.dependency_overrides[get_settings] = lambda: settings
    return TestClient(app)


@pytest.mark.asyncio
async def test_local_sql_generator_returns_valid_readonly_sql() -> None:
    generator = LocalSqlGenerator()

    response = await generator.generate(
        NaturalLanguageQueryRequest(question="Show revenue by customer segment")
    )

    assert response.sql == "SELECT segment, revenue FROM revenue_by_segment"
    assert response.provider == "local"


def test_parse_openai_json_response_reads_output_text() -> None:
    payload = {
        "output_text": json.dumps(
            {
                "sql": "SELECT segment FROM revenue_by_segment",
                "confidence": 0.9,
                "assumptions": [],
            }
        )
    }

    assert _parse_openai_json_response(payload)["sql"] == "SELECT segment FROM revenue_by_segment"


def test_parse_openai_json_response_requires_text() -> None:
    try:
        _parse_openai_json_response({"output": []})
    except SqlGenerationError as exc:
        assert "structured output text" in str(exc)
    else:
        raise AssertionError("Expected SqlGenerationError")


def test_generate_sql_local_provider_writes_audit_event() -> None:
    audit_logs = FakeAuditLogRepository()
    client = create_test_client(
        Settings(_env_file=None, AI_SQL_PROVIDER="local"),
        audit_logs,
    )

    response = client.post(
        "/api/v1/queries/generate",
        json={"question": "Show revenue by customer segment"},
    )

    assert response.status_code == 200
    assert response.json()["provider"] == "local"
    assert audit_logs.events[0]["action"] == "query.sql_generated"


def test_generate_sql_disabled_provider_writes_audit_event() -> None:
    audit_logs = FakeAuditLogRepository()
    client = create_test_client(
        Settings(_env_file=None, AI_SQL_PROVIDER="disabled"),
        audit_logs,
    )

    response = client.post(
        "/api/v1/queries/generate",
        json={"question": "Show revenue by customer segment"},
    )

    assert response.status_code == 503
    assert audit_logs.events[0]["action"] == "query.sql_generation_unavailable"
