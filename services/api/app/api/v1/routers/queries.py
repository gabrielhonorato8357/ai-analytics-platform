from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import Settings, get_settings
from app.db.postgres import get_session
from app.models.user import User
from app.schemas.query import (
    GeneratedSqlResponse,
    NaturalLanguageQueryRequest,
    QueryExecutionRequest,
    QueryExecutionResponse,
)
from app.services.query_execution import QueryValidationError, execute_readonly_query
from app.services.sql_generation import SqlGenerationUnavailableError, get_sql_generator

router = APIRouter(prefix="/queries", tags=["queries"])


@router.post("/generate", response_model=GeneratedSqlResponse)
async def generate_sql(
    payload: NaturalLanguageQueryRequest,
    settings: Annotated[Settings, Depends(get_settings)],
    _current_user: Annotated[User, Depends(get_current_user)],
) -> GeneratedSqlResponse:
    generator = get_sql_generator(settings)
    try:
        return await generator.generate(payload)
    except SqlGenerationUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


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

