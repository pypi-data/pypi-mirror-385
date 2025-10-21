"""
Tool management commands for the Agentic Fabric CLI.
"""


import typer

from af_cli.core.client import get_client
from af_cli.core.output import debug, error, info, print_output, success, warning

app = typer.Typer(help="Tool management commands")


@app.command()
def list(
    format: str = typer.Option("table", "--format", "-f", help="Output format"),
):
    """List your tool connections (configured and connected tools)."""
    try:
        with get_client() as client:
            connections = client.get("/api/v1/user-connections")
            
            if not connections:
                warning("No tool connections found. Add connections in the dashboard UI.")
                return
            
            # Format for better display
            display_data = []
            for conn in connections:
                # Format tool name nicely (e.g., "google_docs" -> "Google Docs")
                tool_name = conn.get("tool", "N/A").replace("_", " ").title()
                
                # Status indicator
                status = "✓ Connected" if conn.get("connected") else "○ Configured"
                
                display_data.append({
                    "Tool": tool_name,
                    "ID": conn.get("connection_id", "N/A"),
                    "Name": conn.get("display_name") or conn.get("connection_id", "N/A"),
                    "Status": status,
                    "Method": conn.get("method", "oauth"),
                    "Added": conn.get("created_at", "N/A")[:10] if conn.get("created_at") else "N/A",
                })
            
            print_output(
                display_data,
                format_type=format,
                title="Your Tool Connections"
            )
            
    except Exception as e:
        error(f"Failed to list tool connections: {e}")
        raise typer.Exit(1)


@app.command()
def get(
    connection_id: str = typer.Argument(..., help="Connection ID (e.g., 'google', 'slack')"),
    format: str = typer.Option("table", "--format", "-f", help="Output format"),
):
    """Get tool connection details."""
    try:
        with get_client() as client:
            # Get all user connections and find the matching one
            connections = client.get("/api/v1/user-connections")
            
            # Find the specific connection
            connection = None
            for conn in connections:
                if conn.get("connection_id") == connection_id or conn.get("tool") == connection_id:
                    connection = conn
                    break
            
            if not connection:
                error(f"Connection '{connection_id}' not found")
                info("Available connections:")
                for conn in connections:
                    info(f"  - {conn.get('tool')} (ID: {conn.get('connection_id')})")
                raise typer.Exit(1)
            
            # Format tool name nicely
            tool_name = connection.get("tool", "N/A").replace("_", " ").title()
            
            # Format the connection details for display
            details = {
                "Tool": tool_name,
                "Connection ID": connection.get("connection_id", "N/A"),
                "Display Name": connection.get("display_name") or connection.get("connection_id", "N/A"),
                "Status": "✓ Connected" if connection.get("connected") else "○ Configured",
                "Method": connection.get("method", "oauth"),
                "Created": connection.get("created_at", "N/A"),
                "Updated": connection.get("updated_at", "N/A"),
            }
            
            # Add tool-specific fields if present
            if connection.get("team_name"):
                details["Team Name"] = connection.get("team_name")
            if connection.get("team_id"):
                details["Team ID"] = connection.get("team_id")
            if connection.get("bot_user_id"):
                details["Bot User ID"] = connection.get("bot_user_id")
            if connection.get("email"):
                details["Email"] = connection.get("email")
            if connection.get("login"):
                details["GitHub Login"] = connection.get("login")
            if connection.get("workspace_name"):
                details["Workspace Name"] = connection.get("workspace_name")
            if connection.get("scopes"):
                details["Scopes"] = ", ".join(connection.get("scopes", []))
            
            print_output(
                details,
                format_type=format,
                title=f"{tool_name} Connection Details"
            )
            
    except Exception as e:
        error(f"Failed to get tool connection: {e}")
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


