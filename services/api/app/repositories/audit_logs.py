from typing import Any, Protocol
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


class AuditLogRepository(Protocol):
    async def list_recent(self, limit: int = 100) -> list[AuditLog]:
        ...

    async def create(
        self,
        *,
        actor_user_id: UUID | None,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        event_metadata: dict[str, Any] | None = None,
    ) -> AuditLog:
        ...


class SqlAlchemyAuditLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_recent(self, limit: int = 100) -> list[AuditLog]:
        result = await self.session.execute(
            select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def create(
        self,
        *,
        actor_user_id: UUID | None,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        event_metadata: dict[str, Any] | None = None,
    ) -> AuditLog:
        audit_log = AuditLog(
            actor_user_id=actor_user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            event_metadata=event_metadata or {},
        )
        self.session.add(audit_log)
        await self.session.commit()
        await self.session.refresh(audit_log)
        return audit_log

