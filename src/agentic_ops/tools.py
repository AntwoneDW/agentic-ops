from dataclasses import dataclass


@dataclass
class ServiceStatus:
    service: str
    status: str
    http_status: int
    healthy_instances: int
    total_instances: int


def get_service_status(service: str) -> ServiceStatus:
    """
    Returns the current simulated health state for a service.

    This local implementation keeps the operations layer deterministic.
    It can later be replaced by a Kubernetes, cloud-platform, or
    observability integration without changing the agent contract.
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

    # Return a stable "unknown" state for services outside the simulation.
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