@app.command()
def add(
    tool: str = typer.Argument(..., help="Tool name (google, slack, notion, github, etc.)"),
    connection_id: str = typer.Option(..., "--connection-id", help="Unique connection ID"),
    display_name: str = typer.Option(None, "--display-name", help="Human-readable name"),
    method: str = typer.Option(..., "--method", help="Connection method: 'api' or 'credentials'"),
    
    # API method fields
    token: str = typer.Option(None, "--token", help="API token (for api method)"),
    
    # Credentials method fields
    client_id: str = typer.Option(None, "--client-id", help="OAuth client ID (for credentials method)"),
    client_secret: str = typer.Option(None, "--client-secret", help="OAuth client secret (for credentials method)"),
    redirect_uri: str = typer.Option(None, "--redirect-uri", help="OAuth redirect URI (optional, auto-generated)"),
):
    """
    Add a new tool connection with credentials.
    
    Examples:
      # Notion (api method - single token)
      afctl tools add notion --connection-id notion-work --method api --token "secret_abc123"
      
      # Google (credentials method - OAuth app)
      afctl tools add google --connection-id google-work --method credentials \\
        --client-id "123.apps.googleusercontent.com" \\
        --client-secret "GOCSPX-abc123"
      
      # Slack bot (api method)
      afctl tools add slack --connection-id slack-bot --method api --token "xoxb-123..."
    """
    try:
        from af_cli.core.config import get_config
        
        with get_client() as client:
            # Validate method
            if method not in ["api", "credentials"]:
                error("Method must be 'api' or 'credentials'")
                raise typer.Exit(1)
            
            # Validate API method requirements
            if method == "api":
                if not token:
                    error("API method requires --token")
                    info(f"Example: afctl tools add {tool} --connection-id {connection_id} --method api --token YOUR_TOKEN")
                    raise typer.Exit(1)
            
            # Validate credentials method requirements
            elif method == "credentials":
                if not client_id or not client_secret:
                    error("Credentials method requires --client-id and --client-secret")
                    info(f"Example: afctl tools add {tool} --connection-id {connection_id} --method credentials \\")
                    info(f"  --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET")
                    raise typer.Exit(1)
            
            info(f"Creating connection: {connection_id}")
            info(f"Tool: {tool}")
            info(f"Method: {method}")
            
            # Step 1: Create connection metadata
            connection_data = {
                "tool": tool,
                "connection_id": connection_id,
                "display_name": display_name or connection_id,
                "method": method,
            }
            
            client.post("/api/v1/user-connections", data=connection_data)
            success(f"✅ Connection entry created: {connection_id}")
            
            # Step 2: Store credentials based on method
            if method == "credentials":
                # Auto-generate redirect_uri if not provided
                if not redirect_uri:
                    config = get_config()
                    redirect_uri = f"{config.gateway_url}/api/v1/tools/{tool}/oauth/callback"
                    info(f"Using default redirect URI: {redirect_uri}")
                
                # Store OAuth app config
                info("Storing OAuth app credentials...")
                config_payload = {
                    "client_id": client_id,
                    "client_secret": client_secret,
                }
                if redirect_uri:
                    config_payload["redirect_uri"] = redirect_uri
                
                client.post(
                    f"/api/v1/tools/{tool}/config?connection_id={connection_id}",
                    data=config_payload
                )
                success("✅ OAuth app credentials stored")
                info("")
                info(f"Next: Run 'afctl tools connect {connection_id}' to complete OAuth setup")
                
            elif method == "api":
                # Store API token directly
                info("Storing API credentials...")
                
                # Tool-specific endpoint and payload mappings
                if tool == "notion":
                    # Notion uses /config endpoint with integration_token field
                    endpoint = f"/api/v1/tools/{tool}/config?connection_id={connection_id}"
                    cred_payload = {"integration_token": token}
                else:
                    # Generic tools use /connection endpoint with api_token field
                    endpoint = f"/api/v1/tools/{tool}/connection?connection_id={connection_id}"
                    cred_payload = {"api_token": token}
                
                client.post(endpoint, data=cred_payload)
                success("✅ API credentials stored")
                success(f"✅ Connection '{connection_id}' is ready to use!")
            
            # Show helpful info
            info("")
            info("View your connections:")
            info(f"  • List all: afctl tools list")
            info(f"  • View details: afctl tools get {connection_id}")
            
    except Exception as e:
        error(f"Failed to add connection: {e}")
        raise typer.Exit(1)


