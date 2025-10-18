"""
Basic Python API Usage for FastApps Dev Server

This example shows the simplest way to start a dev server programmatically.
"""

from fastapps import start_dev_server

if __name__ == "__main__":
    # Simple usage - uses defaults (port 8001, host 0.0.0.0)
    # Will use saved ngrok token from ~/.fastapps/config.json
    print("Starting FastApps development server...")

    start_dev_server()
