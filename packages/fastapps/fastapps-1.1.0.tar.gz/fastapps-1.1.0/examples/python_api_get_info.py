"""
Get Server Info Without Starting Server

This example shows how to get server URLs without actually starting the server.
Useful for testing, automation, or displaying URLs before starting.
"""

import time

from fastapps import get_server_info

if __name__ == "__main__":
    try:
        # Get server info (creates ngrok tunnel but doesn't start server)
        print("Creating ngrok tunnel...")

        info = get_server_info(port=8001)

        print("\n" + "=" * 50)
        print("Server Information")
        print("=" * 50)
        print(f"Local URL:     {info.local_url}")
        print(f"Public URL:    {info.public_url}")
        print(f"MCP Endpoint:  {info.mcp_endpoint}")
        print(f"Port:          {info.port}")
        print(f"Host:          {info.host}")
        print("=" * 50)

        # You can also convert to dict
        print("\nAs dictionary:")
        print(info.to_dict())

        print("\n✅ Tunnel created! You can now start your server manually.")
        print(f"   Use this public URL: {info.public_url}")

        # Keep tunnel alive
        print("\nPress Ctrl+C to close tunnel...")

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n👋 Tunnel closed")
    except Exception as e:
        print(f"\n❌ Error: {e}")
