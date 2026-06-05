from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.security import decode_access_token
from app.db.postgres import get_session
from app.models.user import User
from app.repositories.reports import SavedReportRepository, SqlAlchemySavedReportRepository
from app.repositories.users import SqlAlchemyUserRepository, UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AsyncGenerator[UserRepository, None]:
    yield SqlAlchemyUserRepository(session)


async def get_report_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AsyncGenerator[SavedReportRepository, None]:
    yield SqlAlchemySavedReportRepository(session)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    settings: Annotated[Settings, Depends(get_settings)],
    users: Annotated[UserRepository, Depends(get_user_repository)],
) -> User:
    email = decode_access_token(token, settings)
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await users.get_by_email(email)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
