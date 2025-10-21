# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["Task", "FailureInfo"]


class FailureInfo(BaseModel):
    category: str
    """Primary failure category"""

    message: str
    """Summary of the failure cause"""


class Task(BaseModel):
    id: str
    """Unique identifier for the object."""

    created_at: datetime
    """Timestamp when the object was created."""

    current_state: Literal["not_ready", "waiting_for_manual_completion", "ready", "failed"]
    """Current state of the task, in particular whether it is ready to use."""

    display_name: str
    """Short title shown in the dashboard. Informational only."""

    input_schema: str
    """Task input parameters in the form of a JSON schema."""

    is_fully_autonomous: bool
    """If true, the server will run the browser task autonomously."""

    output_schema: str
    """Task output in the form of a JSON schema."""

    task: str
    """Detailed explanation of the task to be performed."""

    updated_at: datetime
    """Timestamp when the object was last updated."""

    website: str
    """The website to perform the task on."""

    failure_info: Optional[FailureInfo] = None
    """Information about why a task failed, for user display."""
