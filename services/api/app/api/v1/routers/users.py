from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import (
    get_audit_log_repository,
    get_current_superuser,
    get_user_repository,
)
from app.models.user import User
from app.repositories.audit_logs import AuditLogRepository
from app.repositories.users import UserRepository
from app.schemas.users import ManagedUserRead, ManagedUserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[ManagedUserRead])
async def list_users(
    _current_user: Annotated[User, Depends(get_current_superuser)],
    users: Annotated[UserRepository, Depends(get_user_repository)],
) -> list[ManagedUserRead]:
    managed_users = await users.list()
    return [ManagedUserRead.model_validate(user) for user in managed_users]


@router.patch("/{user_id}", response_model=ManagedUserRead)
async def update_user(
    user_id: UUID,
    payload: ManagedUserUpdate,
    current_user: Annotated[User, Depends(get_current_superuser)],
    users: Annotated[UserRepository, Depends(get_user_repository)],
    audit_logs: Annotated[AuditLogRepository, Depends(get_audit_log_repository)],
) -> ManagedUserRead:
    user = await users.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    updated_user = await users.update(user, payload)
    await audit_logs.create(
        actor_user_id=current_user.id,
        action="user.updated",
        resource_type="user",
        resource_id=str(updated_user.id),
        event_metadata=payload.model_dump(exclude_unset=True),
    )
    return ManagedUserRead.model_validate(updated_user)

