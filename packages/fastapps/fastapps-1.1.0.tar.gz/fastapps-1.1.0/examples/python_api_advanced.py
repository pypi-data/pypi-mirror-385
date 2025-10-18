"""
Advanced Python API Usage for FastApps Dev Server

This example shows how to configure the dev server with custom settings.
"""

from fastapps import start_dev_server

if __name__ == "__main__":
    # Option 1: Using keyword arguments
    print("Starting with custom port...")

    start_dev_server(
        port=8080,
        host="127.0.0.1",
        log_level="debug",
        auto_reload=True,  # Enable hot reload
    )

    # Option 2: Using config object (alternative, not run in this example)
    # config = DevServerConfig(
    #     port=8080,
    #     host="0.0.0.0",
    #     ngrok_token="your_token_here",  # Optional
    #     auto_reload=True,
    #     log_level="debug"
    # )
    # start_dev_server_with_config(config)
