from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.api.deps import get_audit_log_repository, get_current_user, get_user_repository
from app.main import create_app
from app.schemas.users import ManagedUserUpdate


class FakeUser:
    def __init__(
        self,
        email: str = "admin@example.com",
        is_superuser: bool = True,
        is_active: bool = True,
    ) -> None:
        self.id = uuid4()
        self.email = email
        self.full_name = "Ada Admin"
        self.hashed_password = "unused"
        self.is_active = is_active
        self.is_superuser = is_superuser
        self.created_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)


class FakeUserRepository:
    def __init__(self, users: list[FakeUser]) -> None:
        self.users = {user.id: user for user in users}

    async def list(self) -> list[FakeUser]:
        return list(self.users.values())

    async def get_by_id(self, user_id: UUID) -> FakeUser | None:
        return self.users.get(user_id)

    async def get_by_email(self, email: str) -> FakeUser | None:
        return next((user for user in self.users.values() if user.email == email), None)

    async def update(self, user: FakeUser, payload: ManagedUserUpdate) -> FakeUser:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(user, field, value)

        user.updated_at = datetime.now(UTC)
        return user


class FakeAuditLogRepository:
    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    async def create(self, **payload: Any) -> dict[str, Any]:
        self.events.append(payload)
        return payload


def create_test_client(
    current_user: FakeUser,
    user_repository: FakeUserRepository,
    audit_log_repository: FakeAuditLogRepository,
) -> TestClient:
    app = create_app()

    async def override_current_user() -> FakeUser:
        return current_user

    async def override_user_repository():
        yield user_repository

    async def override_audit_log_repository():
        yield audit_log_repository

    app.dependency_overrides[get_current_user] = override_current_user
    app.dependency_overrides[get_user_repository] = override_user_repository
    app.dependency_overrides[get_audit_log_repository] = override_audit_log_repository
    return TestClient(app)


def test_list_users_requires_superuser() -> None:
    user = FakeUser(is_superuser=False)
    client = create_test_client(user, FakeUserRepository([user]), FakeAuditLogRepository())

    response = client.get("/api/v1/users")

    assert response.status_code == 403


def test_superuser_can_list_users() -> None:
    admin = FakeUser()
    analyst = FakeUser(email="analyst@example.com", is_superuser=False)
    client = create_test_client(
        admin,
        FakeUserRepository([admin, analyst]),
        FakeAuditLogRepository(),
    )

    response = client.get("/api/v1/users")

    assert response.status_code == 200
    assert {user["email"] for user in response.json()} == {
        "admin@example.com",
        "analyst@example.com",
    }


def test_superuser_can_update_user_and_write_audit_log() -> None:
    admin = FakeUser()
    analyst = FakeUser(email="analyst@example.com", is_superuser=False)
    audit_logs = FakeAuditLogRepository()
    client = create_test_client(admin, FakeUserRepository([admin, analyst]), audit_logs)

    response = client.patch(
        f"/api/v1/users/{analyst.id}",
        json={"full_name": "Grace Analyst", "is_active": False},
    )

    assert response.status_code == 200
    assert response.json()["full_name"] == "Grace Analyst"
    assert response.json()["is_active"] is False
    assert audit_logs.events[0]["action"] == "user.updated"
    assert audit_logs.events[0]["resource_id"] == str(analyst.id)
