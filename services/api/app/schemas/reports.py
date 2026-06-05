from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class VisualizationType(StrEnum):
    table = "table"
    bar = "bar"
    line = "line"


class SavedReportCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2_000)
    sql: str = Field(min_length=1, max_length=20_000)
    visualization_type: VisualizationType = VisualizationType.table
    chart_config: dict[str, Any] = Field(default_factory=dict)


class SavedReportRead(BaseModel):
    id: UUID
    owner_user_id: UUID
    title: str
    description: str | None
    sql: str
    visualization_type: VisualizationType
    chart_config: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

