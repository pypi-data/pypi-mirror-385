"""
Pytest configuration and fixtures
"""

import pytest
import warnings
from unittest.mock import AsyncMock
from ggnomad_sdk import GGNomadSDK, GGNomadSDKConfig


# Suppress specific async mock warnings
warnings.filterwarnings(
    "ignore", message="coroutine 'AsyncMockMixin._execute_mock_call' was never awaited"
)
warnings.filterwarnings("ignore", category=RuntimeWarning, module=".*")


@pytest.fixture
def sdk_config():
    """Basic SDK configuration for testing"""
    return GGNomadSDKConfig(endpoint="https://api.test.com/graphql", api_key="test-api-key")


@pytest.fixture
def sdk(sdk_config):
    """SDK instance for testing"""
    return GGNomadSDK(sdk_config)


@pytest.fixture
async def async_sdk(sdk_config):
    """Async SDK instance with proper cleanup"""
    sdk = GGNomadSDK(sdk_config)
    yield sdk
    await sdk.client.close()
