# Agentic Fabric SDK (Fabriq)

`agentic-fabriq-sdk` provides a Python SDK for interacting with Fabriq/Agentic Fabric.

- High-level client: `af_sdk.FabriqClient`
- DX layer: `af_sdk.dx` (`ToolFabric`, `AgentFabric`, `MCPServer`, `Agent`, and `tool`)

## Install

```bash
pip install agentic-fabriq-sdk
```

## Quickstart

```python
from af_sdk.fabriq_client import FabriqClient

TOKEN = "..."  # Bearer JWT for the Fabriq Gateway
BASE = "http://localhost:8000"

async def main():
    async with FabriqClient(base_url=BASE, auth_token=TOKEN) as af:
        agents = await af.list_agents()
        print(agents)
```

DX orchestration:

```python
from af_sdk.dx import ToolFabric, AgentFabric, Agent, tool

slack = ToolFabric(provider="slack", base_url="http://localhost:8000", access_token=TOKEN, tenant_id=TENANT)
agents = AgentFabric(base_url="http://localhost:8000", access_token=TOKEN, tenant_id=TENANT)

@tool
def echo(x: str) -> str:
    return x

bot = Agent(
    system_prompt="demo",
    tools=[echo],
    agents=agents.get_agents(["summarizer"]),
    base_url="http://localhost:8000",
    access_token=TOKEN,
    tenant_id=TENANT,
    provider_fabrics={"slack": slack},
)
print(bot.run("Summarize my Slack messages"))
```

## License

Apache-2.0
