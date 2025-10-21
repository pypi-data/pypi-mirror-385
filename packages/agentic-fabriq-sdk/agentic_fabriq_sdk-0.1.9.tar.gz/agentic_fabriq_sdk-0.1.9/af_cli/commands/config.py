"""
Configuration commands for the Agentic Fabric CLI.
"""

import typer

from af_cli.core.config import get_config
from af_cli.core.output import error, info, print_output, success

app = typer.Typer(help="Configuration commands")


@app.command()
def show(
    format: str = typer.Option("table", "--format", "-f", help="Output format"),
):
    """Show current configuration."""
    config = get_config()
    
    config_data = {
        "gateway_url": config.gateway_url,
        "tenant_id": config.tenant_id or "Not set",
        "authenticated": "Yes" if config.is_authenticated() else "No",
        "config_file": config.config_file,
        "output_format": config.output_format,
    }
    
    print_output(
        config_data,
        format_type=format,
        title="Configuration"
    )


@app.command()
def set(
    key: str = typer.Argument(..., help="Configuration key"),
    value: str = typer.Argument(..., help="Configuration value"),
):
    """Set configuration value."""
    config = get_config()
    
    valid_keys = {
        "gateway_url": "gateway_url",
        "tenant_id": "tenant_id",
        "output_format": "output_format",
    }
    
    if key not in valid_keys:
        error(f"Invalid configuration key: {key}")
        error(f"Valid keys: {', '.join(valid_keys.keys())}")
        raise typer.Exit(1)
    
    # Set the value
    setattr(config, valid_keys[key], value)
    config.save()
    
    success(f"Configuration updated: {key} = {value}")


@app.command()
def get(
    key: str = typer.Argument(..., help="Configuration key"),
):
    """Get configuration value."""
    config = get_config()
    
    valid_keys = {
        "gateway_url": "gateway_url",
        "tenant_id": "tenant_id",
        "output_format": "output_format",
    }
    
    if key not in valid_keys:
        error(f"Invalid configuration key: {key}")
        error(f"Valid keys: {', '.join(valid_keys.keys())}")
        raise typer.Exit(1)
    
    value = getattr(config, valid_keys[key])
    info(f"{key}: {value}")


@app.command()
def reset():
    """Reset configuration to defaults."""
    config = get_config()
    
    if not typer.confirm("Are you sure you want to reset configuration to defaults?"):
        info("Reset cancelled")
        return
    
    # Clear authentication
    config.clear_auth()
    
    # Reset to defaults
    config.gateway_url = "https://dashboard.agenticfabriq.com"
    config.tenant_id = None
    config.output_format = "table"
    
    config.save()
    
    success("Configuration reset to defaults") 