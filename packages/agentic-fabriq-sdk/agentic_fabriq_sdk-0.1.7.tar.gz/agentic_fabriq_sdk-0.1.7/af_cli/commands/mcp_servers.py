"""
MCP server management commands for the Agentic Fabric CLI.
"""

import typer

from af_cli.core.client import get_client
from af_cli.core.output import error, info, print_output, success, warning

app = typer.Typer(help="MCP server management commands")


@app.command()
def list(
    format: str = typer.Option("table", "--format", "-f", help="Output format"),
):
    """List MCP servers."""
    try:
        with get_client() as client:
            response = client.get("/api/v1/mcp-servers")
            servers = response["servers"]
            
            if not servers:
                warning("No MCP servers found")
                return
            
            print_output(
                servers,
                format_type=format,
                title="MCP Servers"
            )
            
    except Exception as e:
        error(f"Failed to list MCP servers: {e}")
        raise typer.Exit(1)


@app.command()
def get(
    server_id: str = typer.Argument(..., help="MCP server ID"),
    format: str = typer.Option("table", "--format", "-f", help="Output format"),
):
    """Get MCP server details."""
    try:
        with get_client() as client:
            server = client.get(f"/api/v1/mcp-servers/{server_id}")
            
            print_output(
                server,
                format_type=format,
                title=f"MCP Server {server_id}"
            )
            
    except Exception as e:
        error(f"Failed to get MCP server: {e}")
        raise typer.Exit(1)


@app.command()
def create(
    name: str = typer.Option(..., "--name", "-n", help="MCP server name"),
    base_url: str = typer.Option(..., "--base-url", "-u", help="Base URL"),
    auth_type: str = typer.Option("API_KEY", "--auth-type", "-a", help="Authentication type"),
):
    """Create a new MCP server."""
    try:
        with get_client() as client:
            data = {
                "name": name,
                "base_url": base_url,
                "auth_type": auth_type,
                "source": "STATIC",
            }
            
            server = client.post("/api/v1/mcp-servers", data)
            
            success(f"MCP server created: {server['id']}")
            info(f"Name: {server['name']}")
            info(f"Base URL: {server['base_url']}")
            
    except Exception as e:
        error(f"Failed to create MCP server: {e}")
        raise typer.Exit(1) 