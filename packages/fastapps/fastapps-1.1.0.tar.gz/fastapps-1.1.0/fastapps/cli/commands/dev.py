"""Development server command with ngrok integration."""

import json
import os
import sys
import subprocess
import time
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def get_config_dir():
    """Get FastApps config directory."""
    config_dir = Path.home() / ".fastapps"
    config_dir.mkdir(exist_ok=True)
    return config_dir


def get_config_file():
    """Get config file path."""
    return get_config_dir() / "config.json"


def load_config():
    """Load configuration from file."""
    config_file = get_config_file()
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                return json.load(f)
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load config: {e}[/yellow]")
    return {}


def save_config(config):
    """Save configuration to file."""
    config_file = get_config_file()
    try:
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        console.print(f"[red]Error: Could not save config: {e}[/red]")
        return False


def get_ngrok_token():
    """Get ngrok auth token from config or prompt user."""
    config = load_config()

    # Check if token exists
    if "ngrok_token" in config and config["ngrok_token"]:
        return config["ngrok_token"]

    # Prompt for token
    console.print("\n[cyan]ngrok authentication required[/cyan]")
    console.print(
        "Get your free auth token at: [link]https://dashboard.ngrok.com/get-started/your-authtoken[/link]\n"
    )

    token = console.input("[bold]Enter your ngrok auth token:[/bold] ").strip()

    if not token:
        console.print("[red]Error: Token is required[/red]")
        return None

    # Save token
    config["ngrok_token"] = token
    if save_config(config):
        console.print("[green]✓ Token saved successfully[/green]\n")

    return token


def set_ngrok_auth(token):
    """Set ngrok auth token."""
    try:
        from pyngrok import ngrok

        ngrok.set_auth_token(token)
        return True
    except Exception as e:
        console.print(f"[red]Error setting ngrok auth token: {e}[/red]")
        return False


def start_dev_server(port=8001, host="0.0.0.0"):
    """Start development server with ngrok tunnel."""

    # Check if we're in a FastApps project
    if not Path("server/main.py").exists():
        console.print("[red]Error: Not in a FastApps project directory[/red]")
        console.print(
            "[yellow]Run this command from your project root (where server/main.py exists)[/yellow]"
        )
        return False

    # Get ngrok token
    console.print("[cyan]Setting up ngrok tunnel...[/cyan]")
    token = get_ngrok_token()

    if not token:
        return False

    # Set ngrok auth
    if not set_ngrok_auth(token):
        return False

    try:
        from pyngrok import ngrok
        import uvicorn

        # Import project server
        sys.path.insert(0, str(Path.cwd()))

        # Start ngrok tunnel
        console.print(f"[cyan]Starting ngrok tunnel on port {port}...[/cyan]")
        public_url = ngrok.connect(port, bind_tls=True)
        ngrok_url = public_url.public_url

        console.print()

        # Display connection info
        table = Table(title="🚀 FastApps Development Server", title_style="bold green")
        table.add_column("Type", style="cyan", no_wrap=True)
        table.add_column("URL", style="white")

        table.add_row("Local", f"http://{host}:{port}")
        table.add_row("Public (ngrok)", f"[bold green]{ngrok_url}[/bold green]")

        console.print(table)
        console.print()

        # Display MCP endpoint info
        mcp_panel = Panel(
            f"[bold]MCP Server Endpoint:[/bold]\n"
            f"[green]{ngrok_url}[/green]\n\n"
            f"[dim]Use this URL in your MCP client configuration[/dim]",
            title="📡 Model Context Protocol",
            border_style="blue",
        )
        console.print(mcp_panel)
        console.print()

        console.print("[yellow]Press Ctrl+C to stop the server[/yellow]\n")

        # Import and run server
        console.print("[cyan]Starting FastApps server...[/cyan]\n")

        from server.main import app

        # Run uvicorn
        uvicorn.run(app, host=host, port=port, log_level="info")

    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down server...[/yellow]")
        try:
            ngrok.disconnect(public_url.public_url)
            console.print("[green]✓ Server stopped[/green]")
        except:
            pass
        return True

    except ImportError as e:
        if "pyngrok" in str(e):
            console.print("[red]Error: pyngrok not installed[/red]")
            console.print("[yellow]Install it with: pip install pyngrok[/yellow]")
        else:
            console.print(f"[red]Error: Could not import server: {e}[/red]")
            console.print(
                "[yellow]Make sure you're in a FastApps project and dependencies are installed[/yellow]"
            )
        return False

    except Exception as e:
        console.print(f"[red]Error starting server: {e}[/red]")
        return False


def reset_ngrok_token():
    """Reset stored ngrok token."""
    config = load_config()
    if "ngrok_token" in config:
        del config["ngrok_token"]
        save_config(config)
        console.print("[green]✓ ngrok token cleared[/green]")
    else:
        console.print("[yellow]No token stored[/yellow]")
