from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.deps import get_audit_log_repository, get_current_user
from app.main import create_app


class FakeUser:
    def __init__(self, is_superuser: bool = True) -> None:
        self.id = uuid4()
        self.email = "admin@example.com"
        self.full_name = "Ada Admin"
        self.hashed_password = "unused"
        self.is_active = True
        self.is_superuser = is_superuser
        self.created_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)


class FakeAuditLog:
    def __init__(self, actor_user_id) -> None:
        self.id = uuid4()
        self.actor_user_id = actor_user_id
        self.action = "user.updated"
        self.resource_type = "user"
        self.resource_id = str(uuid4())
        self.event_metadata = {"is_active": False}
        self.created_at = datetime.now(UTC)


class FakeAuditLogRepository:
    def __init__(self, logs: list[FakeAuditLog]) -> None:
        self.logs = logs
        self.limit = 0

    async def list_recent(self, limit: int = 100) -> list[FakeAuditLog]:
        self.limit = limit
        return self.logs[:limit]


def create_test_client(user: FakeUser, repository: FakeAuditLogRepository) -> TestClient:
    app = create_app()

    async def override_current_user() -> FakeUser:
        return user

    async def override_audit_log_repository():
        yield repository

    app.dependency_overrides[get_current_user] = override_current_user
    app.dependency_overrides[get_audit_log_repository] = override_audit_log_repository
    return TestClient(app)


def test_list_audit_logs_requires_superuser() -> None:
    user = FakeUser(is_superuser=False)
    client = create_test_client(user, FakeAuditLogRepository([]))

    response = client.get("/api/v1/audit-logs")

    assert response.status_code == 403


def test_superuser_can_list_audit_logs() -> None:
    user = FakeUser()
    repository = FakeAuditLogRepository([FakeAuditLog(user.id)])
    client = create_test_client(user, repository)

    response = client.get("/api/v1/audit-logs?limit=25")

    assert response.status_code == 200
    assert response.json()[0]["action"] == "user.updated"
    assert repository.limit == 25

