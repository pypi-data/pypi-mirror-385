"""Test script for the new fastapps dev command with ngrok integration."""

import sys
from pathlib import Path


def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")

    try:
        from fastapps.cli.commands.dev import (
            get_config_dir,
            get_config_file,
            load_config,
            save_config,
            get_ngrok_token,
            set_ngrok_auth,
            start_dev_server,
            reset_ngrok_token,
        )

        print("✓ All dev.py functions imported successfully")
    except ImportError as e:
        print(f"✗ Import error in dev.py: {e}")
        return False

    try:
        from fastapps.cli.main import cli

        print("✓ CLI imported successfully")
    except ImportError as e:
        print(f"✗ Import error in main.py: {e}")
        return False

    return True


def test_config_management():
    """Test configuration file management."""
    print("\nTesting config management...")

    from fastapps.cli.commands.dev import (
        get_config_dir,
        get_config_file,
        save_config,
        load_config,
    )

    # Test config directory creation
    config_dir = get_config_dir()
    if config_dir.exists():
        print(f"✓ Config directory: {config_dir}")
    else:
        print(f"✗ Config directory not created: {config_dir}")
        return False

    # Test config file path
    config_file = get_config_file()
    print(f"✓ Config file path: {config_file}")

    # Test save and load
    test_config = {"test_key": "test_value", "ngrok_token": "test_token_123"}
    if save_config(test_config):
        print("✓ Config saved successfully")
    else:
        print("✗ Failed to save config")
        return False

    loaded_config = load_config()
    if loaded_config.get("test_key") == "test_value":
        print("✓ Config loaded successfully")
    else:
        print("✗ Failed to load config correctly")
        return False

    # Clean up test config
    config_file.unlink(missing_ok=True)
    print("✓ Test config cleaned up")

    return True


def test_cli_structure():
    """Test CLI command structure."""
    print("\nTesting CLI structure...")

    try:
        from fastapps.cli.main import cli
        from click.testing import CliRunner

        runner = CliRunner()

        # Test --help
        result = runner.invoke(cli, ["--help"])
        if result.exit_code == 0:
            print("✓ CLI --help works")

            # Check if dev command is listed
            if "dev" in result.output:
                print("✓ 'dev' command is registered")
            else:
                print("✗ 'dev' command not found in help")
                return False

            # Check if reset-token command is listed
            if "reset-token" in result.output or "reset_token" in result.output:
                print("✓ 'reset-token' command is registered")
            else:
                print("✗ 'reset-token' command not found in help")
                return False
        else:
            print(f"✗ CLI --help failed with exit code: {result.exit_code}")
            return False

        # Test dev --help
        result = runner.invoke(cli, ["dev", "--help"])
        if result.exit_code == 0:
            print("✓ 'fastapps dev --help' works")

            # Check for key features in help text
            if "ngrok" in result.output.lower():
                print("✓ ngrok mentioned in dev command help")
            if "--port" in result.output:
                print("✓ --port option available")
            if "--host" in result.output:
                print("✓ --host option available")
        else:
            print(f"✗ 'fastapps dev --help' failed")
            return False

        return True

    except Exception as e:
        print(f"✗ CLI structure test failed: {e}")
        return False


def test_syntax():
    """Test Python syntax of new files."""
    print("\nTesting Python syntax...")

    import py_compile

    files_to_check = ["fastapps/cli/commands/dev.py", "fastapps/cli/main.py"]

    all_valid = True
    for file_path in files_to_check:
        try:
            py_compile.compile(file_path, doraise=True)
            print(f"✓ {file_path}: syntax valid")
        except py_compile.PyCompileError as e:
            print(f"✗ {file_path}: syntax error - {e}")
            all_valid = False

    return all_valid


def main():
    """Run all tests."""
    print("=" * 60)
    print("FastApps Dev Command Test Suite")
    print("=" * 60)

    tests = [
        ("Syntax Check", test_syntax),
        ("Import Check", test_imports),
        ("Config Management", test_config_management),
        ("CLI Structure", test_cli_structure),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ {test_name} crashed: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! The dev command is ready to use.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
