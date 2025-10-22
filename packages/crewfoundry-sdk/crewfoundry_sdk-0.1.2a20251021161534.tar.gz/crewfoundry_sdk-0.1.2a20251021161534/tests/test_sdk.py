"""
Tests for the main SDK class
"""

import pytest
from boiler_sdk import BoilerSDK, BoilerSDKConfig


def test_sdk_initialization():
    """Test SDK can be initialized with config"""
    config = BoilerSDKConfig(endpoint="https://api.test.com/graphql")
    sdk = BoilerSDK(config)

    assert sdk.client is not None
    assert sdk.auth is not None
    assert sdk.users is not None
    assert sdk.workspaces is not None


def test_sdk_token_management():
    """Test token management methods"""
    config = BoilerSDKConfig(endpoint="https://api.test.com/graphql")
    sdk = BoilerSDK(config)

    # Initially no tokens
    assert sdk.get_tokens() is None

    # Set tokens
    sdk.set_tokens("access123", "refresh456")
    tokens = sdk.get_tokens()
    assert tokens["access_token"] == "access123"
    assert tokens["refresh_token"] == "refresh456"

    # Clear tokens
    sdk.clear_tokens()
    assert sdk.get_tokens() is None


def test_sdk_endpoint_management():
    """Test endpoint management methods"""
    config = BoilerSDKConfig(endpoint="https://api.test.com/graphql")
    sdk = BoilerSDK(config)

    assert sdk.get_endpoint() == "https://api.test.com/graphql"

    sdk.set_endpoint("https://api.staging.com/graphql")
    assert sdk.get_endpoint() == "https://api.staging.com/graphql"


def test_sdk_config_with_tokens():
    """Test SDK initialization with tokens in config"""
    config = BoilerSDKConfig(
        endpoint="https://api.test.com/graphql",
        access_token="initial_access",
        refresh_token="initial_refresh",
    )
    sdk = BoilerSDK(config)

    tokens = sdk.get_tokens()
    assert tokens["access_token"] == "initial_access"
    assert tokens["refresh_token"] == "initial_refresh"
