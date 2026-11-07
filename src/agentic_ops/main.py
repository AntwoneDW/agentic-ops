import os
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel


load_dotenv()

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"]
)

model = os.getenv("OPENAI_MODEL", "gpt-6-luna")


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


response = client.responses.parse(
    model=model,
    instructions=(
        "You are the reasoning component of an AI operations system. "
        "Assess incidents conservatively. "
        "Do not invent evidence that was not provided."
    ),
    input=(
        "The checkout service is returning HTTP 503 errors. "
        "We do not yet have logs or metrics."
    ),
    text_format=IncidentAssessment,
)

assessment = response.output_parsed

print(assessment)
print()
print("service:", assessment.service)
print("severity:", assessment.severity)
print("likely layer:", assessment.likely_layer)
print("next action:", assessment.next_action)
print("needs more evidence:", assessment.needs_more_evidence)

from agentic_ops.tools import get_service_status


# Direct invocation verifies the tool contract before exposing it to the model.
status = get_service_status("checkout")

print()
print("tool result:")
print(status)