"""
Error Handling with Python API

This example shows how to handle errors when using the dev server API.
"""

from fastapps import (
    DevServerError,
    NgrokError,
    ProjectNotFoundError,
    start_dev_server,
)

if __name__ == "__main__":
    try:
        print("Starting dev server with error handling...")

        start_dev_server(port=8001, host="0.0.0.0")

    except ProjectNotFoundError as e:
        print(f"\n❌ Project Error: {e}")
        print("\n💡 Solution:")
        print("   1. Make sure you're in a FastApps project directory")
        print("   2. Check that server/main.py exists")
        print("   3. Run 'fastapps init myproject' to create a new project")

    except NgrokError as e:
        print(f"\n❌ ngrok Error: {e}")
        print("\n💡 Solution:")
        print("   1. Check your ngrok token is valid")
        print("   2. Verify internet connection")
        print("   3. Try running 'fastapps reset-token' and re-enter token")

    except DevServerError as e:
        print(f"\n❌ Server Error: {e}")
        print("\n💡 Check:")
        print("   1. All dependencies are installed (pip install -r requirements.txt)")
        print("   2. Port is not already in use")
        print("   3. Project structure is correct")

    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")

    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        print("\n💡 Try:")
        print("   1. Check error message above")
        print("   2. Verify FastApps installation: pip install --upgrade fastapps")
        print("   3. Report issue if problem persists")
