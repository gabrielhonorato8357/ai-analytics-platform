from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_audit_log_repository, get_current_superuser
from app.models.user import User
from app.repositories.audit_logs import AuditLogRepository
from app.schemas.audit import AuditLogRead

router = APIRouter(prefix="/audit-logs", tags=["audit logs"])


@router.get("", response_model=list[AuditLogRead])
async def list_audit_logs(
    _current_user: Annotated[User, Depends(get_current_superuser)],
    audit_logs: Annotated[AuditLogRepository, Depends(get_audit_log_repository)],
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> list[AuditLogRead]:
    recent_logs = await audit_logs.list_recent(limit=limit)
    return [AuditLogRead.model_validate(audit_log) for audit_log in recent_logs]

