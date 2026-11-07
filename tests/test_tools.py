from agentic_ops.tools import get_service_logs, get_service_status


def test_checkout_status_is_degraded():
    """
    Verifies the simulated checkout incident remains in the degraded state
    expected by the agent workflow.
    """
    status = get_service_status("checkout")

    assert status.service == "checkout"
    assert status.status == "degraded"
    assert status.http_status == 503
    assert status.healthy_instances == 1
    assert status.total_instances == 3


def test_inventory_status_is_healthy():
    """
    Provides a healthy control case so tool behavior is validated against
    more than the failing checkout scenario.
    """
    status = get_service_status("inventory")

    assert status.service == "inventory"
    assert status.status == "healthy"
    assert status.http_status == 200
    assert status.healthy_instances == 3
    assert status.total_instances == 3


def test_checkout_logs_include_configuration_failure():
    """
    Ensures the simulated log evidence contains the configuration failure
    that should allow the agent to identify the likely incident cause.
    """
    logs = get_service_logs("checkout")

    assert logs.service == "checkout"

    # Validate the evidence the agent relies on without coupling the test
    # to the exact ordering or full text of every simulated log entry.
    assert any(
        "PAYMENT_API_URL" in entry
        for entry in logs.entries
    )