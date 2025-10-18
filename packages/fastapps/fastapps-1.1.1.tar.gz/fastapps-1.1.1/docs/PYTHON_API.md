# FastApps Python API

The FastApps Python API allows you to start and control development servers programmatically from your Python code.

## Quick Start

```python
from fastapps import start_dev_server

# Start server with defaults
start_dev_server()
```

That's it! The server will start with ngrok tunnel on port 8001.

---

## Installation

The Python API is included with FastApps:

```bash
pip install fastapps
```

Make sure pyngrok is also installed:

```bash
pip install pyngrok
```

---

## Basic Usage

### Simple Start

```python
from fastapps import start_dev_server

if __name__ == "__main__":
    start_dev_server()
```

This will:
1. Load ngrok token from `~/.fastapps/config.json`
2. Create public ngrok tunnel on port 8001
3. Start FastApps server
4. Display local and public URLs

### Custom Port

```python
from fastapps import start_dev_server

start_dev_server(port=8080)
```

### Custom Host

```python
from fastapps import start_dev_server

start_dev_server(
    port=8080,
    host="127.0.0.1"
)
```

---

## Advanced Usage

### With ngrok Token

Provide ngrok token programmatically (useful for CI/CD):

```python
import os
from fastapps import start_dev_server

token = os.getenv("NGROK_TOKEN")
start_dev_server(ngrok_token=token)
```

### With Auto-Reload

Enable automatic server restart on code changes:

```python
from fastapps import start_dev_server

start_dev_server(
    port=8001,
    auto_reload=True,
    log_level="debug"
)
```

### Using Configuration Object

```python
from fastapps import start_dev_server_with_config, DevServerConfig

config = DevServerConfig(
    port=8080,
    host="0.0.0.0",
    ngrok_token="your_token",
    auto_reload=True,
    log_level="info"
)

start_dev_server_with_config(config)
```

---

## Getting Server Information

Get server URLs without starting the server:

```python
from fastapps import get_server_info

# Creates tunnel and returns info
info = get_server_info(port=8001)

print(f"Local URL:  {info.local_url}")
print(f"Public URL: {info.public_url}")
print(f"MCP Endpoint: {info.mcp_endpoint}")

# Keep tunnel alive
import time
while True:
    time.sleep(1)
```

This is useful for:
- Getting URLs before starting server
- Testing and automation
- Custom server implementations

---

## Error Handling

```python
from fastapps import (
    start_dev_server,
    DevServerError,
    ProjectNotFoundError,
    NgrokError
)

try:
    start_dev_server(port=8001)

except ProjectNotFoundError as e:
    print(f"Not a FastApps project: {e}")

except NgrokError as e:
    print(f"ngrok tunnel failed: {e}")

except DevServerError as e:
    print(f"Server error: {e}")

except KeyboardInterrupt:
    print("Server stopped")
```

### Exception Hierarchy

```
DevServerError (base)
├── ProjectNotFoundError
└── NgrokError
```

---

## API Reference

### Functions

#### `start_dev_server()`

Start development server with ngrok tunnel.

**Parameters:**
- `port` (int): Port to run server on (default: 8001)
- `host` (str): Host to bind to (default: "0.0.0.0")
- `ngrok_token` (Optional[str]): ngrok auth token
- `project_root` (Optional[Path]): Project directory (default: current)
- `auto_reload` (bool): Enable auto-reload (default: False)
- `log_level` (str): Logging level (default: "info")
- `return_info` (bool): Return ServerInfo before starting (default: False)

**Returns:** `None` (blocks until stopped) or `ServerInfo` if `return_info=True`

**Raises:**
- `ProjectNotFoundError`: Not in FastApps project
- `NgrokError`: ngrok tunnel failed
- `DevServerError`: Other server errors

**Example:**
```python
start_dev_server(port=8080, auto_reload=True)
```

---

#### `start_dev_server_with_config()`

Start server using configuration object.

**Parameters:**
- `config` (DevServerConfig): Configuration object

**Returns:** `None` (blocks until stopped)

**Example:**
```python
config = DevServerConfig(port=8080, auto_reload=True)
start_dev_server_with_config(config)
```

---

#### `get_server_info()`

Get server URLs without starting server.

**Parameters:**
- `port` (int): Server port (default: 8001)
- `host` (str): Server host (default: "0.0.0.0")
- `ngrok_token` (Optional[str]): ngrok auth token

**Returns:** `ServerInfo` with URLs

**Raises:**
- `NgrokError`: ngrok tunnel failed
- `DevServerError`: Token not found

**Example:**
```python
info = get_server_info(port=8001)
print(info.public_url)
```

---

#### `run_dev_server()`

Alias for `start_dev_server()`.

---

### Classes

#### `DevServerConfig`

Configuration for development server.

**Attributes:**
- `port` (int): Server port (default: 8001)
- `host` (str): Server host (default: "0.0.0.0")
- `ngrok_token` (Optional[str]): ngrok auth token
- `project_root` (Optional[Path]): Project directory
- `auto_reload` (bool): Enable auto-reload (default: False)
- `log_level` (str): Log level (default: "info")

**Example:**
```python
config = DevServerConfig(
    port=8080,
    ngrok_token="your_token",
    auto_reload=True
)
```

---

#### `ServerInfo`

Information about running server.

**Attributes:**
- `local_url` (str): Local server URL
- `public_url` (str): Public ngrok URL
- `port` (int): Server port
- `host` (str): Server host
- `mcp_endpoint` (str): MCP server endpoint

