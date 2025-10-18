# FastApps Python API Examples

This directory contains examples of using the FastApps Python API programmatically.

## Available Examples

### 1. Basic Usage (`python_api_basic.py`)
The simplest way to start a dev server:
```bash
python examples/python_api_basic.py
```

### 2. Advanced Configuration (`python_api_advanced.py`)
Custom port, host, and other settings:
```bash
python examples/python_api_advanced.py
```

### 3. With Token (`python_api_with_token.py`)
Provide ngrok token via environment variable:
```bash
NGROK_TOKEN=your_token python examples/python_api_with_token.py
```

### 4. Get Server Info (`python_api_get_info.py`)
Get URLs without starting the server:
```bash
python examples/python_api_get_info.py
```

### 5. Error Handling (`python_api_error_handling.py`)
Proper error handling patterns:
```bash
python examples/python_api_error_handling.py
```

## Quick Reference

### Simple Start
```python
from fastapps import start_dev_server

start_dev_server()
```

### With Configuration
```python
from fastapps import start_dev_server

start_dev_server(
    port=8080,
    host="0.0.0.0",
    ngrok_token="your_token",
    auto_reload=True,
    log_level="debug"
)
```

### Using Config Object
```python
from fastapps import start_dev_server_with_config, DevServerConfig

config = DevServerConfig(
    port=8080,
    ngrok_token="your_token"
)
start_dev_server_with_config(config)
```

### Get Server Info
```python
from fastapps import get_server_info

info = get_server_info(port=8001)
print(f"Public URL: {info.public_url}")
```

### Error Handling
```python
from fastapps import start_dev_server, DevServerError

try:
    start_dev_server()
except DevServerError as e:
    print(f"Error: {e}")
```

## API Reference

See `docs/API.md` for complete API documentation.

## Use Cases

- **Automation**: Start servers programmatically in scripts
- **Testing**: Get URLs for integration tests
- **CI/CD**: Run dev servers in pipelines
- **Jupyter Notebooks**: Start servers in notebooks
- **Custom Workflows**: Build your own dev tools

## Requirements

- Python 3.11+
- FastApps installed (`pip install fastapps`)
- pyngrok installed (`pip install pyngrok`)
- ngrok auth token (get free at https://ngrok.com)

## Need Help?

- CLI Documentation: Run `fastapps --help`
- Full Docs: See `docs/` directory
- Issues: https://github.com/fastapps-framework/fastapps/issues
