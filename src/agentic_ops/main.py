import os
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
import json
from dataclasses import asdict
from agentic_ops.tools import get_service_logs, get_service_status

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

# from agentic_ops.tools import get_service_status
#
# status = get_service_status("checkout")
#
# print()
# print("tool result:")
# print(status)

# Describe an application capability that the model may request.
#
# This is only the tool contract. OpenAI does not receive or execute
# our local Python implementation of get_service_status().
service_status_tool = {
    "type": "function",
    "name": "get_service_status",
    "description": (
        "Returns the current health state of a named application service, "
        "including HTTP status and healthy instance counts."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "service": {
                "type": "string",
                "description": "The service name, such as checkout or inventory.",
            },
        },
        "required": ["service"],
        "additionalProperties": False,
    },
    "strict": True,
}


service_logs_tool = {
    "type": "function",
    "name": "get_service_logs",
    "description": (
        "Returns recent application log entries for a named service. "
        "Use this when service health indicates degradation or additional "
        "diagnostic evidence is needed."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "service": {
                "type": "string",
                "description": "The service whose recent logs should be inspected.",
            },
        },
        "required": ["service"],
        "additionalProperties": False,
    },
    "strict": True,
}


# Second exercise: give the model access to the tool contract and see
# whether it decides that current service health should be queried.
tool_response = client.responses.create(
    model=model,
    instructions=(
        "You are the reasoning component of an AI operations system. "
        "Investigate incidents using available operational tools rather than "
        "inventing service state. Gather evidence before reaching conclusions."
    ),
    input=(
        "Investigate the checkout service. Users are reporting HTTP 503 errors. "
        "Determine what evidence we should examine first."
    ),
    tools=[service_status_tool],
    parallel_tool_calls=False,
)

# Maps model-visible tool names to application-controlled implementations.
# The model can request a tool by name, but only functions registered here
# can actually be executed.
tool_handlers = {
    "get_service_status": get_service_status,
    "get_service_logs": get_service_logs,
}

available_tools = [
    service_status_tool,
    service_logs_tool,
]


# The model's current working conversation.
#
# Each tool request and tool result is appended here so subsequent model
# calls can reason over the complete investigation performed so far.
agent_input = [
    {
        "role": "user",
        "content": (
            "Investigate the checkout service. Users are reporting HTTP 503 errors. "
            "Use the available operational tools to gather enough evidence to "
            "identify the likely cause."
        ),
    }
]

max_steps = 6


for step in range(1, max_steps + 1):
    print()
    print(f"--- AGENT STEP {step} ---")

    response = client.responses.create(
        model=model,
        instructions=(
            "You are the reasoning component of an AI operations system. "
            "Use available tools to gather evidence before reaching conclusions. "
            "Do not invent service state, logs, or operational facts."
        ),
        input=agent_input,
        tools=available_tools,
        parallel_tool_calls=False,
    )

    # Preserve everything the model produced as part of workflow state.
    agent_input.extend(response.output)

    function_calls = [
        item
        for item in response.output
        if item.type == "function_call"
    ]

    # No requested tools means the model has finished investigating.
    if not function_calls:
        print()
        print("FINAL AGENT RESPONSE")
        print(response.output_text)
        break

    for item in function_calls:
        arguments = json.loads(item.arguments)

        print("MODEL REQUESTED TOOL")
        print("tool:", item.name)
        print("arguments:", arguments)

        handler = tool_handlers.get(item.name)

        if handler is None:
            raise ValueError(f"Unsupported tool requested: {item.name}")

        result = handler(**arguments)

        print("APPLICATION EXECUTED TOOL")
        print("result:", result)

        # Return the deterministic tool observation to the model.
        agent_input.append(
            {
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": json.dumps(asdict(result)),
            }
        )

else:
    raise RuntimeError(
        f"Agent exceeded maximum step limit of {max_steps}"
    )