import os
from dataclasses import asdict

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from agentic_ops.tools import get_service_logs, get_service_status


load_dotenv()


# LangChain derives the model-visible tool schema from the function's
# type hints and docstring. The underlying operations remain deterministic.
@tool("get_service_status")
def service_status_tool(service: str) -> dict:
    """
    Return the current health state for an application service.
    """
    return asdict(get_service_status(service))


@tool("get_service_logs")
def service_logs_tool(service: str) -> dict:
    """
    Return recent application log entries for an application service.
    """
    return asdict(get_service_logs(service))


available_tools = [
    service_status_tool,
    service_logs_tool,
]


# ChatOpenAI gives LangGraph/LangChain a common chat-model interface while
# still using the configured OpenAI model underneath.
model = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-6-luna"),
    api_key=os.environ["OPENAI_API_KEY"],
)


# Binding tools tells the model which application capabilities it may request.
# It does not execute them.
model_with_tools = model.bind_tools(available_tools)


response = model_with_tools.invoke(
    "Investigate the checkout service. Users are reporting HTTP 503 errors. "
    "Use available operational tools to gather evidence before diagnosing the cause."
)


print("MODEL RESPONSE")
print(response)

print()
print("REQUESTED TOOLS")
print(response.tool_calls)