from typing import Any

from pydantic import BaseModel, Field


class NaturalLanguageQueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2_000)
    schema_context: str | None = Field(default=None, max_length=10_000)


class GeneratedSqlResponse(BaseModel):
    sql: str
    confidence: float = Field(ge=0, le=1)
    assumptions: list[str] = Field(default_factory=list)
    provider: str


class QueryExecutionRequest(BaseModel):
    sql: str = Field(min_length=1, max_length=20_000)
    limit: int | None = Field(default=None, ge=1, le=5_000)


class QueryExecutionResponse(BaseModel):
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int
    executed_sql: str

