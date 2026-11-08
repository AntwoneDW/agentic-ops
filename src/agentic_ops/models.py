# models.py
from typing import Literal

from pydantic import BaseModel


class IncidentAssessment(BaseModel):
    service: str
    severity: Literal["low", "medium", "high", "critical"]
    likely_layer: Literal[
        "application",
        "infrastructure",
        "database",
        "dependency",
        "unknown",
    ]
    next_action: str
    needs_more_evidence: bool