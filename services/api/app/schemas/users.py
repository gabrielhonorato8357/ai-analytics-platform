from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, model_validator


class ManagedUserRead(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ManagedUserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    is_active: bool | None = None
    is_superuser: bool | None = None

    @model_validator(mode="after")
    def require_update(self) -> "ManagedUserUpdate":
        if self.full_name is None and self.is_active is None and self.is_superuser is None:
            raise ValueError("At least one user field must be provided")

        return self

