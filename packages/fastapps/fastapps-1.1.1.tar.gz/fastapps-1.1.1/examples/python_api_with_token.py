"""
Python API with Explicit ngrok Token

This example shows how to provide ngrok token programmatically.
Useful for CI/CD or when you don't want to save token to config file.
"""

import os
from fastapps import start_dev_server

if __name__ == "__main__":
    # Get token from environment variable
    ngrok_token = os.getenv("NGROK_TOKEN")

    if not ngrok_token:
        print("Error: NGROK_TOKEN environment variable not set")
        print("Usage: NGROK_TOKEN=your_token python python_api_with_token.py")
        exit(1)

    print("Starting server with provided ngrok token...")

    start_dev_server(port=8001, ngrok_token=ngrok_token)
