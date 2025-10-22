"""Test portable config file discovery."""

import os
import tempfile
from pathlib import Path

from krl_data_connectors.utils.config import find_config_file, load_api_key_from_config


def test_find_config_file():
    """Test that find_config_file searches in correct priority order."""

    # Test 1: Environment variable takes priority
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "apikeys"
        config_path.write_text("TEST_API_KEY: test123")

        os.environ["KRL_CONFIG_PATH"] = str(config_path)
        try:
            found = find_config_file("apikeys")
            assert found == str(config_path.resolve())
            print("✅ Test 1 passed: Environment variable priority works")
        finally:
            del os.environ["KRL_CONFIG_PATH"]

    # Test 2: Home directory config
    krl_dir = Path.home() / ".krl"
    krl_dir.mkdir(exist_ok=True)
    test_config = krl_dir / "test_apikeys"
    test_config.write_text("BEA API KEY: test_key_123")

    try:
        found = find_config_file("test_apikeys")
        assert found == str(test_config.resolve())
        print("✅ Test 2 passed: Home directory config found")
    finally:
        test_config.unlink()

    # Test 3: Non-existent file
    found = find_config_file("nonexistent_file_xyz")
    assert found is None
    print("✅ Test 3 passed: Returns None for non-existent files")

    print("\n🎉 All tests passed!")


def test_load_api_key_from_config():
    """Test loading API keys from config file."""

    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "apikeys"
        config_path.write_text(
            """
BEA API KEY: bea_test_key_123
FRED API KEY: fred_test_key_456
BLS API KEY: bls_test_key_789
        """.strip()
        )

        os.environ["KRL_CONFIG_PATH"] = str(config_path)
        try:
            # Test loading different keys
            bea_key = load_api_key_from_config("BEA")
            assert bea_key == "bea_test_key_123"
            print("✅ BEA key loaded correctly")

            fred_key = load_api_key_from_config("FRED")
            assert fred_key == "fred_test_key_456"
            print("✅ FRED key loaded correctly")

            bls_key = load_api_key_from_config("BLS")
            assert bls_key == "bls_test_key_789"
            print("✅ BLS key loaded correctly")

            # Test non-existent key
            missing = load_api_key_from_config("NONEXISTENT")
            assert missing is None
            print("✅ Non-existent key returns None")

        finally:
            del os.environ["KRL_CONFIG_PATH"]

    print("\n🎉 API key loading tests passed!")


if __name__ == "__main__":
    print("Testing portable config file discovery...\n")
    print("=" * 60)
    test_find_config_file()
    print("\n" + "=" * 60)
    test_load_api_key_from_config()
    print("=" * 60)
    print("\n✅ All portability tests passed!")
    print("   Notebooks are ready for public distribution.")
