import pytest

from app.services.query_execution import (
    QueryValidationError,
    execute_readonly_query,
    normalize_readonly_sql,
)


class FakeMappings:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.rows = rows

    def all(self) -> list[dict[str, object]]:
        return self.rows


class FakeResult:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.rows = rows

    def mappings(self) -> FakeMappings:
        return FakeMappings(self.rows)


class FakeSession:
    def __init__(self) -> None:
        self.executed_statement = ""
        self.executed_params: dict[str, object] = {}

    async def execute(self, statement, params: dict[str, object]):
        self.executed_statement = str(statement)
        self.executed_params = params
        return FakeResult([{"segment": "enterprise", "revenue": 125000}])


def test_normalize_readonly_sql_accepts_select() -> None:
    assert normalize_readonly_sql("select id, email from users").startswith("SELECT")


@pytest.mark.parametrize(
    "sql",
    [
        "update users set is_active = false",
        "delete from users",
        "select * from users; select * from audit_logs",
    ],
)
def test_normalize_readonly_sql_rejects_unsafe_statements(sql: str) -> None:
    with pytest.raises(QueryValidationError):
        normalize_readonly_sql(sql)


@pytest.mark.asyncio
async def test_execute_readonly_query_wraps_query_with_limit() -> None:
    session = FakeSession()

    response = await execute_readonly_query(
        session=session,
        sql="select segment, revenue from revenue_by_segment",
        requested_limit=50,
        max_rows=500,
    )

    assert response.columns == ["segment", "revenue"]
    assert response.row_count == 1
    assert session.executed_params == {"limit": 50}
    assert "AS analytics_query LIMIT :limit" in session.executed_statement


@pytest.mark.asyncio
async def test_execute_readonly_query_caps_limit_to_max_rows() -> None:
    session = FakeSession()

    await execute_readonly_query(
        session=session,
        sql="select segment from revenue_by_segment",
        requested_limit=2_000,
        max_rows=500,
    )

    assert session.executed_params == {"limit": 500}

