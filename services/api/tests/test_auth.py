from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.deps import get_user_repository
from app.core.security import hash_password
from app.main import create_app
from app.schemas.auth import UserCreate


class FakeUser:
    def __init__(
        self,
        email: str,
        full_name: str,
        hashed_password: str,
        is_active: bool = True,
    ) -> None:
        self.id = uuid4()
        self.email = email
        self.full_name = full_name
        self.hashed_password = hashed_password
        self.is_active = is_active
        self.is_superuser = False
        self.created_at = datetime.now(UTC)


class FakeUserRepository:
    def __init__(self) -> None:
        self.users: dict[str, FakeUser] = {}

    async def get_by_email(self, email: str) -> FakeUser | None:
        return self.users.get(email.lower())

    async def create(self, payload: UserCreate, hashed_password: str) -> FakeUser:
        user = FakeUser(
            email=payload.email.lower(),
            full_name=payload.full_name,
            hashed_password=hashed_password,
        )
        self.users[user.email] = user
        return user


def create_test_client(repository: FakeUserRepository) -> TestClient:
    app = create_app()

    async def override_user_repository():
        yield repository

    app.dependency_overrides[get_user_repository] = override_user_repository
    return TestClient(app)


def test_register_creates_user_and_returns_token() -> None:
    repository = FakeUserRepository()
    client = create_test_client(repository)

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "Analyst@example.com",
            "full_name": "Ada Analyst",
            "password": "correct-horse-battery",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["user"]["email"] == "analyst@example.com"
    assert "analyst@example.com" in repository.users


def test_register_rejects_duplicate_email() -> None:
    repository = FakeUserRepository()
    repository.users["analyst@example.com"] = FakeUser(
        email="analyst@example.com",
        full_name="Ada Analyst",
        hashed_password=hash_password("correct-horse-battery"),
    )
    client = create_test_client(repository)

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "analyst@example.com",
            "full_name": "Ada Analyst",
            "password": "correct-horse-battery",
        },
    )

    assert response.status_code == 409


def test_login_returns_access_token_for_valid_credentials() -> None:
    repository = FakeUserRepository()
    repository.users["analyst@example.com"] = FakeUser(
        email="analyst@example.com",
        full_name="Ada Analyst",
        hashed_password=hash_password("correct-horse-battery"),
    )
    client = create_test_client(repository)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "analyst@example.com", "password": "correct-horse-battery"},
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_login_rejects_invalid_credentials() -> None:
    repository = FakeUserRepository()
    repository.users["analyst@example.com"] = FakeUser(
        email="analyst@example.com",
        full_name="Ada Analyst",
        hashed_password=hash_password("correct-horse-battery"),
    )
    client = create_test_client(repository)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "analyst@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401


def test_me_returns_current_user() -> None:
    repository = FakeUserRepository()
    client = create_test_client(repository)

    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "analyst@example.com",
            "full_name": "Ada Analyst",
            "password": "correct-horse-battery",
        },
    )
    token = register_response.json()["access_token"]

    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["email"] == "analyst@example.com"

