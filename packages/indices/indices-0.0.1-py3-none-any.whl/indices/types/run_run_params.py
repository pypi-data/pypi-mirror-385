# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Required, TypedDict

__all__ = ["RunRunParams"]


class RunRunParams(TypedDict, total=False):
    task_id: Required[str]
    """ID of the task to execute."""

    arguments: Dict[str, object]
    """Arguments to pass to the task.

    Optional if the task does not require any arguments.
    """
