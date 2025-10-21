"""
Agent management commands for the Agentic Fabric CLI.
"""

from typing import Optional

import typer

from af_cli.core.client import get_client
from af_cli.core.output import error, info, print_output, success, warning, prompt_confirm

app = typer.Typer(help="Agent management commands")


@app.command()
def list(
    page: int = typer.Option(1, "--page", "-p", help="Page number"),
    page_size: int = typer.Option(20, "--page-size", "-s", help="Page size"),
    search: Optional[str] = typer.Option(None, "--search", "-q", help="Search query"),
    format: str = typer.Option("table", "--format", "-f", help="Output format"),
):
    """List agents."""
    try:
        with get_client() as client:
            params = {
                "page": page,
                "page_size": page_size,
            }
            
            if search:
                params["search"] = search
            
            response = client.get("/api/v1/agents", params=params)

            # Support both new (items/total) and legacy (agents/total) shapes
            if isinstance(response, dict):
                if "items" in response:
                    agents = response.get("items", [])
                    total = response.get("total", len(agents))
                elif "agents" in response:
                    agents = response.get("agents", [])
                    total = response.get("total", len(agents))
                else:
                    agents = []
                    total = 0
            elif isinstance(response, list):
                agents = response
                total = len(agents)
            else:
                agents = []
                total = 0
            
            if not agents:
                warning("No agents found")
                return
            
            # Format agent data for display
            display_data = []
            for agent in agents:
                display_data.append({
                    "id": agent.get("id"),
                    "name": agent.get("name"),
                    "version": agent.get("version"),
                    "protocol": agent.get("protocol"),
                    "endpoint_url": agent.get("endpoint_url"),
                    "auth_method": agent.get("auth_method"),
                    "created_at": (agent.get("created_at") or "")[:19],  # Trim microseconds if present
                })
            
            print_output(
                display_data,
                format_type=format,
                columns=["id", "name", "version", "protocol", "endpoint_url", "auth_method", "created_at"],
                title=f"Agents ({len(agents)}/{total})"
            )
            
    except Exception as e:
        error(f"Failed to list agents: {e}")
        raise typer.Exit(1)


@app.command()
def get(
    agent_id: str = typer.Argument(..., help="Agent ID"),
    format: str = typer.Option("table", "--format", "-f", help="Output format"),
):
    """Get agent details."""
    try:
        with get_client() as client:
            agent = client.get(f"/api/v1/agents/{agent_id}")
            
            print_output(
                agent,
                format_type=format,
                title=f"Agent {agent_id}"
            )
            
    except Exception as e:
        error(f"Failed to get agent: {e}")
        raise typer.Exit(1)


@app.command()
def create(
    name: str = typer.Option(..., "--name", "-n", help="Agent name"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Agent description"),
    version: str = typer.Option("1.0.0", "--version", "-v", help="Agent version"),
    protocol: str = typer.Option("HTTP", "--protocol", help="Agent protocol"),
    endpoint_url: str = typer.Option(..., "--endpoint-url", "-u", help="Agent endpoint URL"),
    auth_method: str = typer.Option("OAUTH2", "--auth-method", "-a", help="Authentication method"),
):
    """Create a new agent."""
    try:
        with get_client() as client:
            data = {
                "name": name,
                "description": description,
                "version": version,
                "protocol": protocol,
                "endpoint_url": endpoint_url,
                "auth_method": auth_method,
            }
            
            agent = client.post("/api/v1/agents", data)
            
            success(f"Agent created: {agent['id']}")
            info(f"Name: {agent['name']}")
            info(f"Endpoint: {agent['endpoint_url']}")
            
    except Exception as e:
        error(f"Failed to create agent: {e}")
        raise typer.Exit(1)


@app.command()
def update(
    agent_id: str = typer.Argument(..., help="Agent ID"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Agent name"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Agent description"),
    version: Optional[str] = typer.Option(None, "--version", "-v", help="Agent version"),
    protocol: Optional[str] = typer.Option(None, "--protocol", help="Agent protocol"),
    endpoint_url: Optional[str] = typer.Option(None, "--endpoint-url", "-u", help="Agent endpoint URL"),
    auth_method: Optional[str] = typer.Option(None, "--auth-method", "-a", help="Authentication method"),
):
    """Update an agent."""
    try:
        with get_client() as client:
            data = {}
            
            if name is not None:
                data["name"] = name
            if description is not None:
                data["description"] = description
            if version is not None:
                data["version"] = version
            if protocol is not None:
                data["protocol"] = protocol
            if endpoint_url is not None:
                data["endpoint_url"] = endpoint_url
            if auth_method is not None:
                data["auth_method"] = auth_method
            
            if not data:
                error("No update data provided")
                raise typer.Exit(1)
            
            agent = client.put(f"/api/v1/agents/{agent_id}", data)
            
            success(f"Agent updated: {agent['id']}")
            info(f"Name: {agent['name']}")
            info(f"Endpoint: {agent['endpoint_url']}")
            
    except Exception as e:
        error(f"Failed to update agent: {e}")
        raise typer.Exit(1)


@app.command()
def delete(
    agent_id: str = typer.Argument(..., help="Agent ID"),
    force: bool = typer.Option(False, "--force", "-f", help="Force deletion without confirmation"),
):
    """Delete an agent."""
    try:
        if not force:
            if not prompt_confirm(f"Are you sure you want to delete agent {agent_id}?"):
                info("Deletion cancelled")
                return
        
        with get_client() as client:
            client.delete(f"/api/v1/agents/{agent_id}")
            
            success(f"Agent deleted: {agent_id}")
            
    except Exception as e:
        error(f"Failed to delete agent: {e}")
        raise typer.Exit(1)


@app.command()
def invoke(
    agent_id: str = typer.Argument(..., help="Agent ID"),
    input_text: str = typer.Option(..., "--input", "-i", help="Input message for the agent"),
    format: str = typer.Option("table", "--format", "-f", help="Output format"),
):
    """Invoke an agent."""
    try:
        with get_client() as client:
            data = {
                "input": input_text,
                "parameters": {},
                "context": {},
            }
            
            info(f"Invoking agent {agent_id}...")
            response = client.post(f"/api/v1/agents/{agent_id}/invoke", data)
            
            success("Agent invoked successfully")
            
            # Display response
            if format == "table":
                info("Response:")
                print(response["output"])
                
                if response.get("metadata"):
                    info("\nMetadata:")
                    print_output(response["metadata"], format_type="yaml")
                
                if response.get("logs"):
                    info("\nLogs:")
                    for log in response["logs"]:
                        print(f"  {log}")
            else:
                print_output(response, format_type=format)
            
    except Exception as e:
        error(f"Failed to invoke agent: {e}")
        raise typer.Exit(1) 