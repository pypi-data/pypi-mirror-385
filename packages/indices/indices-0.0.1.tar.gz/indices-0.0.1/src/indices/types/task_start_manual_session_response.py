# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["TaskStartManualSessionResponse"]


class TaskStartManualSessionResponse(BaseModel):
    iframe_url: str
    """URL to embed in an iframe to control the browser."""

    session_id: str
    """Opaque identifier for the spawned browser session."""
