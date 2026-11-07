import os
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
import json
from dataclasses import asdict
from agentic_ops.tools import get_service_status


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
}


# Preserve the model's output so the next model call has the complete
# conversation state, including the function request it generated.
next_input = list(tool_response.output)


for item in tool_response.output:
    if item.type != "function_call":
        continue

    arguments = json.loads(item.arguments)

    print()
    print("MODEL REQUESTED TOOL")
    print("tool:", item.name)
    print("arguments:", arguments)
    print("call id:", item.call_id)

    # Resolve the requested tool through our explicit application registry.
    # A model-generated tool name never directly becomes arbitrary code execution.
    handler = tool_handlers.get(item.name)

    if handler is None:
        raise ValueError(f"Unsupported tool requested: {item.name}")

    # Execute the real deterministic Python function.
    result = handler(**arguments)

    print()
    print("APPLICATION EXECUTED TOOL")
    print("result:", result)

    # Return the tool result to the model in JSON form.
    #
    # call_id ties this result to the exact function request that produced it.
    next_input.append(
        {
            "type": "function_call_output",
            "call_id": item.call_id,
            "output": json.dumps(asdict(result)),
        }
    )


# Give the model the observation produced by our application and allow it
# to continue reasoning from the newly acquired evidence.
final_response = client.responses.create(
    model=model,
    instructions=(
        "You are the reasoning component of an AI operations system. "
        "Investigate incidents using available operational tools rather than "
        "inventing service state. Gather evidence before reaching conclusions."
    ),
    input=next_input,
    tools=[service_status_tool],
    parallel_tool_calls=False,
)

print()
print("MODEL AFTER TOOL RESULT")
print(final_response.output_text)

# Inspect the model response for a requested function call.
# At this stage we are deliberately NOT executing the tool yet.
# for item in tool_response.output:
#     if item.type != "function_call":
#         continue
#
#     arguments = json.loads(item.arguments)
#
#     print()
#     print("MODEL REQUESTED TOOL")
#     print("tool:", item.name)
#     print("arguments:", arguments)
#     print("call id:", item.call_id)

from dataclasses import asdict