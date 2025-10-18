"""
FastApps Development Server API

Programmatic interface for starting FastApps development server with ngrok tunnel.

Example:
    from fastapps import start_dev_server

    # Simple usage
    start_dev_server()

    # With configuration
    start_dev_server(port=8080, ngrok_token="your_token")
"""

import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class DevServerConfig:
    """Configuration for development server.

    Attributes:
        port: Port to run server on (default: 8001)
        host: Host to bind server to (default: "0.0.0.0")
        ngrok_token: ngrok auth token (optional, will prompt if not provided)
        project_root: Path to FastApps project (default: current directory)
        auto_reload: Enable auto-reload on code changes (default: False)
        log_level: Uvicorn log level (default: "info")
    """

    port: int = 8001
    host: str = "0.0.0.0"
    ngrok_token: Optional[str] = None
    project_root: Optional[Path] = None
    auto_reload: bool = False
    log_level: str = "info"

    def __post_init__(self):
        if self.project_root is None:
            self.project_root = Path.cwd()
        elif not isinstance(self.project_root, Path):
            self.project_root = Path(self.project_root)


@dataclass
class ServerInfo:
    """Information about running server.

    Attributes:
        local_url: Local server URL
        public_url: Public ngrok URL
        port: Server port
        host: Server host
        mcp_endpoint: MCP server endpoint URL
    """

    local_url: str
    public_url: str
    port: int
    host: str
    mcp_endpoint: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def __str__(self) -> str:
        return (
            f"FastApps Dev Server\n"
            f"  Local:  {self.local_url}\n"
            f"  Public: {self.public_url}\n"
            f"  MCP:    {self.mcp_endpoint}"
        )


class DevServerError(Exception):
    """Base exception for dev server errors."""

    pass


class ProjectNotFoundError(DevServerError):
    """Raised when FastApps project not found."""

    pass


class NgrokError(DevServerError):
    """Raised when ngrok fails."""

    pass


def _get_config_dir() -> Path:
    """Get FastApps config directory."""
    config_dir = Path.home() / ".fastapps"
    config_dir.mkdir(exist_ok=True)
    return config_dir


def _load_saved_config() -> Dict[str, Any]:
    """Load saved configuration."""
    config_file = _get_config_dir() / "config.json"
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_config(config: Dict[str, Any]) -> bool:
    """Save configuration."""
    config_file = _get_config_dir() / "config.json"
    try:
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
        return True
    except Exception:
        return False


def _get_ngrok_token(provided_token: Optional[str] = None) -> Optional[str]:
    """Get ngrok token from config or parameter."""
    if provided_token:
        return provided_token

    config = _load_saved_config()
    return config.get("ngrok_token")


def _setup_ngrok(token: str, port: int) -> str:
    """Setup ngrok tunnel and return public URL."""
    try:
        from pyngrok import ngrok

        # Set auth token
        ngrok.set_auth_token(token)

        # Create tunnel
        public_url = ngrok.connect(port, bind_tls=True)
        return public_url.public_url

    except ImportError:
        raise NgrokError(
            "pyngrok is not installed. Install it with: pip install pyngrok"
        )
    except Exception as e:
        raise NgrokError(f"Failed to create ngrok tunnel: {e}")


def _validate_project(project_root: Path) -> None:
    """Validate that directory is a FastApps project."""
    main_py = project_root / "server" / "main.py"
    if not main_py.exists():
        raise ProjectNotFoundError(
            f"Not a FastApps project. Missing: {main_py}\n"
            f"Run 'fastapps init' to create a new project."
        )


