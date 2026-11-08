import os
from dataclasses import asdict

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from agentic_ops.tools import get_service_logs, get_service_status
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

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


SYSTEM_PROMPT = (
    "You are the reasoning component of an AI operations system. "
    "Use available operational tools to gather evidence before reaching conclusions. "
    "Do not invent service state, logs, or operational facts."
)


def call_model(state: MessagesState) -> dict:
    """
    Executes one model reasoning step using the investigation state accumulated
    by the graph.

    The model may either return a final response or request one or more tools.
    Routing is handled by the graph rather than by an explicit application loop.
    """

    response = model_with_tools.invoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            *state["messages"],
        ]
    )

    # MessagesState appends this AIMessage to the existing message history.
    return {"messages": [response]}


# ToolNode executes tool requests contained in the most recent AIMessage.
# The resulting ToolMessages are automatically added back to graph state.
tool_node = ToolNode(available_tools)


# MessagesState maintains the ordered history of:
# HumanMessage -> AIMessage -> ToolMessage -> AIMessage ...
builder = StateGraph(MessagesState)

builder.add_node("model", call_model)
builder.add_node("tools", tool_node)


# Every workflow begins by asking the model to reason about the incident.
builder.add_edge(START, "model")


# tools_condition examines the latest AIMessage:
#
# tool_calls present -> route to "tools"
# no tool_calls      -> workflow ends
builder.add_conditional_edges(
    "model",
    tools_condition,
)


# After tools execute, return control to the model so it can reason over
# the newly acquired evidence.
builder.add_edge("tools", "model")


graph = builder.compile()


result = graph.invoke(
    {
        "messages": [
            HumanMessage(
                content=(
                    "Investigate the checkout service. Users are reporting "
                    "HTTP 503 errors. Use available operational tools to gather "
                    "enough evidence to identify the likely cause."
                )
            )
        ]
    }
)


print()
print("GRAPH EXECUTION")


# Keep graph behavior visible during development so tool requests, tool
# observations, and the final reasoning step can be inspected directly.
for message in result["messages"]:
    print()
    print(type(message).__name__)

    if getattr(message, "tool_calls", None):
        print("tool calls:", message.tool_calls)

    if message.content:
        print("content:", message.content)


print()
print("FINAL GRAPH RESPONSE")
print(result["messages"][-1].content)

response = model_with_tools.invoke(
    "Investigate the checkout service. Users are reporting HTTP 503 errors. "
    "Use available operational tools to gather evidence before diagnosing the cause."
)


print("MODEL RESPONSE")
print(response)

print()
print("REQUESTED TOOLS")
print(response.tool_calls)