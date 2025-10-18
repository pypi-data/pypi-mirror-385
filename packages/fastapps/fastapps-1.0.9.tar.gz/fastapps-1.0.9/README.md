# FastApps Framework

<p align="center">
  <strong>A zero-boilerplate framework for building interactive ChatGPT widgets</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/fastapps/"><img src="https://img.shields.io/pypi/v/fastapps.svg" alt="PyPI"></a>
  <a href="https://pypi.org/project/fastapps/"><img src="https://img.shields.io/pypi/pyversions/fastapps.svg" alt="Python"></a>
  <a href="https://pepy.tech/projects/fastapps"><img src="https://static.pepy.tech/personalized-badge/fastapps?period=total&units=INTERNATIONAL_SYSTEM&left_color=GREY&right_color=GREEN&left_text=downloads" alt="PyPI Downloads"></a>
  <a href="https://github.com/DooiLabs/FastApps/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
  <br>
  <a href="https://github.com/DooiLabs/FastApps/actions"><img src="https://github.com/DooiLabs/FastApps/workflows/CI/badge.svg" alt="CI Status"></a>
  <a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
  <a href="https://github.com/DooiLabs/FastApps"><img src="https://img.shields.io/github/stars/DooiLabs/FastApps?style=social" alt="GitHub Stars"></a>
</p>

---

