# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["Run"]


class Run(BaseModel):
    id: str
    """Unique identifier for the object."""

    arguments: Dict[str, object]
    """Arguments in this run for the task's input parameters."""

    created_at: datetime
    """Timestamp when the object was created."""

    finished_at: Optional[datetime] = None
    """Timestamp when the object was last updated."""

    result_json: Optional[str] = None
    """Execution result of the run. In JSON, matching the task's output schema."""

    task_id: str
    """ID of the task executed in this run."""
