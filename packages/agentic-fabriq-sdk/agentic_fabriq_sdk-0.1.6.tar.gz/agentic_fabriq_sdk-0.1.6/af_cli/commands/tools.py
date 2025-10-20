"""
Tool management commands for the Agentic Fabric CLI.
"""


import typer

from af_cli.core.client import get_client
from af_cli.core.output import error, info, print_output, success, warning

app = typer.Typer(help="Tool management commands")


@app.command()
def list(
    format: str = typer.Option("table", "--format", "-f", help="Output format"),
):
    """List tools."""
    try:
        with get_client() as client:
            response = client.get("/api/v1/tools")
            tools = response["tools"]
            
            if not tools:
                warning("No tools found")
                return
            
            print_output(
                tools,
                format_type=format,
                title="Tools"
            )
            
    except Exception as e:
        error(f"Failed to list tools: {e}")
        raise typer.Exit(1)


@app.command()
def get(
    tool_id: str = typer.Argument(..., help="Tool ID"),
    format: str = typer.Option("table", "--format", "-f", help="Output format"),
):
    """Get tool details."""
    try:
        with get_client() as client:
            tool = client.get(f"/api/v1/tools/{tool_id}")
            
            print_output(
                tool,
                format_type=format,
                title=f"Tool {tool_id}"
            )
            
    except Exception as e:
        error(f"Failed to get tool: {e}")
        raise typer.Exit(1)


@app.command()
def invoke(
    tool_id: str = typer.Argument(..., help="Tool ID"),
    method: str = typer.Option(..., "--method", "-m", help="Tool method to invoke"),
    format: str = typer.Option("table", "--format", "-f", help="Output format"),
):
    """Invoke a tool."""
    try:
        with get_client() as client:
            data = {
                "method": method,
                "parameters": {},
                "context": {},
            }
            
            info(f"Invoking tool {tool_id} method {method}...")
            response = client.post(f"/api/v1/tools/{tool_id}/invoke", data)
            
            success("Tool invoked successfully")
            print_output(response, format_type=format)
            
    except Exception as e:
        error(f"Failed to invoke tool: {e}")
        raise typer.Exit(1) 