📚 **Documentation**: [https://www.fastapps.org/](https://www.fastapps.org/)

👥 **Community**: [Join Our Discord](https://discord.gg/5cEy3Jqek3)

---

## Quick Start

### 1. Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate    # macOS/Linux
venv\Scripts\activate       # Windows
```

### 2. Install FastApps & Create Project

```bash
pip install fastapps
fastapps init my-app
```

This generates the complete project structure:

```
my-app/
├── server/
│   ├── __init__.py
│   ├── main.py              # Auto-discovery server
│   ├── tools/               # Widget backends
│   │   └── __init__.py
│   └── api/                 # (optional) Shared APIs
│       └── __init__.py
├── widgets/                 # Widget frontends (empty initially)
├── requirements.txt         # Python dependencies
├── package.json             # JavaScript dependencies
├── .gitignore
└── README.md
```

### 3. Install Dependencies

```bash
cd my-app
pip install -r requirements.txt
npm install
```

### 4. Create Your First Widget

```bash
fastapps create my-widget
```

This adds to your project:

```
my-app/
├── server/
│   └── tools/
│       └── my_widget_tool.py # ← Generated: Widget backend
└── widgets/
    └── my-widget/
        └── index.jsx         # ← Generated: Widget frontend
```

### 5. Edit Your Widget Code

**You only need to edit these 2 files:**

#### `server/tools/my_widget_tool.py` - Backend Logic

```python
from fastapps import BaseWidget, Field, ConfigDict
from pydantic import BaseModel
from typing import Dict, Any

class MyWidgetInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: str = Field(default="World")

class MyWidgetTool(BaseWidget):
    identifier = "my-widget"
    title = "My Widget"
    input_schema = MyWidgetInput
    invoking = "Processing..."
    invoked = "Done!"
    
    widget_csp = {
        "connect_domains": [],      # APIs you'll call
        "resource_domains": []      # Images/fonts you'll use
    }
    
    async def execute(self, input_data: MyWidgetInput) -> Dict[str, Any]:
        # Your logic here
        return {
            "name": input_data.name,
            "message": f"Hello, {input_data.name}!"
        }
```

#### `widgets/my-widget/index.jsx` - Frontend UI

```jsx
import React from 'react';
import { useWidgetProps } from 'fastapps';

export default function MyWidget() {
  const props = useWidgetProps();
  
  return (
    <div style={{
      padding: '40px',
      textAlign: 'center',
      background: '#4A90E2',
      color: 'white',
      borderRadius: '12px'
    }}>
      <h1>{props.message}</h1>
      <p>Welcome, {props.name}!</p>
    </div>
  );
}
```

**That's it! These are the only files you need to write.**

### 6. Build Widgets

```bash
npm run build
```

### 7. Start Development Server with Public Access

**Option A: Using `fastapps dev` (Recommended)**

The easiest way to run and expose your server:

```bash
fastapps dev
```

On first run, you'll be prompted for your ngrok auth token:
- Get it free at: https://dashboard.ngrok.com/get-started/your-authtoken
- Token is saved and won't be asked again

You'll see:
```
🚀 FastApps Development Server
┌─────────┬─────────────────────────┐
│ Local   │ http://0.0.0.0:8001    │
│ Public  │ https://xyz.ngrok.io   │
└─────────┴─────────────────────────┘

📡 MCP Server Endpoint: https://xyz.ngrok.io
```

Use the public URL in ChatGPT Settings > Connectors.

**Option B: Manual Setup**

```bash
# Start server
python server/main.py

# In a separate terminal, create tunnel
ngrok http 8001
```

---

## What You Need to Know

### Widget Structure

Every widget has **exactly 2 files you write**:

1. **Python Tool** (`server/tools/*_tool.py`)
   - Define inputs with Pydantic
   - Write your logic in `execute()`
   - Return data as a dictionary

2. **React Component** (`widgets/*/index.jsx`)
   - Get data with `useWidgetProps()`
   - Render your UI
   - Use inline styles

**Everything else is automatic:**
- Widget discovery
- Registration
- Build process
- Server setup
- Mounting logic

### Input Schema

```python
from fastapps import Field, ConfigDict
from pydantic import BaseModel

class MyInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    name: str = Field(default="", description="User's name")
    age: int = Field(default=0, ge=0, le=150)
    email: str = Field(default="", pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
```

### CSP (Content Security Policy)

Allow external resources:

```python
widget_csp = {
    "connect_domains": ["https://api.example.com"],     # For API calls
    "resource_domains": ["https://cdn.example.com"]     # For images/fonts
}
```

### React Hooks

```jsx
import { useWidgetProps, useWidgetState, useOpenAiGlobal } from 'fastapps';

function MyWidget() {
  const props = useWidgetProps();              // Data from Python
  const [state, setState] = useWidgetState({}); // Persistent state
  const theme = useOpenAiGlobal('theme');      // ChatGPT theme
  
  return <div>{props.message}</div>;
}
```

---

## Documentation

- **[Quick Start Guide](https://github.com/DooiLabs/FastApps/blob/main/docs/QUICKSTART.md)** - Detailed setup instructions
- **[Tutorial](https://github.com/DooiLabs/FastApps/blob/main/docs/TUTORIAL.md)** - Step-by-step widget examples
- **[Python API](https://github.com/DooiLabs/FastApps/blob/main/docs/PYTHON_API.md)** - Programmatic dev server control
- **[API Reference](https://github.com/DooiLabs/FastApps/blob/main/docs/API.md)** - Complete API documentation
- **[Examples](https://github.com/DooiLabs/FastApps/tree/main/examples)** - Real-world code examples

---

## CLI Commands

```bash
# Initialize new project
fastapps init my-app

# Create new widget (auto-generates both files)
fastapps create mywidget

# Start development server with ngrok tunnel
fastapps dev

# Start on custom port
fastapps dev --port 8080

# Reset ngrok auth token
fastapps reset-token

# View authentication guide
fastapps auth-info
```

**Tip**: If `fastapps` command is not found, use:
```bash
python -m fastapps.cli.main <command>
```

---

## Project Structure After `fastapps create`

When you run `python -m fastapps.cli.main create my-widget`, you get:

```
my-app/
├── server/
│   ├── __init__.py
│   ├── main.py                  # Already setup (no edits needed)
│   ├── tools/
│   │   ├── __init__.py
│   │   └── my_widget_tool.py    # ← Edit this: Your widget logic
│   └── api/                     # (optional: for shared APIs)
│
├── widgets/
│   └── my-widget/
│       └── index.jsx            # ← Edit this: Your UI
│
├── assets/                      # Auto-generated during build
│   ├── my-widget-HASH.html
│   └── my-widget-HASH.js
│
├── requirements.txt             # Python dependencies
├── package.json                 # JavaScript dependencies
└── build-all.mts                # Auto-copied from fastapps
```

**You only edit the 2 files marked with ←**

---

## Key Features

- **Zero Boilerplate** - Just write your widget code
- **Auto-Discovery** - Widgets automatically registered
- **Type-Safe** - Pydantic for Python, TypeScript for React
- **CLI Tools** - Scaffold widgets instantly
- **Python API** - Programmatic server control
- **ngrok Integration** - Public URLs with one command
- **React Hooks** - Modern React patterns via `fastapps`
- **MCP Protocol** - Native ChatGPT integration

---

## Python API

Start dev servers programmatically:

```python
from fastapps import start_dev_server

# Simple usage
start_dev_server()

# With configuration
start_dev_server(
    port=8080,
    auto_reload=True,
    ngrok_token="your_token"
)

# Get server info without starting
from fastapps import get_server_info
info = get_server_info(port=8001)
print(f"Public URL: {info.public_url}")
```

See [Python API Documentation](./docs/PYTHON_API.md) for more details.

---

## Examples

### Simple Widget

```python
# server/tools/hello_tool.py
class HelloTool(BaseWidget):
    identifier = "hello"
    title = "Hello"
    input_schema = HelloInput
    
    async def execute(self, input_data):
        return {"message": "Hello World!"}
```

```jsx
// widgets/hello/index.jsx
export default function Hello() {
  const props = useWidgetProps();
  return <h1>{props.message}</h1>;
}
```

### With API Call

```python
async def execute(self, input_data):
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
        data = response.json()
    return {"data": data}
```

### With State

```jsx
function Counter() {
  const [state, setState] = useWidgetState({ count: 0 });
  return (
    <button onClick={() => setState({ count: state.count + 1 })}>
      Count: {state.count}
    </button>
  );
}
```

### Development Server with ngrok (pyngrok)

**Real-World Use Cases:**

| Use Case | Scenario | Benefits |
|----------|----------|----------|
| 🤖 **ChatGPT Development** | Develop ChatGPT custom actions locally | Test widgets in ChatGPT without deployment |
| 🪝 **Webhook Testing** | Test webhooks from Stripe, GitHub, Slack | Get real webhook events on localhost |
| 👥 **Remote Collaboration** | Share your local dev server with team | Instant demos without pushing code |
| 📱 **Mobile Testing** | Test mobile apps against local backend | Access localhost from phone/tablet |
| 🔌 **API Integration** | Third-party APIs need public callback URLs | Receive OAuth callbacks locally |
| 🏢 **Client Demos** | Show work-in-progress to clients | Professional public URL instantly |
| 🎓 **Workshops/Teaching** | Students access instructor's local server | Share examples in real-time |
| 🌐 **Cross-Browser Testing** | Test on BrowserStack, Sauce Labs | Cloud browsers access your localhost |
| 🔄 **CI/CD Preview** | Preview branches before deployment | Test PRs with temporary URLs |
| 🛠️ **IoT Development** | IoT devices callback to local server | Hardware talks to dev environment |

#### Programmatic Start
```python
from fastapps import start_dev_server

# Start with automatic ngrok tunnel
start_dev_server(port=8001)

# With custom configuration
start_dev_server(
    port=8080,
    ngrok_token="your_token",
    auto_reload=True
)
```

#### Get Server URLs for Testing
```python
from fastapps import get_server_info

# Create tunnel and get URLs
info = get_server_info(port=8001)
print(f"Local: {info.local_url}")
print(f"Public: {info.public_url}")

# Use in integration tests
import requests
response = requests.get(f"{info.public_url}/health")
```

#### Environment Variable Token
```python
import os
from fastapps import start_dev_server

# Get token from environment (great for CI/CD)
token = os.getenv("NGROK_TOKEN")
start_dev_server(ngrok_token=token)
```

#### Error Handling
```python
from fastapps import start_dev_server, DevServerError, NgrokError

try:
    start_dev_server(port=8001)
except NgrokError as e:
    print(f"ngrok tunnel failed: {e}")
except DevServerError as e:
    print(f"Server error: {e}")
```

#### Automation Script
```python
#!/usr/bin/env python3
from fastapps import start_dev_server
import sys

if __name__ == "__main__":
    try:
        print("🚀 Starting FastApps with ngrok...")
        start_dev_server(
            port=8001,
            auto_reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n✅ Server stopped")
        sys.exit(0)
```

#### Real-World Example Scenarios

**Scenario 1: ChatGPT Custom Action Development**
```python
# Start server for ChatGPT testing
from fastapps import start_dev_server

# Auto-reload when you edit widgets
start_dev_server(
    port=8001,
    auto_reload=True  # Restart on code changes
)
# Copy ngrok URL → ChatGPT Settings → Connectors → Add your URL
# Test widgets live in ChatGPT while developing!
```

**Scenario 2: Webhook Testing (Stripe, GitHub, etc.)**
```python
from fastapps import get_server_info

# Get public URL for webhook configuration
info = get_server_info(port=8001)
print(f"Configure webhook URL: {info.public_url}/webhooks")

# Add this URL to Stripe Dashboard → Webhooks
# Receive real webhook events on your localhost!
```

**Scenario 3: Team Demo / Client Preview**
```python
from fastapps import start_dev_server

# Share work-in-progress with team
start_dev_server(port=8001)

# Send the ngrok URL to your team/client
# They can access your local server instantly!
# No deployment needed
```

**Scenario 4: Mobile App Testing**
```python
from fastapps import get_server_info

info = get_server_info(port=8001)

# Use public URL in your mobile app config
print(f"API Base URL for mobile app: {info.public_url}")

# Test your iOS/Android app against local backend
# No need for deployed staging server
```

**Scenario 5: OAuth Callback (Third-Party APIs)**
```python
from fastapps import start_dev_server

# OAuth providers need public callback URL
start_dev_server(port=8001)

# Register callback: https://your-ngrok-url.ngrok.io/auth/callback
# Test OAuth flow locally:
# 1. User clicks "Login with Google"
# 2. Google redirects to your ngrok URL
# 3. Your local server receives the callback
```

**Scenario 6: CI/CD Integration Testing**
```python
# .github/workflows/test.yml
import os
from fastapps import start_dev_server
import threading
import requests

# Start server in background
def run_server():
    start_dev_server(
        port=8001,
        ngrok_token=os.getenv("NGROK_TOKEN")
    )

# Run server in separate thread
server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()

# Run integration tests against public URL
# Perfect for testing webhooks, OAuth, etc. in CI
```

**Scenario 7: IoT/Embedded Device Testing**
```python
from fastapps import get_server_info

# IoT devices need to callback to your server
info = get_server_info(port=8001)

# Configure IoT device with this URL
print(f"Configure device callback: {info.public_url}/iot/callback")

# Your Raspberry Pi, Arduino, etc. can now reach your localhost!
```

---

## Troubleshooting

**Widget not loading?**
- Check `identifier` matches folder name
- Rebuild: `npm run build`
- Restart: `python server/main.py`

**Import errors?**
```bash
pip install --upgrade fastapps
npm install fastapps@latest
```

**Need help?** Check our [docs](https://github.com/DooiLabs/FastApps/tree/main/docs) or [open an issue](https://github.com/DooiLabs/FastApps/issues)

---

## Contributing

We welcome contributions! Please see our contributing guidelines:

- **[Contributing Guide](https://github.com/DooiLabs/FastApps/blob/main/CONTRIBUTING.md)** - How to contribute to FastApps
- **[Code Style Guide](https://github.com/DooiLabs/FastApps/blob/main/CODE_STYLE.md)** - Code formatting and style standards
- **[GitHub Workflows](https://github.com/DooiLabs/FastApps/blob/main/.github/WORKFLOWS.md)** - CI/CD documentation

### Quick Start for Contributors

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/FastApps.git
cd FastApps

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Make changes and ensure they pass checks
black .
ruff check --fix .
pytest

# Submit a pull request
```

## License

MIT © FastApps Team

## Links

- **PyPI**: https://pypi.org/project/fastapps/
- **ChatJS Hooks**: https://www.npmjs.com/package/fastapps
- **GitHub**: https://github.com/DooiLabs/FastApps
- **MCP Spec**: https://modelcontextprotocol.io/
