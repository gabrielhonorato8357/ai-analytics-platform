from unittest.mock import patch

import pytest

from app.cli.bootstrap_admin import bootstrap_admin
from app.core.config import Settings, get_settings


@pytest.mark.asyncio
async def test_bootstrap_admin_requires_email_and_password() -> None:
    with pytest.raises(RuntimeError, match="FIRST_SUPERUSER_EMAIL"):
        with patch("app.cli.bootstrap_admin.get_settings", return_value=Settings(_env_file=None)):
            await bootstrap_admin()


@pytest.mark.asyncio
async def test_bootstrap_admin_rejects_short_password() -> None:
    settings = Settings(
        _env_file=None,
        FIRST_SUPERUSER_EMAIL="admin@example.com",
        FIRST_SUPERUSER_PASSWORD="short",
    )

    with pytest.raises(RuntimeError, match="at least 12"):
        with patch("app.cli.bootstrap_admin.get_settings", return_value=settings):
            await bootstrap_admin()


def test_get_settings_cache_can_be_cleared_for_tests() -> None:
    get_settings.cache_clear()
    assert get_settings()
