from typing import Protocol
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.auth import UserCreate
from app.schemas.users import ManagedUserUpdate


class UserRepository(Protocol):
    async def list(self) -> list[User]:
        ...

    async def get_by_id(self, user_id: UUID) -> User | None:
        ...

    async def get_by_email(self, email: str) -> User | None:
        ...

    async def create(self, payload: UserCreate, hashed_password: str) -> User:
        ...

    async def update(self, user: User, payload: ManagedUserUpdate) -> User:
        ...


class SqlAlchemyUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(self) -> list[User]:
        result = await self.session.execute(select(User).order_by(User.created_at.desc()))
        return list(result.scalars().all())

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email.lower()))
        return result.scalar_one_or_none()

    async def create(self, payload: UserCreate, hashed_password: str) -> User:
        user = User(
            email=payload.email.lower(),
            full_name=payload.full_name,
            hashed_password=hashed_password,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(self, user: User, payload: ManagedUserUpdate) -> User:
        updates = payload.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(user, field, value)

        await self.session.commit()
        await self.session.refresh(user)
        return user
