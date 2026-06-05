from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.api.deps import get_current_user, get_report_repository
from app.main import create_app
from app.schemas.reports import SavedReportCreate


class FakeUser:
    def __init__(self) -> None:
        self.id = uuid4()
        self.email = "analyst@example.com"
        self.full_name = "Ada Analyst"
        self.hashed_password = "unused"
        self.is_active = True
        self.is_superuser = False
        self.created_at = datetime.now(UTC)


class FakeReport:
    def __init__(self, owner_user_id: UUID, payload: SavedReportCreate) -> None:
        self.id = uuid4()
        self.owner_user_id = owner_user_id
        self.title = payload.title
        self.description = payload.description
        self.sql = payload.sql
        self.visualization_type = payload.visualization_type
        self.chart_config = payload.chart_config
        self.created_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)


class FakeReportRepository:
    def __init__(self) -> None:
        self.reports: dict[UUID, FakeReport] = {}

    async def list_for_user(self, owner_user_id: UUID) -> list[FakeReport]:
        return [report for report in self.reports.values() if report.owner_user_id == owner_user_id]

    async def get_for_user(self, report_id: UUID, owner_user_id: UUID) -> FakeReport | None:
        report = self.reports.get(report_id)
        if report is None or report.owner_user_id != owner_user_id:
            return None
        return report

    async def create(self, owner_user_id: UUID, payload: SavedReportCreate) -> FakeReport:
        report = FakeReport(owner_user_id, payload)
        self.reports[report.id] = report
        return report

    async def delete_for_user(self, report_id: UUID, owner_user_id: UUID) -> bool:
        report = await self.get_for_user(report_id, owner_user_id)
        if report is None:
            return False

        del self.reports[report_id]
        return True


def create_test_client(user: FakeUser, repository: FakeReportRepository) -> TestClient:
    app = create_app()

    async def override_current_user():
        return user

    async def override_report_repository():
        yield repository

    app.dependency_overrides[get_current_user] = override_current_user
    app.dependency_overrides[get_report_repository] = override_report_repository
    return TestClient(app)


def test_create_report_returns_saved_report() -> None:
    user = FakeUser()
    repository = FakeReportRepository()
    client = create_test_client(user, repository)

    response = client.post(
        "/api/v1/reports",
        json={
            "title": "Revenue by segment",
            "description": "Quarterly revenue report",
            "sql": "select segment, revenue from revenue_by_segment",
            "visualization_type": "bar",
            "chart_config": {"xKey": "segment", "yKey": "revenue"},
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Revenue by segment"
    assert body["owner_user_id"] == str(user.id)


def test_list_reports_returns_only_current_users_reports() -> None:
    user = FakeUser()
    other_user = FakeUser()
    repository = FakeReportRepository()
    repository.reports[uuid4()] = FakeReport(
        user.id,
        SavedReportCreate(
            title="Revenue",
            sql="select segment, revenue from revenue_by_segment",
            visualization_type="bar",
        ),
    )
    repository.reports[uuid4()] = FakeReport(
        other_user.id,
        SavedReportCreate(title="Private", sql="select * from private_metrics"),
    )
    client = create_test_client(user, repository)

    response = client.get("/api/v1/reports")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Revenue"


def test_delete_report_removes_owned_report() -> None:
    user = FakeUser()
    repository = FakeReportRepository()
    report = FakeReport(
        user.id,
        SavedReportCreate(title="Revenue", sql="select segment from revenue_by_segment"),
    )
    repository.reports[report.id] = report
    client = create_test_client(user, repository)

    response = client.delete(f"/api/v1/reports/{report.id}")

    assert response.status_code == 204
    assert report.id not in repository.reports


def test_get_report_rejects_report_from_another_user() -> None:
    user = FakeUser()
    other_user = FakeUser()
    repository = FakeReportRepository()
    report = FakeReport(
        other_user.id,
        SavedReportCreate(title="Private", sql="select * from private_metrics"),
    )
    repository.reports[report.id] = report
    client = create_test_client(user, repository)

    response = client.get(f"/api/v1/reports/{report.id}")

    assert response.status_code == 404

