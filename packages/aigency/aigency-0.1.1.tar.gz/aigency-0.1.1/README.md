# Aigency

AI Agent Development Acceleration Kit — build, run, and orchestrate intelligent agents with a production‑ready Agent‑to‑Agent (A2A) runtime.

Aigency provides primitives and utilities to define agents via simple YAML, instantiate them programmatically, and serve them over HTTP using the A2A server. It is designed to be modular, observable, and extensible.

- Python: >= 3.12
- PyPI package: `aigency`
- Core deps: `a2a-sdk`, `pyyaml`, `litellm`, `PyJWT`, `google-adk`

## Features
- Config‑first agents: define agent behavior, skills, tools, and model in YAML
- Agent generator: instantiate agents, build agent cards, and executors programmatically
- A2A integration: serve agents over HTTP with Starlette‑based A2A server
- MCP‑friendly: integrate external tools/services via Model Context Protocol (optional)
- Observability: compatible with Phoenix and A2A Inspector for tracing and debugging
- Docker‑friendly: used across example demos and containers

## Installation
```bash
pip install aigency
```
Requires Python 3.12+.

## Quickstart
Minimal example for a single agent (no MCP) that responds in the user’s language.

1) Create an agent config file (e.g., `agent_config.yaml`):
```yaml
metadata:
  name: hello_agent
  description: A simple example agent that greets and answers briefly.
  version: 1.0.0

service:
  url: http://hello-agent:8080
  capabilities:
    streaming: true
  interface:
    default_input_modes: [text, text/plain]
    default_output_modes: [text, text/plain]

agent:
  model:
    name: gemini-2.0-flash

  instruction: |
      """
      You are a friendly, concise assistant. Always reply in the same language as the user.
      Keep responses short and helpful.
      """

  skills:
    - id: greet
      name: Greet
      description: Greets users and offers help
      examples:
        - "Hello! How can I help you today?"
```

2) Run a tiny A2A app (e.g., `app.py`):
```python
import os
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from aigency.agents.generator import AgentA2AGenerator
from aigency.utils.config_service import ConfigService

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "agent_config.yaml")

config_service = ConfigService(config_file=CONFIG_PATH)
agent_config = config_service.config

agent = AgentA2AGenerator.create_agent(agent_config=agent_config)
agent_card = AgentA2AGenerator.build_agent_card(agent_config=agent_config)
executor = AgentA2AGenerator.build_executor(agent=agent, agent_card=agent_card)

request_handler = DefaultRequestHandler(
    agent_executor=executor,
    task_store=InMemoryTaskStore(),
)
app = A2AStarletteApplication(
    agent_card=agent_card,
    http_handler=request_handler,
).build()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

3) Start the server:
```bash
python app.py
```
Then open http://localhost:8080 to interact via the A2A HTTP interface or connect a compatible client.

## Using Models & Providers
Aigency integrates with LLM providers via its dependencies. For Google Gemini models:

- Use API key (Google AI Studio):
  - `GEMINI_API_KEY=your_gemini_api_key`
  - `GOOGLE_GENAI_USE_VERTEXAI=FALSE`
- Or use Vertex AI (requires additional env like project/region and credentials):
  - `GOOGLE_GENAI_USE_VERTEXAI=TRUE`

Set these environment variables before running your app if you use Gemini‑based models.

## Configuration Reference (YAML)
Common top‑level sections:

- `metadata`: name, description, version
- `service`: url, capabilities, interface defaults
- `agent`:
  - `model`: model name (e.g., `gemini-2.0-flash`)
  - `instruction`: system prompt/persona
  - `skills`: list of skills with `id`, `name`, `description`, and `examples`
  - `tools`: optional integrations (e.g., MCP tools)
- `observability`: optional Phoenix/A2A Inspector configuration

Example of adding an MCP tool:
```yaml
tools:
  - type: mcp
    name: sample_mcp
    description: Example MCP tool
    mcp_config:
      url: sample-mcp-service
      port: 8080
      path: /mcp/
```

## Examples & Demos
Explore ready‑to‑run demos built with Aigency:

- Reception Agent (single agent, no MCP):
  https://aigency-project.github.io/get_started/demos/reception_aigent
- Gossip Agent (single agent + MCP tools):
  https://aigency-project.github.io/get_started/demos/gossip_agent
- Detective Aigency (multi‑agent system):
  https://aigency-project.github.io/get_started/demos/detective_aigency/

Documentation site:
- https://aigency-project.github.io/

## Observability
Aigency‑based apps can be observed with:
- Phoenix dashboard (tracing/metrics)
- A2A Inspector (agent/task introspection)

Refer to the demo repositories for docker‑compose setups that launch these services.

## Development
- Python 3.12+
- Install dev deps and run tests as usual; for versioning helpers, see `scripts/version_manager.py` in this repo.

## License
This project’s license is provided in the `LICENSE` file.
