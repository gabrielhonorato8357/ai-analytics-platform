from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.api.deps import get_current_user, get_report_repository
from app.models.user import User
from app.repositories.reports import SavedReportRepository
from app.schemas.reports import SavedReportCreate, SavedReportRead

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("", response_model=list[SavedReportRead])
async def list_reports(
    current_user: Annotated[User, Depends(get_current_user)],
    reports: Annotated[SavedReportRepository, Depends(get_report_repository)],
) -> list[SavedReportRead]:
    user_reports = await reports.list_for_user(current_user.id)
    return [SavedReportRead.model_validate(report) for report in user_reports]


@router.post("", response_model=SavedReportRead, status_code=status.HTTP_201_CREATED)
async def create_report(
    payload: SavedReportCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    reports: Annotated[SavedReportRepository, Depends(get_report_repository)],
) -> SavedReportRead:
    report = await reports.create(current_user.id, payload)
    return SavedReportRead.model_validate(report)


@router.get("/{report_id}", response_model=SavedReportRead)
async def get_report(
    report_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    reports: Annotated[SavedReportRepository, Depends(get_report_repository)],
) -> SavedReportRead:
    report = await reports.get_for_user(report_id, current_user.id)
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    return SavedReportRead.model_validate(report)


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    reports: Annotated[SavedReportRepository, Depends(get_report_repository)],
) -> Response:
    deleted = await reports.delete_for_user(report_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    return Response(status_code=status.HTTP_204_NO_CONTENT)