def start_dev_server(
    port: int = 8001,
    host: str = "0.0.0.0",
    ngrok_token: Optional[str] = None,
    project_root: Optional[Path] = None,
    auto_reload: bool = False,
    log_level: str = "info",
    return_info: bool = False,
) -> Optional[ServerInfo]:
    """Start FastApps development server with ngrok tunnel.

    This function starts a FastApps server and creates a public ngrok tunnel.
    It blocks until the server is stopped (Ctrl+C).

    Args:
        port: Port to run server on (default: 8001)
        host: Host to bind to (default: "0.0.0.0")
        ngrok_token: ngrok auth token (if None, uses saved token or prompts)
        project_root: Path to FastApps project (default: current directory)
        auto_reload: Enable auto-reload on code changes (default: False)
        log_level: Uvicorn log level (default: "info")
        return_info: If True, return ServerInfo before starting (default: False)

    Returns:
        ServerInfo if return_info=True, otherwise None

    Raises:
        ProjectNotFoundError: If not in a FastApps project
        NgrokError: If ngrok setup fails
        DevServerError: For other server errors

    Example:
        >>> from fastapps import start_dev_server
        >>> start_dev_server(port=8080)

        # Or with config
        >>> start_dev_server(
        ...     port=8080,
        ...     ngrok_token="your_token",
        ...     log_level="debug"
        ... )
    """
    # Create config
    config = DevServerConfig(
        port=port,
        host=host,
        ngrok_token=ngrok_token,
        project_root=project_root,
        auto_reload=auto_reload,
        log_level=log_level,
    )

    # Validate project
    _validate_project(config.project_root)

    # Get ngrok token
    token = _get_ngrok_token(config.ngrok_token)
    if not token:
        raise DevServerError(
            "ngrok token not found. Provide it via:\n"
            "1. ngrok_token parameter\n"
            "2. Run 'fastapps dev' once to save token\n"
            "3. Set in ~/.fastapps/config.json"
        )

    # Setup ngrok
    try:
        print(f"🔧 Setting up ngrok tunnel on port {config.port}...")
        public_url = _setup_ngrok(token, config.port)

        # Create server info
        local_url = f"http://{config.host}:{config.port}"
        server_info = ServerInfo(
            local_url=local_url,
            public_url=public_url,
            port=config.port,
            host=config.host,
            mcp_endpoint=public_url,
        )

        print(f"✅ Tunnel created!")
        print(f"\n{server_info}\n")

        # Return info if requested (for testing/integration)
        if return_info:
            return server_info

        # Add project to path
        sys.path.insert(0, str(config.project_root))

        # Import and run server
        print(f"🚀 Starting FastApps server...\n")

        try:
            import uvicorn
            from server.main import app

            uvicorn.run(
                app,
                host=config.host,
                port=config.port,
                log_level=config.log_level,
                reload=config.auto_reload,
            )

        except ImportError as e:
            raise DevServerError(
                f"Failed to import server: {e}\n"
                f"Make sure you're in a FastApps project with dependencies installed."
            )

    except KeyboardInterrupt:
        print("\n⏹️  Server stopped")
        return None
    except NgrokError:
        raise
    except Exception as e:
        raise DevServerError(f"Server error: {e}")


def start_dev_server_with_config(config: DevServerConfig) -> Optional[ServerInfo]:
    """Start dev server with configuration object.

    Args:
        config: DevServerConfig instance

    Returns:
        ServerInfo if config includes return_info, otherwise None

    Example:
        >>> from fastapps import start_dev_server_with_config, DevServerConfig
        >>> config = DevServerConfig(port=8080, ngrok_token="token")
        >>> start_dev_server_with_config(config)
    """
    return start_dev_server(
        port=config.port,
        host=config.host,
        ngrok_token=config.ngrok_token,
        project_root=config.project_root,
        auto_reload=config.auto_reload,
        log_level=config.log_level,
    )


def get_server_info(
    port: int = 8001, host: str = "0.0.0.0", ngrok_token: Optional[str] = None
) -> ServerInfo:
    """Get server info without starting the server.

    This creates the ngrok tunnel and returns server URLs,
    but does NOT start the FastApps server.

    Args:
        port: Port for server
        host: Host for server
        ngrok_token: ngrok auth token

    Returns:
        ServerInfo with URLs

    Raises:
        NgrokError: If ngrok setup fails

    Example:
        >>> from fastapps import get_server_info
        >>> info = get_server_info(port=8080)
        >>> print(f"Public URL: {info.public_url}")
    """
    token = _get_ngrok_token(ngrok_token)
    if not token:
        raise DevServerError("ngrok token required")

    public_url = _setup_ngrok(token, port)

    return ServerInfo(
        local_url=f"http://{host}:{port}",
        public_url=public_url,
        port=port,
        host=host,
        mcp_endpoint=public_url,
    )


# Convenience alias
run_dev_server = start_dev_server
