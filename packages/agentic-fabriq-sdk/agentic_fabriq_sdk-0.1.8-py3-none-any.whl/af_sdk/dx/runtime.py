from __future__ import annotations

from typing import Any, Dict, List, Optional
import os
import httpx


def _base_headers(token: str, tenant_id: Optional[str]) -> Dict[str, str]:
    headers = {"Authorization": f"Bearer {token}"}
    if tenant_id:
        headers["X-Tenant-Id"] = tenant_id
    # Dev helper: allow overriding scopes from env for local testing
    debug_scopes = os.getenv("FABRIQ_DEBUG_SCOPES")
    if debug_scopes is not None:
        headers["X-Debug-Scopes"] = debug_scopes
    return headers


class ToolFabric:
    """Thin facade over Fabriq provider proxy endpoints (e.g., Slack).

    This class lets developers think in terms of a "fabric" of tools provided
    by a vendor, while under the hood we call the Gateway proxy endpoints.
    """

    def __init__(self, *, provider: str, base_url: str, access_token: str, tenant_id: Optional[str] = None):
        self.provider = provider
        self.base_url = base_url.rstrip("/")
        self.token = access_token
        self.tenant_id = tenant_id

    def get_tools(self, names: List[str]) -> List[str]:
        # Placeholder: simply returns opaque method identifiers as strings the Agent understands
        return [f"{self.provider}:{name}" for name in names]

    def invoke(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/v1/proxy/{self.provider}/{action}"
        with httpx.Client(timeout=30.0) as c:
            r = c.post(url, json=params, headers=_base_headers(self.token, self.tenant_id))
            r.raise_for_status()
            return r.json()


class MCPServer:
    """Facade for an MCP server registered in Fabriq (proxy layer)."""

    def __init__(self, *, server_id: str, base_url: str, access_token: str, tenant_id: Optional[str] = None):
        self.server_id = server_id
        self.base_url = base_url.rstrip("/")
        self.token = access_token
        self.tenant_id = tenant_id

    def get_tools(self, names: List[str]) -> List[str]:
        return [f"mcp:{self.server_id}:{name}" for name in names]

    def invoke(self, tool: str, args: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/v1/proxy/mcp/{self.server_id}/invoke"
        payload = {"payload": {"tool": tool, "args": args}}
        with httpx.Client(timeout=60.0) as c:
            r = c.post(url, json=payload, headers=_base_headers(self.token, self.tenant_id))
            r.raise_for_status()
            return r.json()


class AgentFabric:
    """Future-facing A2A discovery placeholder.

    Today it simply stores identifiers of other agents by id.
    """

    def __init__(self, *, base_url: str, access_token: str, tenant_id: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.token = access_token
        self.tenant_id = tenant_id

    def get_agents(self, ids: List[str]) -> List[str]:
        return ids

    def invoke_agent(self, agent_id: str, input: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/api/v1/agents/{agent_id}/invoke"
        with httpx.Client(timeout=60.0) as c:
            r = c.post(url, json={"input": input, "context": {}}, headers=_base_headers(self.token, self.tenant_id))
            r.raise_for_status()
            return r.json()


class Agent:
    """Minimal orchestrator that can call tools and agents.

    tools: a mixed list of
      - wrapped local functions decorated with @tool (call directly), or
      - string references produced by ToolFabric/MCPServer (we route accordingly).
    agents: a list of agent ids discoverable via AgentFabric.get_agents().
    """

    def __init__(
        self,
        *,
        system_prompt: str,
        tools: List[Any],
        agents: List[str],
        base_url: str,
        access_token: str,
        tenant_id: Optional[str] = None,
        provider_fabrics: Optional[Dict[str, ToolFabric]] = None,
        mcp_servers: Optional[Dict[str, MCPServer]] = None,
        agent_fabric: Optional[AgentFabric] = None,
    ) -> None:
        self.system_prompt = system_prompt
        self.tools = tools
        self.agents = agents
        self.base_url = base_url.rstrip("/")
        self.token = access_token
        self.tenant_id = tenant_id
        self.provider_fabrics = provider_fabrics or {}
        self.mcp_servers = mcp_servers or {}
        self.agent_fabric = agent_fabric or AgentFabric(base_url=base_url, access_token=access_token, tenant_id=tenant_id)

    def _is_wrapped_tool(self, obj: Any) -> bool:
        return hasattr(obj, "_af_tool")

    def run(self, instruction: str) -> str:
        # Super-minimal router: if instruction mentions "slack" and "summary",
        # fetch recent messages via a slack ToolFabric and send to a summarizer agent.
        inst = instruction.lower()
        if "slack" in inst and "summary" in inst:
            slack: Optional[ToolFabric] = self.provider_fabrics.get("slack")
            if not slack:
                return "No slack ToolFabric configured."
            # Find a channel id (prefer env, else pick first from channels.list)
            channel_id = os.getenv("SLACK_DEFAULT_CHANNEL")
            if not channel_id:
                try:
                    ch_resp = slack.invoke("channels.list", {})
                    channels = (ch_resp.get("channels") or ch_resp.get("items") or [])
                    if channels:
                        channel_id = channels[0].get("id")
                except Exception:
                    channel_id = None
            if not channel_id:
                return "Could not determine a Slack channel id; set SLACK_DEFAULT_CHANNEL or ensure channels.list works."

            # Fetch messages
            hist = slack.invoke("conversations.history", {"channel": channel_id, "limit": 50})
            # Gateway proxy normalizes to { items: [...] }, but also returns provider-shape under raw
            messages = hist.get("items") or hist.get("messages") or []
            if not messages:
                return "No Slack messages available or Slack is not connected. Connect Slack in the UI (Tools tab) for the active tenant or set SLACK_DEFAULT_CHANNEL."
            lines = [m.get("text", "").strip() for m in messages if m.get("text")]
            corpus = "\n".join(lines)
            # Call first collaborator agent named 'summarizer' if present
            target = next((a for a in self.agents if a == "summarizer"), None)
            if not target:
                return "No summarizer agent configured."
            result = self.agent_fabric.invoke_agent(target, {"text": corpus})
            # result shape: { output, metadata, logs, status }
            return result.get("output") or str(result)

        # Fallback: try local tools if any
        for t in self.tools:
            if self._is_wrapped_tool(t):
                try:
                    out = t(instruction)  # type: ignore[misc]
                    if isinstance(out, str) and out:
                        return out
                except Exception:
                    pass
        return "No handler matched the instruction."


