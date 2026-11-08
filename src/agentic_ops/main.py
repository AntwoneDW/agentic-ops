import os
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
import json
from dataclasses import asdict

from agentic_ops.models import IncidentAssessment
from agentic_ops.tools import get_service_logs, get_service_status

load_dotenv()

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"]
)

model = os.getenv("OPENAI_MODEL", "gpt-6-luna")




from agentic_ops.agent import run_incident_agent

if __name__ == "__main__":
    run_incident_agent("checkout", client, model)