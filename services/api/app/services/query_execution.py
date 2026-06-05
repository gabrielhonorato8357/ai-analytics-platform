from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlglot import exp, parse, parse_one
from sqlglot.errors import ParseError

from app.schemas.query import QueryExecutionResponse


class QueryValidationError(ValueError):
    pass


def normalize_readonly_sql(sql: str) -> str:
    stripped_sql = sql.strip()
    if not stripped_sql:
        raise QueryValidationError("SQL query is required")

    try:
        statements = [statement for statement in parse(stripped_sql, read="postgres") if statement]
        expression = parse_one(stripped_sql, read="postgres")
    except ParseError as exc:
        raise QueryValidationError("SQL query could not be parsed") from exc

    if len(statements) != 1:
        raise QueryValidationError("Only one SQL statement can be executed at a time")

    if not isinstance(expression, exp.Select):
        raise QueryValidationError("Only read-only SELECT queries are allowed")

    return expression.sql(dialect="postgres")


async def execute_readonly_query(
    session: AsyncSession,
    sql: str,
    requested_limit: int | None,
    max_rows: int,
) -> QueryExecutionResponse:
    normalized_sql = normalize_readonly_sql(sql)
    limit = min(requested_limit or max_rows, max_rows)
    wrapped_sql = f"SELECT * FROM ({normalized_sql}) AS analytics_query LIMIT :limit"

    result = await session.execute(text(wrapped_sql), {"limit": limit})
    rows = [dict(row) for row in result.mappings().all()]
    columns = list(rows[0].keys()) if rows else []

    return QueryExecutionResponse(
        columns=columns,
        rows=rows,
        row_count=len(rows),
        executed_sql=normalized_sql,
    )