**Methods:**
- `to_dict()`: Convert to dictionary
- `__str__()`: Human-readable string

**Example:**
```python
info = get_server_info()
print(info)  # Pretty print
print(info.to_dict())  # As dictionary
```

---

## Use Cases

### 1. Automation Scripts

```python
#!/usr/bin/env python3
from fastapps import start_dev_server

if __name__ == "__main__":
    print("Starting automated dev server...")
    start_dev_server(port=8001)
```

### 2. Jupyter Notebooks

```python
# Cell 1: Start server in background
import threading
from fastapps import start_dev_server

def start_server():
    start_dev_server(port=8001)

thread = threading.Thread(target=start_server, daemon=True)
thread.start()

# Cell 2: Continue working while server runs
print("Server running in background!")
```

### 3. CI/CD Pipelines

```python
import os
from fastapps import start_dev_server

# Get token from environment
token = os.getenv("NGROK_TOKEN")

# Start server for testing
start_dev_server(
    port=8001,
    ngrok_token=token,
    log_level="error"  # Quiet mode
)
```

### 4. Testing

```python
import pytest
from fastapps import get_server_info

@pytest.fixture
def dev_server():
    """Provide server URLs for tests."""
    info = get_server_info(port=8001)
    yield info
    # Cleanup handled by ngrok

def test_api_endpoint(dev_server):
    import requests
    response = requests.get(f"{dev_server.public_url}/health")
    assert response.status_code == 200
```

### 5. Custom Dev Tools

```python
from fastapps import start_dev_server, DevServerConfig
import click

@click.command()
@click.option("--port", default=8001, help="Server port")
@click.option("--reload", is_flag=True, help="Enable auto-reload")
def mydev(port, reload):
    """Custom dev command."""
    config = DevServerConfig(
        port=port,
        auto_reload=reload,
        log_level="debug" if reload else "info"
    )
    start_dev_server_with_config(config)

if __name__ == "__main__":
    mydev()
```

---

## Configuration

### ngrok Token Storage

Token is stored in `~/.fastapps/config.json`:

```json
{
  "ngrok_token": "your_token_here"
}
```

You can:
1. Provide token via `ngrok_token` parameter
2. Run `fastapps dev` once to save token
3. Manually edit `~/.fastapps/config.json`

### Environment Variables

```bash
# Provide token via environment
export NGROK_TOKEN=your_token
python your_script.py
```

---

## Examples

See `examples/` directory for complete working examples:

- `python_api_basic.py` - Simple usage
- `python_api_advanced.py` - Custom configuration
- `python_api_with_token.py` - Environment variable token
- `python_api_get_info.py` - Get URLs without starting
- `python_api_error_handling.py` - Error handling patterns

Run any example:
```bash
python examples/python_api_basic.py
```

---

## Comparison: CLI vs Python API

| Feature | CLI Command | Python API |
|---------|-------------|------------|
| **Simple Start** | `fastapps dev` | `start_dev_server()` |
| **Custom Port** | `fastapps dev --port 8080` | `start_dev_server(port=8080)` |
| **Get URLs Only** | ❌ Not available | `get_server_info()` |
| **Programmatic Control** | ❌ Limited | ✅ Full control |
| **In Scripts** | ❌ Requires subprocess | ✅ Native Python |
| **Error Handling** | ❌ Exit codes only | ✅ Exception catching |
| **Use in Tests** | ❌ Difficult | ✅ Easy |

---

## Best Practices

### 1. Token Management

✅ **Good:**
```python
# Use saved token
start_dev_server()

# Or environment variable
import os
start_dev_server(ngrok_token=os.getenv("NGROK_TOKEN"))
```

❌ **Bad:**
```python
# Hardcoded token
start_dev_server(ngrok_token="hardcoded_token_here")
```

### 2. Error Handling

✅ **Good:**
```python
try:
    start_dev_server()
except DevServerError as e:
    logger.error(f"Server failed: {e}")
    sys.exit(1)
```

❌ **Bad:**
```python
# No error handling
start_dev_server()  # Will crash on error
```

### 3. Project Validation

✅ **Good:**
```python
from pathlib import Path

if not (Path.cwd() / "server" / "main.py").exists():
    print("Not a FastApps project!")
    sys.exit(1)

start_dev_server()
```

---

## Troubleshooting

### Token Not Found

```python
DevServerError: ngrok token not found
```

**Solutions:**
1. Run `fastapps dev` once to save token
2. Provide via `ngrok_token` parameter
3. Set in `~/.fastapps/config.json`

### Project Not Found

```python
ProjectNotFoundError: Not a FastApps project
```

**Solutions:**
1. Run from project root directory
2. Specify `project_root` parameter
3. Check `server/main.py` exists

### Port Already in Use

```python
DevServerError: Address already in use
```

**Solutions:**
1. Use different port: `start_dev_server(port=8080)`
2. Stop other servers on that port
3. Check with: `lsof -i :8001`

---

## Next Steps

- [Examples Directory](../examples/)
- [CLI Documentation](./01-INTRO.md)
- [API Reference](./API.md)
- [ngrok Integration Guide](../NGROK_INTEGRATION.md)

---

## Support

- GitHub Issues: https://github.com/fastapps-framework/fastapps/issues
- Discord Community: https://discord.gg/fastapps
- Documentation: https://fastapps.dev/docs
