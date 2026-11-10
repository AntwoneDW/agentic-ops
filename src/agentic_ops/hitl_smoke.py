from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class RemediationState(TypedDict):
    service: str
    action: str
    approved: bool
    result: str


def request_approval(state: RemediationState) -> dict:
    """
    Pauses workflow execution before a privileged remediation action.
    """

    approved = interrupt(
        {
            "service": state["service"],
            "action": state["action"],
            "question": "Approve this remediation action?",
        }
    )

    return {"approved": bool(approved)}


def execute_remediation(state: RemediationState) -> dict:
    """
    Executes the simulated remediation only after explicit approval.
    """

    if not state["approved"]:
        return {
            "result": (
                f"Remediation rejected. No action taken against "
                f"{state['service']}."
            )
        }

    return {
        "result": (
            f"SIMULATED: {state['action']} executed against "
            f"{state['service']}."
        )
    }


builder = StateGraph(RemediationState)

builder.add_node("approval", request_approval)
builder.add_node("remediation", execute_remediation)

builder.add_edge(START, "approval")
builder.add_edge("approval", "remediation")
builder.add_edge("remediation", END)


checkpointer = InMemorySaver()

graph = builder.compile(
    checkpointer=checkpointer
)


config = {
    "configurable": {
        "thread_id": "checkout-remediation-001"
    }
}


initial_result = graph.invoke(
    {
        "service": "checkout",
        "action": "restart unhealthy checkout instances",
        "approved": False,
        "result": "",
    },
    config=config,
)


print("WORKFLOW PAUSED")
print(initial_result["__interrupt__"])


resumed_result = graph.invoke(
    Command(resume=True),
    config=config,
)


print()
print("WORKFLOW RESUMED")
print(resumed_result["result"])