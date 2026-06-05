from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_audit_log_repository, get_current_user
from app.core.config import Settings, get_settings
from app.db.postgres import get_session
from app.models.user import User
from app.repositories.audit_logs import AuditLogRepository
from app.schemas.query import (
    GeneratedSqlResponse,
    NaturalLanguageQueryRequest,
    QueryExecutionRequest,
    QueryExecutionResponse,
)
from app.services.query_execution import QueryValidationError, execute_readonly_query
from app.services.sql_generation import (
    SqlGenerationError,
    SqlGenerationUnavailableError,
    get_sql_generator,
)

router = APIRouter(prefix="/queries", tags=["queries"])


@router.post("/generate", response_model=GeneratedSqlResponse)
async def generate_sql(
    payload: NaturalLanguageQueryRequest,
    settings: Annotated[Settings, Depends(get_settings)],
    current_user: Annotated[User, Depends(get_current_user)],
    audit_logs: Annotated[AuditLogRepository, Depends(get_audit_log_repository)],
) -> GeneratedSqlResponse:
    generator = get_sql_generator(settings)
    try:
        response = await generator.generate(payload)
    except SqlGenerationUnavailableError as exc:
        await audit_logs.create(
            actor_user_id=current_user.id,
            action="query.sql_generation_unavailable",
            resource_type="query",
            event_metadata={"provider": settings.ai_sql_provider},
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except SqlGenerationError as exc:
        await audit_logs.create(
            actor_user_id=current_user.id,
            action="query.sql_generation_failed",
            resource_type="query",
            event_metadata={"provider": settings.ai_sql_provider},
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    await audit_logs.create(
        actor_user_id=current_user.id,
        action="query.sql_generated",
        resource_type="query",
        event_metadata={"provider": response.provider, "confidence": response.confidence},
    )
    return response


@router.post("/execute", response_model=QueryExecutionResponse)
async def execute_query(
    payload: QueryExecutionRequest,
    settings: Annotated[Settings, Depends(get_settings)],
    _current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> QueryExecutionResponse:
    try:
        return await execute_readonly_query(
            session=session,
            sql=payload.sql,
            requested_limit=payload.limit,
            max_rows=settings.max_query_rows,
        )
    except QueryValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
