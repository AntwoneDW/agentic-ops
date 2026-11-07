# AgenticOps

AgenticOps is a Python-based AI operations workflow project that explores
tool-calling agents, structured outputs, provider abstraction, retrieval,
human approval, persistent workflows, MCP integrations, observability,
and evaluation.

## Current Capabilities

- OpenAI Responses API integration
- Anthropic Claude API integration
- Structured incident assessment using typed model output
- Deterministic service-status and service-log tools
- Model-directed tool selection
- Explicit application-controlled tool dispatch
- Bounded handwritten agent loop
- Multi-step incident investigation using tool observations
- Basic deterministic tool tests

## Current Incident Scenario

The initial workflow investigates a simulated checkout-service incident.

The agent:

1. Receives an incident objective.
2. Determines which operational evidence is required.
3. Requests service-health information.
4. Receives deterministic tool results from the host application.
5. Requests application logs when additional evidence is needed.
6. Produces a final diagnosis once sufficient evidence has been gathered.

## Architecture

The current implementation intentionally uses a handwritten agent loop before
introducing an orchestration framework.

The model proposes tool calls, while the host application retains control over
tool registration, execution, workflow limits, and returned observations.

## Development

Install dependencies:

```bash
uv sync