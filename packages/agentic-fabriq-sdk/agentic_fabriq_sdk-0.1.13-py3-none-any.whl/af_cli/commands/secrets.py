"""
Secret management commands for the Agentic Fabric CLI.
"""

import typer

from af_cli.core.client import get_client
from af_cli.core.output import error, info, print_output, success

app = typer.Typer(help="Secret management commands")


@app.command()
def get(
    path: str = typer.Argument(..., help="Secret path"),
    format: str = typer.Option("table", "--format", "-f", help="Output format"),
):
    """Get a secret."""
    try:
        with get_client() as client:
            secret = client.get(f"/api/v1/secrets/{path}")
            
            # Don't display the actual secret value in table format
            if format == "table":
                display_data = {
                    "path": secret["path"],
                    "description": secret.get("description", ""),
                    "version": secret["version"],
                    "created_at": secret["created_at"],
                    "updated_at": secret["updated_at"],
                }
                print_output(display_data, format_type=format, title=f"Secret {path}")
                info("Use --format=json to see the secret value")
            else:
                print_output(secret, format_type=format)
            
    except Exception as e:
        error(f"Failed to get secret: {e}")
        raise typer.Exit(1)


@app.command()
def create(
    path: str = typer.Argument(..., help="Secret path"),
    value: str = typer.Option(..., "--value", "-v", help="Secret value"),
    description: str = typer.Option("", "--description", "-d", help="Secret description"),
):
    """Create a new secret."""
    try:
        with get_client() as client:
            data = {
                "value": value,
                "description": description,
            }
            
            secret = client.post(f"/api/v1/secrets/{path}", data)
            
            success(f"Secret created: {secret['path']}")
            info(f"Version: {secret['version']}")
            
    except Exception as e:
        error(f"Failed to create secret: {e}")
        raise typer.Exit(1)


@app.command()
def update(
    path: str = typer.Argument(..., help="Secret path"),
    value: str = typer.Option(..., "--value", "-v", help="Secret value"),
    description: str = typer.Option("", "--description", "-d", help="Secret description"),
):
    """Update a secret."""
    try:
        with get_client() as client:
            data = {
                "value": value,
                "description": description,
            }
            
            secret = client.put(f"/api/v1/secrets/{path}", data)
            
            success(f"Secret updated: {secret['path']}")
            info(f"Version: {secret['version']}")
            
    except Exception as e:
        error(f"Failed to update secret: {e}")
        raise typer.Exit(1)


@app.command()
def delete(
    path: str = typer.Argument(..., help="Secret path"),
    force: bool = typer.Option(False, "--force", "-f", help="Force deletion"),
):
    """Delete a secret."""
    try:
        if not force:
            if not typer.confirm(f"Are you sure you want to delete secret {path}?"):
                info("Deletion cancelled")
                return
        
        with get_client() as client:
            client.delete(f"/api/v1/secrets/{path}")
            
            success(f"Secret deleted: {path}")
            
    except Exception as e:
        error(f"Failed to delete secret: {e}")
        raise typer.Exit(1) 