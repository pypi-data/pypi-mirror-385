# FastApps Quick Start Guide

Get your first ChatGPT widget running in 5 minutes!

## What Gets Created

When you run `fastapps create greeting`, this structure is generated:

```
my-widgets/
├── server/
│   ├── __init__.py              # Empty file
│   ├── main.py                  # Auto-discovery server (pre-configured)
│   └── tools/
│       ├── __init__.py          # Empty file
│       └── greeting_tool.py     # ← YOUR CODE: Widget backend
│
├── widgets/
│   └── greeting/
│       └── index.jsx            # ← YOUR CODE: Widget frontend
│
├── assets/                      # Auto-generated during npm run build
│   ├── greeting-HASH.html
│   └── greeting-HASH.js
│
├── build-all.mts                # Auto-copied from fastapps
├── requirements.txt             # Python dependencies
└── package.json                 # JavaScript dependencies
```

**You only edit the files marked with ←**

---

## Step 1: Install FastApps

```bash
pip install fastapps
```

## Step 2: Create Project Structure

```bash
# Create project directory
mkdir my-widgets
cd my-widgets

# Create folder structure
mkdir -p server/tools server/api widgets
```

## Step 3: Setup Files

### Create `server/main.py`

```python
from pathlib import Path
import sys
import importlib
import inspect

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapps import WidgetBuilder, WidgetMCPServer, BaseWidget
import uvicorn

PROJECT_ROOT = Path(__file__).parent.parent
TOOLS_DIR = Path(__file__).parent / "tools"

def auto_load_tools(build_results):
    tools = []
    for tool_file in TOOLS_DIR.glob("*_tool.py"):
        module_name = tool_file.stem
        try:
            module = importlib.import_module(f"server.tools.{module_name}")
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BaseWidget) and obj is not BaseWidget:
                    tool_identifier = obj.identifier
                    if tool_identifier in build_results:
                        tool_instance = obj(build_results[tool_identifier])
                        tools.append(tool_instance)
                        print(f"[OK] Loaded: {name}")
        except Exception as e:
            print(f"[ERROR] Error: {e}")
    return tools

builder = WidgetBuilder(PROJECT_ROOT)
build_results = builder.build_all()
tools = auto_load_tools(build_results)
server = WidgetMCPServer(name="my-widgets", widgets=tools)
app = server.get_app()

if __name__ == "__main__":
    print(f"\n[START] Starting with {len(tools)} tools")
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

### Create `server/__init__.py` and `server/tools/__init__.py`

```bash
touch server/__init__.py
touch server/tools/__init__.py
```

### Create `requirements.txt`

```
fastapps>=1.0.3
httpx>=0.28.0
```

### Create `package.json`

```json
{
  "name": "my-widgets",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "build": "npx tsx node_modules/fastapps/build-all.mts"
  },
  "dependencies": {
    "fastapps": "^1.0.0",
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.4",
    "fast-glob": "^3.3.2",
    "tsx": "^4.19.2",
    "typescript": "^5.7.2",
    "vite": "^6.0.5"
  }
}
```

## Step 4: Install Dependencies

```bash
pip install -r requirements.txt
npm install
```

## Step 5: Create Your First Widget

```bash
python -m fastapps.cli.main create hello
```

This creates:
- `server/tools/hello_tool.py`
- `widgets/hello/index.jsx`

## Step 6: Build Widgets

```bash
npm run build
```

## Step 7: Start Development Server

**Recommended: Using `fastapps dev`**

```bash
fastapps dev
```

This will:
1. Prompt for your ngrok token (first time only)
2. Start your FastApps server
3. Create a public ngrok tunnel
4. Display both local and public URLs

Output:
```
🚀 FastApps Development Server
┌─────────┬─────────────────────────┐
│ Local   │ http://0.0.0.0:8001    │
│ Public  │ https://xyz.ngrok.io   │
└─────────┴─────────────────────────┘

📡 MCP Server Endpoint: https://xyz.ngrok.io
```

**Alternative: Manual Start**

```bash
python server/main.py
```

Your server runs on `http://localhost:8001`. For ChatGPT testing, you'll need to expose it with ngrok manually.

## Step 8: Test in ChatGPT!

1. Copy your public ngrok URL
2. Go to ChatGPT Settings > Connectors
3. Add new connector with your ngrok URL
4. Your widget is ready to use!

## Next Steps

- [Full Documentation](../README.md)
- [Widget Tutorial](./TUTORIAL.md)
- [API Reference](./API.md)
- [Examples](../../examples/)

## Common Issues

### Module not found

```bash
pip install --upgrade fastapps
```

### Build fails

```bash
npm install fastapps@latest --force
```

### Widget not loading

Check that `identifier` matches folder name:
```python
identifier = "hello"  # Must match widgets/hello/
```

