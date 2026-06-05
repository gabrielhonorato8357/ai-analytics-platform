from typing import Protocol
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.saved_report import SavedReport
from app.schemas.reports import SavedReportCreate


class SavedReportRepository(Protocol):
    async def list_for_user(self, owner_user_id: UUID) -> list[SavedReport]:
        ...

    async def get_for_user(self, report_id: UUID, owner_user_id: UUID) -> SavedReport | None:
        ...

    async def create(self, owner_user_id: UUID, payload: SavedReportCreate) -> SavedReport:
        ...

    async def delete_for_user(self, report_id: UUID, owner_user_id: UUID) -> bool:
        ...


class SqlAlchemySavedReportRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_for_user(self, owner_user_id: UUID) -> list[SavedReport]:
        result = await self.session.execute(
            select(SavedReport)
            .where(SavedReport.owner_user_id == owner_user_id)
            .order_by(SavedReport.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_for_user(self, report_id: UUID, owner_user_id: UUID) -> SavedReport | None:
        result = await self.session.execute(
            select(SavedReport).where(
                SavedReport.id == report_id,
                SavedReport.owner_user_id == owner_user_id,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, owner_user_id: UUID, payload: SavedReportCreate) -> SavedReport:
        report = SavedReport(owner_user_id=owner_user_id, **payload.model_dump(mode="json"))
        self.session.add(report)
        await self.session.commit()
        await self.session.refresh(report)
        return report

    async def delete_for_user(self, report_id: UUID, owner_user_id: UUID) -> bool:
        result = await self.session.execute(
            delete(SavedReport).where(
                SavedReport.id == report_id,
                SavedReport.owner_user_id == owner_user_id,
            )
        )
        await self.session.commit()
        return bool(result.rowcount)

