import asyncio

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.postgres import async_session_factory
from app.models.user import User
from app.repositories.users import SqlAlchemyUserRepository
from app.schemas.auth import UserCreate


async def bootstrap_admin() -> None:
    settings = get_settings()
    if not settings.first_superuser_email or not settings.first_superuser_password:
        raise RuntimeError(
            "FIRST_SUPERUSER_EMAIL and FIRST_SUPERUSER_PASSWORD are required to bootstrap an admin"
        )

    if len(settings.first_superuser_password) < 12:
        raise RuntimeError("FIRST_SUPERUSER_PASSWORD must be at least 12 characters")

    async with async_session_factory() as session:
        users = SqlAlchemyUserRepository(session)
        existing_user = await users.get_by_email(settings.first_superuser_email)
        if existing_user is not None:
            existing_user.is_active = True
            existing_user.is_superuser = True
            await session.commit()
            print(f"Updated existing superuser: {existing_user.email}")
            return

        payload = UserCreate(
            email=settings.first_superuser_email,
            full_name=settings.first_superuser_name,
            password=settings.first_superuser_password,
        )
        user = User(
            email=payload.email.lower(),
            full_name=payload.full_name,
            hashed_password=hash_password(payload.password),
            is_active=True,
            is_superuser=True,
        )
        session.add(user)
        await session.commit()
        print(f"Created superuser: {user.email}")


def main() -> None:
    asyncio.run(bootstrap_admin())


if __name__ == "__main__":
    main()

