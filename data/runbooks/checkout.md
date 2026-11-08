# Checkout Service Runbook

## Missing Payment Configuration

If checkout instances fail readiness and logs contain a message indicating
that PAYMENT_API_URL could not be loaded, verify the deployment environment
configuration before restarting the service.

A restart without correcting the missing configuration will recreate the same
failure condition.

Recommended actions:

1. Verify PAYMENT_API_URL exists in the target environment.
2. Confirm the value is available to all checkout instances.
3. Correct the configuration if missing or invalid.
4. Restart or redeploy unhealthy instances only after configuration is corrected.
5. Verify readiness probes succeed and HTTP 503 responses return to normal levels.

## Database Connectivity

If checkout logs show database connection failures, inspect database health and
connection-pool saturation before restarting application instances.

Repeated restarts can increase connection pressure and should not be used as
the first remediation for database exhaustion.

## Downstream Payment Provider

If checkout is healthy but payment requests fail, inspect payment-provider
availability, timeout rates, and circuit-breaker state.

Application restarts are not recommended unless local checkout health is also
degraded.