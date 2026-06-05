from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class AuditLogRead(BaseModel):
    id: UUID
    actor_user_id: UUID | None
    action: str
    resource_type: str
    resource_id: str | None
    event_metadata: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}

