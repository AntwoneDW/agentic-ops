from dataclasses import asdict, dataclass

from dataclasses import dataclass
import json

@dataclass
class ServiceStatus:
    service: str
    status: str
    http_status: int
    healthy_instances: int
    total_instances: int


@dataclass
class ServiceLogs:
    service: str
    entries: list[str]


def get_service_status(service: str) -> ServiceStatus:
    """
    Returns the current simulated health state for a service.

    The deterministic implementation can later be replaced by a Kubernetes,
    cloud-platform, or observability integration without changing the
    model-facing tool contract.
    """

    simulated_services = {
        "checkout": ServiceStatus(
            service="checkout",
            status="degraded",
            http_status=503,
            healthy_instances=1,
            total_instances=3,
        ),
        "inventory": ServiceStatus(
            service="inventory",
            status="healthy",
            http_status=200,
            healthy_instances=3,
            total_instances=3,
        ),
    }

    return simulated_services.get(
        service,
        ServiceStatus(
            service=service,
            status="unknown",
            http_status=404,
            healthy_instances=0,
            total_instances=0,
        ),
    )


def get_service_logs(service: str) -> ServiceLogs:
    """
    Returns recent simulated application log entries for a service.

    Keeping the simulation deterministic gives the agent stable evidence
    while the orchestration layer is being developed and tested.
    """

    simulated_logs = {
        "checkout": ServiceLogs(
            service="checkout",
            entries=[
                "ERROR Configuration provider failed to load PAYMENT_API_URL",
                "ERROR Checkout initialization aborted due to missing configuration",
                "WARN Readiness probe failed: application not ready",
            ],
        ),
        "inventory": ServiceLogs(
            service="inventory",
            entries=[
                "INFO Inventory service started successfully",
                "INFO Readiness probe succeeded",
            ],
        ),
    }

    return simulated_logs.get(
        service,
        ServiceLogs(
            service=service,
            entries=["WARN No log data available for requested service"],
        ),
    )

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
