# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["TaskCreateParams"]


class TaskCreateParams(TypedDict, total=False):
    display_name: Required[str]
    """Short title shown in the dashboard.

    Informational only; not used to generate the task.
    """

    input_schema: Required[str]
    """Task input parameters in the form of a JSON schema."""

    output_schema: Required[str]
    """Task output in the form of a JSON schema."""

    task: Required[str]
    """Detailed explanation of the task to be performed."""

    website: Required[str]
    """The website to perform the task on."""

    is_fully_autonomous: bool
    """If true, the server will run the browser task autonomously.

    If false, the user must complete the task manually in a spawned browser.
    """
