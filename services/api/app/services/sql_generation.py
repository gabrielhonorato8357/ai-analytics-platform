import json
from abc import ABC, abstractmethod

import httpx

from app.core.config import Settings
from app.schemas.query import GeneratedSqlResponse, NaturalLanguageQueryRequest
from app.services.query_execution import QueryValidationError, normalize_readonly_sql


class SqlGenerationUnavailableError(Exception):
    pass


class SqlGenerationError(Exception):
    pass


class SqlGenerator(ABC):
    provider: str

    @abstractmethod
    async def generate(self, request: NaturalLanguageQueryRequest) -> GeneratedSqlResponse:
        raise NotImplementedError


class DisabledSqlGenerator(SqlGenerator):
    provider = "disabled"

    async def generate(self, request: NaturalLanguageQueryRequest) -> GeneratedSqlResponse:
        raise SqlGenerationUnavailableError(
            f"SQL generation provider '{self.provider}' is not configured"
        )


class LocalSqlGenerator(SqlGenerator):
    provider = "local"

    async def generate(self, request: NaturalLanguageQueryRequest) -> GeneratedSqlResponse:
        question = request.question.lower()

        if "revenue" in question and "segment" in question:
            sql = "SELECT segment, revenue FROM revenue_by_segment"
            assumptions = ["Using revenue_by_segment as the curated analytics source."]
        elif "user" in question:
            sql = "SELECT id, email, full_name, is_active, created_at FROM users"
            assumptions = ["Using the users table because the question references users."]
        else:
            sql = "SELECT 1 AS value"
            assumptions = [
                "No matching schema hint was found, so a safe placeholder query was used."
            ]

        return GeneratedSqlResponse(
            sql=normalize_readonly_sql(sql),
            confidence=0.55,
            assumptions=assumptions,
            provider=self.provider,
        )


class OpenAISqlGenerator(SqlGenerator):
    provider = "openai"

    def __init__(self, settings: Settings) -> None:
        if not settings.openai_api_key:
            raise SqlGenerationUnavailableError("OPENAI_API_KEY is required for AI SQL generation")

        self.settings = settings

    async def generate(self, request: NaturalLanguageQueryRequest) -> GeneratedSqlResponse:
        payload = {
            "model": self.settings.openai_model,
            "input": [
                {
                    "role": "system",
                    "content": (
                        "Generate one read-only PostgreSQL SELECT query for an analytics platform. "
                        "Return JSON only. Do not include INSERT, UPDATE, DELETE, DDL, multiple "
                        "statements, comments, or markdown."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Question: {request.question}\n\n"
                        "Schema context:\n"
                        f"{request.schema_context or 'No schema context provided.'}"
                    ),
                },
            ],
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "generated_sql",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "sql": {"type": "string"},
                            "confidence": {"type": "number"},
                            "assumptions": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                        "required": ["sql", "confidence", "assumptions"],
                    },
                }
            },
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.settings.openai_base_url.rstrip('/')}/responses",
                headers={
                    "Authorization": f"Bearer {self.settings.openai_api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

        if response.status_code >= 400:
            raise SqlGenerationError("OpenAI SQL generation request failed")

        parsed = _parse_openai_json_response(response.json())
        try:
            normalized_sql = normalize_readonly_sql(parsed["sql"])
        except QueryValidationError as exc:
            raise SqlGenerationError("Generated SQL failed read-only validation") from exc

        return GeneratedSqlResponse(
            sql=normalized_sql,
            confidence=float(parsed["confidence"]),
            assumptions=list(parsed["assumptions"]),
            provider=f"openai:{self.settings.openai_model}",
        )


def _parse_openai_json_response(payload: dict) -> dict:
    output_text = payload.get("output_text")
    if isinstance(output_text, str):
        return json.loads(output_text)

    for item in payload.get("output", []):
        for content in item.get("content", []):
            text = content.get("text")
            if isinstance(text, str):
                return json.loads(text)

    raise SqlGenerationError("OpenAI response did not include structured output text")


def get_sql_generator(settings: Settings) -> SqlGenerator:
    provider = settings.ai_sql_provider.lower()
    if provider == "local":
        return LocalSqlGenerator()
    if provider == "openai":
        return OpenAISqlGenerator(settings)
    return DisabledSqlGenerator()