@app.command()
def connect(
    connection_id: str = typer.Argument(..., help="Connection ID to connect"),
):
    """Complete OAuth connection (open browser for authorization)."""
    try:
        import webbrowser
        import time
        
        with get_client() as client:
            # Get connection info
            connections = client.get("/api/v1/user-connections")
            
            connection = None
            for conn in connections:
                if conn.get("connection_id") == connection_id:
                    connection = conn
                    break
            
            if not connection:
                error(f"Connection '{connection_id}' not found")
                info("Run 'afctl tools list' to see available connections")
                raise typer.Exit(1)
            
            tool = connection["tool"]
            method = connection["method"]
            
            # Only credentials method needs OAuth completion
            if method != "credentials":
                error(f"Connection '{connection_id}' uses '{method}' method")
                info("Only 'credentials' method connections need OAuth setup")
                info("API connections are already connected after 'afctl tools add'")
                raise typer.Exit(1)
            
            # Check if already connected
            if connection.get("connected"):
                warning(f"Connection '{connection_id}' is already connected")
                confirm = typer.confirm("Do you want to reconnect (re-authorize)?")
                if not confirm:
                    return
            
            # Initiate OAuth flow
            info(f"Initiating OAuth for {tool}...")
            
            result = client.post(
                f"/api/v1/tools/{tool}/connect/initiate?connection_id={connection_id}",
                data={}
            )
            
            debug(f"Backend response: {result}")
            
            # Different tools use different field names for the auth URL
            auth_url = (
                result.get("authorization_url") or 
                result.get("auth_url") or 
                result.get("oauth_url")
            )
            
            if not auth_url:
                error("Failed to get authorization URL from backend")
                error(f"Response keys: {list(result.keys())}")
                debug(f"Full response: {result}")
                raise typer.Exit(1)
            
            info("Opening browser for authentication...")
            info("")
            info(f"If browser doesn't open, visit: {auth_url}")
            
            # Open browser
            webbrowser.open(auth_url)
            
            info("")
            info("Waiting for authorization...")
            info("(Complete the login in your browser)")
            
            # Poll for connection completion
            max_attempts = 120  # 2 minutes
            for attempt in range(max_attempts):
                time.sleep(1)
                
                # Check connection status
                connections = client.get("/api/v1/user-connections")
                for conn in connections:
                    if conn.get("connection_id") == connection_id:
                        if conn.get("connected"):
                            info("")
                            success(f"✅ Successfully connected to {tool}!")
                            
                            # Show connection details
                            info(f"Connection ID: {connection_id}")
                            if conn.get("email"):
                                info(f"Email: {conn['email']}")
                            if conn.get("team_name"):
                                info(f"Team: {conn['team_name']}")
                            if conn.get("login"):
                                info(f"GitHub: {conn['login']}")
                            
                            return
                        break
            
            # Timeout
            error("")
            error("Timeout: Authorization not completed within 2 minutes")
            info("Please try again or check your browser")
            raise typer.Exit(1)
            
    except Exception as e:
        error(f"Failed to connect: {e}")
        raise typer.Exit(1)


@app.command()
def disconnect(
    connection_id: str = typer.Argument(..., help="Connection ID to disconnect"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Disconnect a tool (remove credentials but keep connection entry)."""
    try:
        with get_client() as client:
            # Get connection info
            connections = client.get("/api/v1/user-connections")
            
            connection = None
            for conn in connections:
                if conn.get("connection_id") == connection_id:
                    connection = conn
                    break
            
            if not connection:
                error(f"Connection '{connection_id}' not found")
                raise typer.Exit(1)
            
            tool = connection["tool"]
            tool_display = connection.get("display_name") or connection_id
            
            # Check if connected
            if not connection.get("connected"):
                error(f"Connection '{connection_id}' is already disconnected")
                info(f"Use 'afctl tools get {connection_id}' to view status")
                raise typer.Exit(1)
            
            # Confirm
            if not force:
                warning(f"This will remove OAuth tokens/credentials for '{tool_display}'")
                info("You can reconnect later with 'afctl tools connect'")
                confirm = typer.confirm(f"Disconnect {tool} connection '{connection_id}'?")
                if not confirm:
                    info("Cancelled")
                    return
            
            # Delete connection credentials
            client.delete(
                f"/api/v1/tools/{tool}/connection?connection_id={connection_id}"
            )
            
            success(f"✅ Disconnected: {connection_id}")
            info("Connection entry preserved.")
            info(f"Run 'afctl tools connect {connection_id}' to reconnect.")
            
    except Exception as e:
        error(f"Failed to disconnect: {e}")
        raise typer.Exit(1)


@app.command()
def remove(
    connection_id: str = typer.Argument(..., help="Connection ID to remove"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Remove a tool connection completely (delete entry and credentials)."""
    try:
        with get_client() as client:
            # Get connection info
            connections = client.get("/api/v1/user-connections")
            
            connection = None
            for conn in connections:
                if conn.get("connection_id") == connection_id:
                    connection = conn
                    break
            
            if not connection:
                error(f"Connection '{connection_id}' not found")
                raise typer.Exit(1)
            
            tool = connection["tool"]
            tool_display = connection.get("display_name") or connection_id
            
            # Confirm
            if not force:
                warning("⚠️  This will permanently delete the connection and credentials")
                confirm = typer.confirm(f"Remove {tool} connection '{tool_display}'?")
                if not confirm:
                    info("Cancelled")
                    return
            
            # Delete connection entry (backend will cascade delete credentials)
            client.delete(f"/api/v1/user-connections/{connection_id}")
            
            success(f"✅ Removed: {connection_id}")
            
    except Exception as e:
        error(f"Failed to remove: {e}")
        raise typer.Exit(1) 