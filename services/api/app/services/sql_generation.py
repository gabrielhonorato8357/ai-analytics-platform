from dataclasses import dataclass

from app.core.config import Settings
from app.schemas.query import GeneratedSqlResponse, NaturalLanguageQueryRequest


class SqlGenerationUnavailableError(Exception):
    pass


@dataclass(frozen=True)
class SqlGenerator:
    provider: str

    async def generate(self, request: NaturalLanguageQueryRequest) -> GeneratedSqlResponse:
        raise SqlGenerationUnavailableError(
            f"SQL generation provider '{self.provider}' is not configured"
        )


def get_sql_generator(settings: Settings) -> SqlGenerator:
    return SqlGenerator(provider=settings.ai_sql_provider)

